# Nimbus — Piano di implementazione MVP

Versione: 0.1 · Stato: Fase 6 · Data: 2026-08-29.

## Esito e perimetro

Questo piano trasforma la [specifica di fattibilità](07-technical-feasibility-specification.md) in incrementi consegnabili. Il primo esito utile non è una previsione web, ma un benchmark riproducibile che risponda: *il post-processing migliora GFS per il campione scelto, senza leakage?*

Il perimetro iniziale è quindi deliberatamente ristretto:

- Italia con GFS 0,25°, osservazioni NOAA ISD/GHCNh e DEM;
- previsione point-based per stazioni, lead 1–72 h;
- T2m come primo target obbligatorio; precipitazione solo dopo la validazione del suo target temporale;
- un solo repository pubblico `nimbus`, nessun raw data o segreto in Git;
- esecuzione locale/CI GitHub-hosted per i controlli rapidi; nessun workload o runner è attivato sul cluster in questa fase.

Il piano non autorizza un backfill massivo, una pubblicazione di forecast, l'uso di fonti con licenza `PENDING`, né la creazione di repository aggiuntivi.

## Ordine delle decisioni

| Gate | Decisione richiesta | Evidenza minima | Esito se negativo |
| --- | --- | --- | --- |
| D0 | Stack locale e object storage della prova | Budget, provider e modalità di backup approvati | Limitare il pilota a filesystem locale e fixture; non avviare ingestion reale continuativa |
| D1 | Campione ISD/GHCNh idoneo | Coverage/QA per stazione-variabile-anno e coordinate coerenti | Ridurre area/stazioni o integrare una fonte regionale solo dopo audit legale |
| D2 | Schema di forecast GFS correttamente normalizzato | Fixture, unit test e confronto manuale di un piccolo campione | Correggere adapter/contratto; nessun feature snapshot |
| D3 | Dataset joined temporalmente valido | Audit di `run_time`, `publication_time`, `valid interval` e target | Correggere join; nessun baseline report |
| D4 | Baseline riproducibili | Report GFS raw, climatologia, persistenza e bias correction | Investigare dati/metrica; non addestrare ML |
| D5 | ML utile e generalizzabile | Gate del [benchmark](04-mvp-benchmark-validation-plan.md) sul test congelato | Conservare la baseline; non pubblicare modello ML |
| D6 | Serving beta sicuro e spiegabile | Provenance, stati `complete/partial/stale`, rate limit e test API | Restare su report offline |

## Backlog per milestone

Le stime sono in giorni-persona per una singola persona esperta e indicano lavoro attivo, non attese di provider, approvazioni o download. I gate `D*` devono essere superati prima di iniziare il relativo blocco.

### M0 — Fondazioni e contratti dati (6–10 giorni)

| ID | Attività | Dipende da | Criterio di accettazione | Stima |
| --- | --- | --- | --- | --- |
| M0.1 | Definire struttura Python, gestione dipendenze, configurazione non segreta e convenzioni UTC/unità | D0 | Installazione riproducibile; nessun segreto/versione locale nel repository | 1–2 g |
| M0.2 | Versionare gli schemi di `forecast_run`, `raw_object`, `station`, `observation`, `feature_snapshot` e manifest | M0.1 | Fixture sintetiche valide/invalid e test di schema; chiavi e invarianti di Fase 4 rispettati | 2 g |
| M0.3 | Implementare catalogo locale e migrazioni iniziali PostgreSQL/PostGIS | M0.2 | Inserimento idempotente e transizioni di stato valide; test su DB effimero | 1–2 g |
| M0.4 | Definire layout object storage, checksum, lifecycle e policy di retention | M0.2, D0 | Un manifest riferisce oggetti immutabili; raw/normalized/features non si sovrappongono | 1–2 g |
| M0.5 | CI base: formato, lint, test, link e secret scan su fixture | M0.1 | Pull request/branch protetti da controlli rapidi GitHub-hosted | 1–2 g |

