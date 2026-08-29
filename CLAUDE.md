# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Cos'è Nimbus

Piattaforma open-source di ricerca su previsioni meteo locali per l'Italia: **post-processing statistico/ML di forecast NWP**, non un centro NWP. Il repository è oggi **solo documentazione** (fase di discovery/fattibilità conclusa, Fasi 1–6). Non esiste ancora codice, build, test o CI: il primo codice va scritto seguendo il piano in `docs/08-mvp-implementation-plan.md` a partire da M0.1–M0.2, e solo dopo l'approvazione del gate D0 (storage, budget, periodo pilota).

La documentazione è in **italiano** e va mantenuta tale.

## Come è organizzata la documentazione

I file `docs/NN-*.md` sono sequenziali e ognuno è l'output di una fase decisionale; le decisioni successive sovrascrivono quelle precedenti solo se il documento più recente lo dice esplicitamente.

| Doc | Ruolo quando si lavora |
| --- | --- |
| `01-data-model-landscape.md` | Quali provider NWP/osservazioni esistono e quali sono esclusi dall'MVP |
| `02-historical-forecast-observation-protocol.md` | **Regole anti-leakage e campi temporali obbligatori** — vincolante per ogni feature |
| `03-italy-observation-source-census.md` | Stato legale/tecnico per fonte osservativa italiana; criteri di accettazione stazione |
| `04-mvp-benchmark-validation-plan.md` | Split temporali, baseline obbligatorie, metriche, criterio go/no-go ML |
| `05-mvp-data-feasibility.md` | Volumi misurati (GFS ~5,46 MB/run-lead, 124 stazioni ISD candidate), lifecycle/retention |
| `06-reference-architecture.md` | Componenti, contratto dati/lineage, stati pipeline, layout object storage |
| `07-technical-feasibility-specification.md` | Requisiti, contratti forecast/osservazione, API `/v1`, milestone M0–M5 |
| `08-mvp-implementation-plan.md` | **Backlog eseguibile**: gate D0–D6, task M0.x–M5.x con criteri di accettazione |
| `data-sources-register.md` | `licence_status` per provider; da aggiornare prima di ogni nuova fonte |

Il `README.md` indicizza tutti i documenti: aggiungendo un doc, aggiornare anche l'indice.

## Architettura target (decisa, non ancora implementata)

**Modular monolith batch**, non microservizi/Kubernetes/Kafka:

- **Source adapters** pianificati per provider (GFS via NOMADS, NOAA ISD/GHCNh, DEM) → download idempotente con manifest e checksum.
- **Object storage** per raw immutabile a retention breve (14 giorni post-normalizzazione); layout `raw/ · normalized/ · features/ · models/ · backtests/` mai sovrapposti.
- **PostgreSQL 16+ / PostGIS** per catalogo (run, file, stazioni, lineage, stato pipeline) e per i forecast pubblicati. Non ci si copia dentro i campi grigliati.
- **Parquet ZSTD partizionato** (`valid_date`, `run_cycle`, `model_id`) come feature store point-forecast. Zarr solo se e quando servono campi grigliati/radar — sono complementari, non alternative.
- **Training/backtest** come job batch separati; model registry = tabella PostgreSQL + artefatti immutabili su object storage.
- **REST API `/v1` stateless** che legge solo forecast già materializzati: nessun parsing GRIB nel request path.

Stati pipeline (idempotenti): `DISCOVERED → DOWNLOADING → VERIFIED → NORMALIZED → FEATURED → ELIGIBLE → PUBLISHED`, più `FAILED_RETRYABLE / FAILED_FINAL / QUARANTINED`. Chiave di idempotenza: `provider:model:version:run_time:variable:bbox:lead`. Un run `PARTIAL` non sostituisce mai l'ultimo forecast completo.

## Invarianti da non violare

Queste regole sono il motivo per cui il progetto esiste; una PR che le rompe è da rifiutare anche se i test passano.

