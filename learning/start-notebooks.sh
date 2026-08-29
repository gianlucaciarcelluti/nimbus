#!/usr/bin/env bash
#
# Avvio del percorso didattico Nimbus.
#
# Crea il virtualenv se manca, installa le dipendenze di requirements.txt
# soltanto quando qualcosa non e' soddisfatto, poi lancia JupyterLab sui
# notebook. Rieseguirlo a venv sano non reinstalla nulla e non tocca la rete.
#
# Uso:
#   learning/start-notebooks.sh              # controlla e avvia JupyterLab
#   learning/start-notebooks.sh --check      # solo controllo, non avvia
#   learning/start-notebooks.sh --no-install # non installa, avvisa e si ferma
#   learning/start-notebooks.sh --recreate   # ricrea il venv da zero
#
# Gli argomenti non riconosciuti vengono passati a "jupyter lab".

set -euo pipefail

# Radice di learning/, indipendente dalla directory di invocazione.
LEARNING_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$LEARNING_DIR/.venv"
REQUIREMENTS="$LEARNING_DIR/requirements.txt"
NOTEBOOKS_DIR="$LEARNING_DIR/notebooks"

# Versione richiesta dal percorso didattico (vedere learning/README.md).
PY_MAJOR_MINOR="3.12"

CHECK_ONLY=0
ALLOW_INSTALL=1
RECREATE=0
JUPYTER_ARGS=()

info() { printf '\033[1;34m[nimbus]\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m[nimbus]\033[0m %s\n' "$1" >&2; }
die()  { printf '\033[1;31m[nimbus]\033[0m %s\n' "$1" >&2; exit 1; }

usage() {
    sed -n '3,15p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//; s/^#$//'
}

for arg in "$@"; do
    case "$arg" in
        --check)      CHECK_ONLY=1 ;;
        --no-install) ALLOW_INSTALL=0 ;;
        --recreate)   RECREATE=1 ;;
        -h|--help)    usage; exit 0 ;;
        *)            JUPYTER_ARGS+=("$arg") ;;
    esac
done

[[ -f "$REQUIREMENTS" ]] || die "requirements.txt non trovato in $LEARNING_DIR"

# Individua un interprete Python della versione richiesta, provando prima i
# nomi versionati e poi il python3 di sistema.
find_python() {
    local candidate resolved
    for candidate in "python$PY_MAJOR_MINOR" \
                     "/opt/homebrew/bin/python$PY_MAJOR_MINOR" \
                     "/usr/local/bin/python$PY_MAJOR_MINOR" \
                     python3; do
        resolved="$(command -v "$candidate" 2>/dev/null)" || continue
        if "$resolved" -c "import sys; raise SystemExit(0 if '.'.join(map(str, sys.version_info[:2])) == '$PY_MAJOR_MINOR' else 1)" 2>/dev/null; then
            printf '%s\n' "$resolved"
            return 0
        fi
    done
    return 1
}

# Elenca i requisiti non soddisfatti nel venv, uno per riga. Il controllo e'
# locale: legge i metadata dei pacchetti installati, senza contattare PyPI.
# Stampa la sola riga "*" se i pin non sono valutabili.
unsatisfied_requirements() {
    "$VENV_DIR/bin/python" - "$REQUIREMENTS" <<'PY'
import sys

from importlib.metadata import PackageNotFoundError, version

try:
    from packaging.requirements import Requirement
except ModuleNotFoundError:
    # Senza packaging non si possono valutare i pin: si forza l'installazione,
    # che a sua volta rimettera' a posto anche packaging.
    print("*")
    raise SystemExit(0)

with open(sys.argv[1], encoding="utf-8") as handle:
    for line in handle:
        line = line.split("#")[0].strip()
        if not line:
            continue
        try:
            requirement = Requirement(line)
        except Exception:
            print(f"{line} (requisito illeggibile)")
            continue
        try:
            installed = version(requirement.name)
        except PackageNotFoundError:
            print(f"{line} (assente)")
            continue
        if requirement.specifier and not requirement.specifier.contains(
            installed, prereleases=True
        ):
            print(f"{line} (installato: {installed})")
PY
}

if (( RECREATE )) && [[ -d "$VENV_DIR" ]]; then
    info "Rimozione del venv esistente ($VENV_DIR)"
    rm -rf "$VENV_DIR"
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    (( ALLOW_INSTALL )) || die "venv assente in $VENV_DIR e --no-install richiesto."
    PYTHON_BIN="$(find_python)" || die \
"Nessun Python $PY_MAJOR_MINOR trovato.
    macOS: brew install python@$PY_MAJOR_MINOR
    Linux: installare python$PY_MAJOR_MINOR dalla propria distribuzione."
    info "Creazione del venv con $PYTHON_BIN ($("$PYTHON_BIN" -V 2>&1))"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    "$VENV_DIR/bin/python" -m pip install --upgrade --quiet pip
fi

info "Controllo delle dipendenze di requirements.txt"
MISSING="$(unsatisfied_requirements)"

if [[ -n "$MISSING" ]]; then
    if [[ "$MISSING" == '*' ]]; then
        warn "Impossibile verificare i pin: reinstallo tutto requirements.txt"
    else
        warn "Requisiti non soddisfatti:"
        while IFS= read -r item; do
            if [[ -n "$item" ]]; then
                warn "  - $item"
            fi
        done <<< "$MISSING"
    fi

    (( ALLOW_INSTALL )) || die \
"Dipendenze mancanti e --no-install richiesto. Per installarle:
    $VENV_DIR/bin/pip install -r $REQUIREMENTS"

    info "Installazione in corso (serve rete, i wheel binari sono grandi)"
    # -q tiene l'output leggibile: restano visibili download, errori e il
    # riepilogo finale, spariscono le righe "already satisfied".
    "$VENV_DIR/bin/pip" install -q -r "$REQUIREMENTS"

    # Verifica che l'installazione abbia davvero risolto tutto: un pip che
    # esce 0 non garantisce che ogni pin sia ora soddisfatto.
    STILL_MISSING="$(unsatisfied_requirements)"
    [[ -z "$STILL_MISSING" ]] || die \
"Dopo l'installazione restano requisiti non soddisfatti:
$STILL_MISSING"
    info "Dipendenze installate."
else
    info "Tutte le dipendenze sono gia' presenti alle versioni richieste."
fi

if (( CHECK_ONLY )); then
    info "Controllo completato (--check): JupyterLab non avviato."
    exit 0
fi

[[ -d "$NOTEBOOKS_DIR" ]] || die "Cartella notebooks non trovata: $NOTEBOOKS_DIR"

info "Avvio di JupyterLab su $NOTEBOOKS_DIR (Ctrl-C due volte per uscire)"
# ${ARR[@]+"${ARR[@]}"} e' l'idioma compatibile con il bash 3.2 di macOS, dove
# con "set -u" l'espansione di un array vuoto conta come variabile non definita.
exec "$VENV_DIR/bin/jupyter" lab "$NOTEBOOKS_DIR" ${JUPYTER_ARGS[@]+"${JUPYTER_ARGS[@]}"}