**Deliverable:** package scheletro, schema/migrazioni, fixture sintetiche, CI e ADR iniziali.  
**Exit gate M0:** una run fittizia può essere registrata, verificata e ripetuta senza duplicati.

### M1 — Censimento osservazioni e acquisition pilota (8–14 giorni)

| ID | Attività | Dipende da | Criterio di accettazione | Stima |
| --- | --- | --- | --- | --- |
| M1.1 | Congelare il campione iniziale di stazioni e la finestra pilota | D1 | Registro pubblico di ID, coordinate, quota, fonte, variabili e ragione di inclusione/esclusione; nessun raw | 1–2 g |
| M1.2 | Adapter ISD/GHCNh con download idempotente e manifest | M0 | Un campione di un anno è ripetibile, checksum verificati, errori classificati | 2–3 g |
| M1.3 | QA e normalizzazione osservazioni | M1.2 | UTC, unità, `qa_level`, revisioni e intervalli sono espliciti; report di missingness | 2–3 g |
| M1.4 | Audit tecnico e legale ARPA Piemonte, separato dal core | M1.1 | Decisione `APPROVED`/`PENDING` documentata; nessun ingest se non approvato | 1–2 g |
| M1.5 | Report coverage per anno, variabile, stagione e quota | M1.3 | Determina in modo riproducibile il campione effettivo disponibile per il benchmark | 2–3 g |

**Deliverable:** observation census versionato, adapter NOAA, dataset osservativo pilota e report QA.  
**Exit gate M1:** il campione conserva copertura sufficiente per train/validation/test; altrimenti si ridimensiona esplicitamente l'MVP.

### M2 — Ingestion e normalizzazione GFS (8–12 giorni)

| ID | Attività | Dipende da | Criterio di accettazione | Stima |
| --- | --- | --- | --- | --- |
| M2.1 | Adapter GFS storico per bbox Italia+buffer, run e lead configurabili | M0 | Manifest completo, download selettivo, retry e idempotenza | 2–3 g |
| M2.2 | Parser GRIB e normalizzatore delle variabili MVP | M2.1 | Unità, livelli, accumuli e tempi validi verificati contro campione manuale | 2–3 g |
| M2.3 | Interpolazione griglia-stazione e feature statiche DEM | M1.1, M2.2 | Metodo/versione di interpolazione e differenza quota modello-stazione registrati | 2–3 g |
| M2.4 | Check di completezza per run e quarantena di input anomali | M2.1 | Run `PARTIAL` non diventa eleggibile; alert/report locale disponibile | 1–2 g |
| M2.5 | Backfill controllato di un anno e misura reale di tempo/spazio | M2.2–M2.4 | Consuntivo byte, durata, errori e costo; decisione sul backfill pluriennale | 1–2 g |

**Deliverable:** point-forecast Parquet per campione/anno, catalogo GFS e report di fattibilità misurato.  
**Exit gate M2:** tutti i record includono `source_run_time_utc`, `source_publication_time_utc`, lead e valid interval; i valori possono essere ricondotti al raw manifest.

### M3 — Join storico e baseline scientifiche (10–16 giorni)

| ID | Attività | Dipende da | Criterio di accettazione | Stima |
| --- | --- | --- | --- | --- |
| M3.1 | Costruire feature snapshot point-forecast/osservazione per split temporale | M1, M2, D3 | Join con intervalli esatti e audit automatico anti-leakage | 2–3 g |
| M3.2 | Implementare climatologia, persistenza e GFS raw come baseline | M3.1 | Stesso campione, stessi filtri e stesso metodo di interpolazione tra baseline | 2–3 g |
| M3.3 | Implementare bias correction train-only | M3.1 | Parametri fit solo sul train e applicati a validation/test senza refit | 2–3 g |
| M3.4 | Motore metriche, segmentazione e intervalli bootstrap station-day | M3.2–M3.3 | MAE/RMSE/bias per i segmenti obbligatori; report machine-readable e leggibile | 2–3 g |
| M3.5 | Congelare dataset/test e pubblicare baseline report | M3.4 | Checksum, codice, config, finestre e risultati riferibili a un experiment ID | 2–4 g |

