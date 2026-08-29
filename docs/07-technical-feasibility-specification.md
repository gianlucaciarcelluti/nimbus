# Nimbus — Technical Feasibility Specification

Versione: 0.1 · Stato: Fase 5 · Data: 2026-08-29.

## 1. Executive summary

Nimbus è fattibile come piattaforma di post-processing locale di previsioni, non come sostituto di un centro NWP globale. Il primo prodotto deve dimostrare miglioramento riproducibile contro GFS e bias correction semplice su stazioni selezionate, prima di aggiungere modelli, radar, deep learning o una promessa di risoluzione chilometrica.

La configurazione raccomandata per l'MVP è: GFS storico + osservazioni NOAA ISD/GHCNh + DEM, pipeline batch modulare, PostgreSQL/PostGIS, object storage e Parquet. Piemonte è il primo candidato per una verifica locale con osservazioni regionali open; nessun dato ARPA/radar entra senza una licenza e un audit specifico.

## 2. Visione, obiettivi e non-obiettivi

| Categoria | Definizione |
| --- | --- |
| Visione | Rendere esplicite previsione, incertezza, provenienza e performance locale per una località italiana. |
| Obiettivo MVP | Misurare se il post-processing migliora forecast GFS 1–72 h per T2m e, separatamente, per precipitazione. |
| Obiettivo successivo | Ensemble IFS/AIFS/ICON solo quando esistono archivi/licenze e raccolta prospettica affidabili. |
| Non-obiettivo | Eseguire un modello meteorologico globale, produrre allerte ufficiali, o dichiarare skill su microclimi non testati. |
| Non-obiettivo MVP | Nowcasting radar, downscaling 1 km, forecast generativi, app mobile e pubblicazione di raw data di terzi. |

## 3. Utenti e casi d’uso

| Utente | Caso d’uso | Vincolo |
| --- | --- | --- |
| Ricercatore / maintainer | Riprodurre benchmark, confrontare modelli, tracciare lineage | Accesso a dataset snapshot e report, non a credenziali |
| Utente web | Consultare forecast oraria/giornaliera per coordinate | Deve distinguere forecast Nimbus, source model e osservazione |
| API consumer futuro | Integrare forecast puntuale | Rate limit, versione, provenance e non uso safety-critical senza accordo |
| Operatore | Gestire run mancanti e dataset degradati | Nessun override silenzioso della qualità |

## 4. Requisiti funzionali

1. Ingerire run forecast e osservazioni con timestamp, checksum, licenza e stato.
2. Generare feature esclusivamente disponibili entro il `publication_time_utc` della previsione.
3. Produrre forecast point-based a partire da `lat`, `lon`, `elevation_m` e dalla versione modello selezionata.
4. Esporre valori orari, aggregati giornalieri, stato di completezza, intervalli/quantili e provenance.
5. Consentire backtest riproducibile per stazione, area, stagione, lead e soglia evento.
6. Bloccare la pubblicazione quando una dipendenza è parziale, non verificata legalmente o non supera i validation gate.

## 5. Requisiti non funzionali

| Area | Requisito iniziale | Criterio di verifica |
| --- | --- | --- |
| Correttezza temporale | Nessun leakage | Audit di feature e split; tutti i record hanno run/publication/valid time |
| Riproducibilità | Ogni report è ricostruibile | Dataset snapshot, codice/versione, checksum e config registrati |
| Disponibilità | Degrado esplicito, non dato inventato | API restituisce stato `partial`/`stale` e ultimo issue time |
| Sicurezza | Nessun secret nel repository o output log | Secret scan e review CI |
| Legalità | Pubblicare solo derivati autorizzati | Policy engine basata su `licence_status` |
| Performance API | Lettura forecast già calcolato | Nessun GRIB parsing in request path |
| Osservabilità | Run, download, QA e publish sono auditabili | Metriche e log strutturati con correlation ID |

## 6. Architettura e contratti dati

L’architettura di riferimento è definita nel [documento Fase 4](06-reference-architecture.md). Il contratto canonico usa UTC e intervalli half-open `[start, end)`.