1. **Anti-leakage.** Nessuna feature può usare informazione non disponibile entro `source_publication_time_utc`. ERA5 è ammesso *solo* per climatologie/anomalie calcolate sul passato dello split. Split train/validation/test sempre temporali, mai random. Il test è congelato: mai usato per tuning.
2. **Ricostruibilità.** Ogni `published_forecast` deve essere ricostruibile dal suo `model_version` + `feature_snapshot` + `forecast_run`. Se non lo è, non è pubblicabile.
3. **Immutabilità.** Nessuna tabella o oggetto viene sovrascritto in posto; ogni artefatto ha un `dataset_version_id`. Una correzione di osservazione crea una revisione con `revision_time_utc`, preservando valore e `qa_level` originari.
4. **Tempo.** Tutto UTC, intervalli half-open `[start, end)`. Per gli accumuli (precipitazione) l'intervallo osservato deve coincidere *esattamente* con quello previsto. Vale `valid_time_utc = run_time_utc + lead_hours`.
5. **Licenza come gate tecnico.** Il serving pubblico accetta solo fonti `APPROVED`; `PENDING`/`END_USER_ONLY`/`NO_REDISTRIBUTION`/`REVOKED` sono bloccate dal job di pubblicazione. Le attribuzioni si generano dai metadati del catalogo.
6. **Ordine scientifico obbligatorio.** climatologia → persistenza → GFS raw → bias correction semplice → ML tabellare. Nessun ML prima che le baseline siano riproducibili (gate D4); nessuna promozione ML senza superare il gate D5 sul test congelato, con bootstrap **per stazione-giorno**.
7. **Confronti equi.** Le baseline devono usare lo stesso campione, gli stessi filtri e la stessa interpolazione griglia-stazione del modello candidato.
8. **Degrado esplicito.** L'API dichiara `complete`/`partial`/`stale` e l'ultimo issue time; non si inventa un valore né si sostituisce silenziosamente un modello con un altro.

## Cosa non entra nel repository

- Dati grezzi o derivati non ridistribuibili: GRIB/NetCDF/Zarr, osservazioni, artefatti modello (già coperti da `.gitignore`).
- Segreti, credenziali, `.env`, chiavi.
- Dettagli operativi del cluster: kubeconfig, manifest di deploy, namespace, nomi di risorse, runbook infrastrutturali. Quando serviranno, andranno in un repo privato `nimbus-ops` — che **non va creato ora**.

Il repository resta **singolo** finché non si manifesta un trigger di separazione documentato in `docs/07-technical-feasibility-specification.md` §11.

## Perimetro MVP — cosa è fuori

Fuori perimetro finché i gate non dicono il contrario: nowcasting radar, downscaling 1 km, forecast generativi/deep learning, app mobile, ensemble IFS/AIFS/ICON, backfill massivo, pubblicazione di forecast, allerte ufficiali, GPU, ingest ARPA non approvato. Il primo target ML è **T2m**; la precipitazione entra solo dopo un audit dedicato del suo target temporale.

Primo backfill autorizzato: 12 mesi, **una run/die**, lead 1–48 h.

## Convenzioni operative

- **Commit**: prefissi convenzionali (`docs:`, `feat:`, `fix:`), messaggio in inglese, imperativo, una riga.
- **CI**: quando esisterà, runner GitHub-hosted con fixture sintetiche — lint, test, link check, secret scan. Backfill, benchmark e training non sono mai job di pull request.
- **Decision log**: le decisioni architetturali/di perimetro si registrano nella tabella "Decision log" in coda al documento di fase pertinente, con data, alternative escluse e motivazione. Non cambiare una decisione passata: aggiungerne una nuova.
- **Fonti**: ogni affermazione tecnica nei docs va collegata alla fonte ufficiale (WMO, ECMWF, NOAA, ARPA). Distinguere sempre **misura riproducibile** da **stima di pianificazione**, come già fatto in `05-mvp-data-feasibility.md`.