**Deliverable:** primo benchmark riproducibile, con report go/no-go sul valore del post-processing.  
**Exit gate M3:** la qualità del dataset e le baseline sono note; soltanto allora è autorizzata la sperimentazione ML.

### M4 — Primo modello ML e registry (8–14 giorni)

| ID | Attività | Dipende da | Criterio di accettazione | Stima |
| --- | --- | --- | --- | --- |
| M4.1 | Definire feature contract e esperimento tabellare per T2m | M3 | Feature disponibili al cutoff e importanza/assenze tracciabili | 1–2 g |
| M4.2 | Addestrare candidati semplici regolarizzati/gradient boosting | M4.1 | Ricerca iperparametri soltanto su train/validation | 2–3 g |
| M4.3 | Model registry minimo e artefatti immutabili | M4.2 | Modello, feature schema, snapshot e metriche sono ricostruibili | 1–2 g |
| M4.4 | Backtest test congelato, segmenti ed explainability diagnostica | M4.2–M4.3 | Gate D5 documentato, bootstrap e regressioni espliciti | 2–4 g |
| M4.5 | Decisione di prodotto | M4.4 | `PROMOTE` solo se i criteri scientifici sono soddisfatti; altrimenti baseline promossa | 1–3 g |

**Deliverable:** modello candidato o decisione documentata di mantenere bias correction.  
**Exit gate M4:** un modello pubblicabile è selezionato senza usare il test congelato per tuning.

### M5 — Serving beta, solo dopo D5 (8–14 giorni)

| ID | Attività | Dipende da | Criterio di accettazione | Stima |
| --- | --- | --- | --- |
| M5.1 | Materializzare forecast e stato run nel database di serving | M4 | Pubblicazione atomica, provenance completa e rollback di modello | 2–3 g |
| M5.2 | API `/v1` minima e test di contratto | M5.1 | Oraria, giornaliera, provenance e status rispettano gli stati/HTTP definiti | 2–3 g |
| M5.3 | UI essenziale o report web statico | M5.2 | Distingue osservazione, modello sorgente e Nimbus; nessuna allerta ufficiale | 2–3 g |
| M5.4 | Monitoring, backup, rate limit e runbook | M5.1–M5.3 | Degrado dichiarato, backup testato, alert per run assente/parziale | 2–3 g |
| M5.5 | Beta limitata e revisione qualità | M5.4 | Metriche pubblicate con coverage/limiti; nessuna promessa oltre il perimetro validato | 1–2 g |

**Deliverable:** beta controllata, non una piattaforma general-purpose.  
**Exit gate M5:** disponibilità, provenance e limiti scientifici sono comprensibili a un utente esterno.

## Sequenza, durata e percorso critico

Per una persona, M0–M3 richiedono circa **32–52 giorni-persona**; M4 aggiunge **8–14** e M5 **8–14**. Una stima di calendario responsabile va fissata solo dopo M1 e M2, perché coverage osservativa e costi/tempi effettivi di ingestion sono le principali incertezze.

```text
M0 contratti ──> M1 osservazioni ──> M3 join/baseline ──> M4 ML ──> M5 beta
       └──────> M2 GFS ────────────┘
```

M1 e M2 possono procedere in parallelo dopo M0. Le attività su ARPA Piemonte restano un ramo opzionale: non bloccano il core NOAA/GFS e non devono diventare una dipendenza implicita.

## Primo sprint consigliato

Durata indicativa: 5 giorni-persona. Scopo: rendere il lavoro successivo sicuro e testabile, non scaricare dati in volume.

1. Creare lo scheletro applicativo e le convenzioni di configurazione senza segreti.
2. Aggiungere gli schemi canonici e fixture sintetiche di un run forecast e di un'osservazione.
3. Implementare il catalogo/migrazione iniziale e le transizioni di stato validate.
4. Configurare CI GitHub-hosted per lint, test, controlli di segreti e documentazione.
5. Redigere un ADR sul provider object storage e un protocollo di retention del pilota.