### 6.1 Contratto forecast point-based

| Campo | Regola |
| --- | --- |
| `issue_time_utc` | Quando Nimbus ha emesso il forecast derivato |
| `source_run_time_utc` | Inizializzazione del forecast NWP sorgente |
| `source_publication_time_utc` | Prima disponibilità registrata dal pipeline |
| `valid_start_utc`, `valid_end_utc` | Punto o accumulo previsto |
| `location` | Lat, lon, quota richiesta e metodo di elevazione usato |
| `value`, `unit` | Valore e unità canonica |
| `uncertainty` | Intervallo/quantili soltanto se calibrati e versionati |
| `model_version` | Versione immutabile del post-processor |
| `provenance` | Provider/modelli, feature contract, licenze e stato |

### 6.2 Contratto osservazione

Le osservazioni sono immutabili per versione: una correzione crea una nuova revisione, preservando valore originario, `qa_level`, intervallo misurato e `revision_time_utc`. Il target di precipitazione deve coincidere esattamente con l’intervallo dell’accumulo forecast.

## 7. API v1 proposta

| Metodo / endpoint | Scopo | Risposta essenziale |
| --- | --- | --- |
| `GET /v1/locations/resolve` | Validare coordinate e feature geografiche | località normalizzata, quota, cella/modello |
| `GET /v1/forecasts/hourly` | Forecast 1–72 h | serie con issue/valid time, valori, quantili, provenance |
| `GET /v1/forecasts/daily` | Min/max, accumuli e probabilità aggregate | intervallo locale/UTC, metodo aggregazione |
| `GET /v1/forecasts/{id}/provenance` | Audit di un forecast | modello, source runs, qualità e attribuzioni |
| `GET /v1/status` | Stato dataset/model run | freshness, completezza e ultimo forecast completo |

Regole API: `/v1` è versionato; coordinate WGS84; UTC come default esplicito; cache soltanto su forecast immutabili; 400 per coordinate/parametri invalidi, 404 per località/forecast assente, 409 per run parziale, 429 per rate limit, 503 per sorgente degradata. Autenticazione non necessaria per una beta pubblica limitata; API key e quota sono requisiti prima di accesso programmatico generalizzato.

## 8. Strategia ML e gate scientifici

Ordine obbligatorio: climatologia → persistenza → GFS raw → bias correction semplice → modello tabellare. Il primo ML non è approvato se non supera le baseline sulle metriche, segmenti geografici e split temporali documentati nel [piano benchmark](04-mvp-benchmark-validation-plan.md).

Primo candidato: modello tabellare regolarizzato/gradient boosting per variabile, stazione o cluster orografico e lead; output probabilistico solo dopo calibrazione. Reti neurali, transformer e downscaling vengono valutati dopo avere dimostrato che il limite non è qualità/coverage delle osservazioni.

## 9. Osservabilità e operazioni

Metriche minime: run attesi/ricevuti/completi, età dell’ultimo forecast, byte scaricati, retry, mismatch checksum, record QA per livello, copertura stazioni, feature null, latenza normalizzazione, metriche backtest e drift per stagione/area.

Alert minimi: assenza di run oltre la finestra configurata, run parziale, variazione schema, tasso QA anomalo, storage lifecycle fallito, regressione statisticamente significativa del modello pubblicato.

Runbook operativo: il fallback di una fonte è sempre dichiarato in API e UI; non si sostituisce silenziosamente un modello con un altro e non si riaddestra automaticamente un modello in produzione.

## 10. Sicurezza, privacy e aspetti legali

- Segreti fuori dal repo e dal data lake; accesso least-privilege per raw, database, CI e pubblicazione.
- Nessun dato personale è previsto dal core MVP; i log API devono ridurre o anonimizzare IP e coordinate precise quando non indispensabili.
- Ogni dataset ha `licence_status`: `APPROVED`, `PENDING`, `END_USER_ONLY`, `NO_REDISTRIBUTION`, `REVOKED`.
- Il public serving accetta solo `APPROVED`; attribuzioni provider sono compilate da metadati, non inserite manualmente nelle pagine.
- Source code Apache-2.0 non modifica i diritti sui dati terzi.