**Definition of Done dello sprint:** da fixture si può registrare una run, associare un oggetto raw e un'osservazione, rigettare uno schema o una transizione errata e ripetere l'operazione senza duplicati. Nessun accesso al cluster è necessario.

## Qualità, sicurezza e controlli trasversali

| Controllo | Quando | Evidenza |
| --- | --- | --- |
| Segreto/credential scan | Ogni CI | Build fallita e report senza valori sensibili |
| Licenza e attribuzione | Ogni nuova fonte e prima del serving | `licence_status`, fonte e decisione datati |
| Contract/schema test | Ogni modifica adapter/schema | Fixture valide e casi negativi |
| Idempotenza | Ogni ingestion | Seconda esecuzione non duplica raw/catalogo/features |
| Anti-leakage audit | Ogni feature snapshot ed esperimento | Cutoff, run/publication/valid time nei manifest |
| Reproducibility check | Ogni benchmark candidato | Config, commit, checksum e metriche riferiti allo stesso experiment ID |
| Capacity/cost check | Prima di ogni backfill esteso | Byte, durata e costo misurati sul pilota |

## Regole per repository, CI e cluster

- Il repository `nimbus` rimane il solo repository sino a quando un trigger di separazione della Fase 5 si manifesta davvero.
- I dati raw, dataset derivati non ridistribuibili, kubeconfig, manifest operativi, nomi di risorse e credenziali non entrano nel repository pubblico.
- La CI iniziale usa runner GitHub-hosted e fixture sintetiche; test pesanti, backfill e training non sono job di pull request.
- L'eventuale CI privata nel cluster richiede una decisione separata: repository `nimbus-ops` privato, budget di risorse, modello di identità/segreti, limiti, isolamento e runbook approvati. Fino ad allora non è un prerequisito né un'azione pianificata.

## Decision log

| Data | Decisione | Alternative | Motivazione | Conseguenza |
| --- | --- | --- | --- | --- |
| 2026-08-29 | Implementare prima M0–M3 | API/UI o ML immediati | La qualità del join e delle baseline è la prova di fattibilità | Nessuna previsione pubblica prima del benchmark |
| 2026-08-29 | T2m è il primo target ML | Partire dalla precipitazione | Target e metriche della pioggia sono più sensibili a intervallo, qualità e rarità | Pioggia entra dopo audit dedicato |
| 2026-08-29 | Un repository fino al prototipo dati | Separazione immediata web/platform/ops | Riduce overhead e non crea CI/integrazioni premature | I trigger di separazione restano espliciti |
| 2026-08-29 | CI hosted iniziale; cluster fuori dal percorso critico | Runner privati subito | Risorse e configurazione privata non sono necessarie per validare M0–M3 | Eventuale integrazione cluster resta una decisione futura |

## Rischi e segnali di stop

| Segnale | Azione obbligatoria |
| --- | --- |
| Stazioni insufficienti per un anno/split/segmento | Ridurre claim geografico o fermare il modello per quel segmento |
| Download GFS/normalizzazione non riproducibili | Bloccare il backfill e correggere manifest/adapter |
| Join richiede osservazioni successive al cutoff | Correggere il contratto; invalidare i risultati prodotti |
| Bias correction non supera GFS in modo coerente | Pubblicare il risultato negativo; non scalare il modello |
| ML migliora solo aggregate metric ma peggiora segmenti critici | Non promuovere senza una policy esplicita per i trade-off |
| Costo pilota oltre budget approvato | Applicare retention/subset e rivalutare il perimetro prima di estendere |

## Prossima azione eseguibile

All'avvio dell'implementazione, eseguire **M0.1–M0.2** e approvare D0: scelta di storage della prova, budget mensile massimo e periodo pilota. Solo dopo questi tre elementi va creato il primo codice della pipeline.