## 11. Repositories e CI

### Decisione attuale

Mantenere **un solo repository pubblico `nimbus`** fino al primo prototipo dati. È il modo più semplice di far evolvere insieme contratti, pipeline, benchmark, API e documentazione.

### Trigger per separare repository

| Condizione | Repository separato proposto | Visibilità |
| --- | --- | --- |
| Frontend ha release, team o ritmo indipendente | `nimbus-web` | Pubblico |
| Pipeline/API richiedono deployment indipendente | `nimbus-platform` | Pubblico, senza dati/segreti |
| Manifest di deploy, runner CI, credenziali e runbook cluster | `nimbus-ops` | **Privato** |
| Dataset/raw o benchmark con licenze non ridistribuibili | Nessun repository Git; object storage con catalogo privato | Privato |

Non creare ora questi repository: separare prima della prima implementazione aumenterebbe coordinamento e CI senza un beneficio misurato.

### Strategia CI

1. **Ora:** GitHub Actions su runner GitHub-hosted per markdown, link, lint, test e controlli di secret; nessuna dipendenza da cluster o credenziali private.
2. **Quando la pipeline esiste:** test di contratto su fixture sintetiche, test unitari e integrazione con database/object storage effimeri.
3. **Quando il cluster viene esplicitamente predisposto:** runner autoscalabili in un perimetro privato, con limiti CPU/memoria, namespace dedicato, cache controllata, NetworkPolicy e GitHub App/secret manager. Nessun dettaglio di cluster, kubeconfig, namespace o credenziale va nel repository pubblico.
4. **Batch pesanti:** code separate e budget di risorse; benchmark/radar/training non condividono la coda con CI rapida.

L’abilitazione della CI sul cluster non rientra in questa fase: richiederà una verifica privata delle componenti runner e un design privato approvato. Nessun dettaglio operativo del cluster è incluso in questo repository pubblico.

## 12. Piano di rilascio

| Milestone | Deliverable | Criterio di uscita |
| --- | --- | --- |
| M0 — Data contract | Schema, manifest, fixture sintetiche | Review di anti-leakage e licenze |
| M1 — Ingestion | GFS + ISD/GHCNh su un anno | Checkpoint idempotenti e report completezza |
| M2 — Baseline | GFS raw, climatologia, bias correction | Report validation riproducibile |
| M3 — First ML | Modello tabellare e model registry | Gate go/no-go superato sul test congelato |
| M4 — Serving beta | API + UI minima, provenance visibile | Forecast completo/stale esposto correttamente |
| M5 — Multi-model | IFS/AIFS/ICON se contrattualmente disponibili | Beneficio dimostrato versus baseline |

## 13. Rischi residui

| Rischio | Mitigazione |
| --- | --- |
| Coverage osservativa insufficiente | Segmentare le promesse per area/altitudine; pilota regionale |
| Provider cambia schema o retention | Adapter versionati, manifest e contract test |
| Costi raw crescono | Lifecycle, subset geografici, feature snapshot |
| CI sul cluster sottrae capacità al forecast | Runner non attivati finché non esiste budget; priorità/batch separati |
| Modello ML appare migliore per leakage | Test congelato e audit temporalmente vincolato |
| Dati con licenza incompatibile | Status legale come gate tecnico alla pubblicazione |

## 14. Decisioni aperte prima dell’implementazione

1. Approvare il provider object storage e il budget mensile.
2. Eseguire audit di completezza per le 124 candidate ISD e prova tecnica ARPA Piemonte.
3. Definire API beta pubblica oppure accesso autenticato fin dall’inizio.
4. Scegliere se il primo modello copre solo T2m o include precipitazione, che ha requisiti di target più difficili.
5. Decidere, separatamente, se e quando predisporre CI privata sul cluster.
