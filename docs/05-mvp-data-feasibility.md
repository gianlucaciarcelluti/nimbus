# Misure di fattibilità del dataset MVP

Data della misura: 2026-08-29. Stato: Fase 3. Le cifre sotto separano misure riproducibili da stime di pianificazione.

## Esito

Il dataset MVP è fattibile su un singolo server o workstation, purché i GRIB grezzi vengano usati come staging a retention breve e non come archivio permanente. Non è fattibile trattare l'intera griglia GFS per più anni come input predefinito di un progetto individuale senza una politica di lifecycle.

## Misura 1 — copertura italiana ISD

È stato scaricato il solo inventario pubblico `isd-history.csv` NOAA il 2026-08-29 e analizzato localmente, senza scaricare osservazioni. Risultati:

| Indicatore | Valore misurato | Interpretazione |
| --- | ---: | --- |
| Record di stazione con `CTRY=IT` | 318 | Non equivale a 318 serie utilizzabili contemporaneamente |
| Stazioni geolocalizzate | 317 | Una riga ha coordinate nulle/non utili |
| Stazioni con `BEGIN ≤ 2021-01-01` e `END ≥ 2025-08-01` | 124 | Primo insieme candidato per il MVP storico |
| Candidate sotto 300 m | 89 | Forte prevalenza di pianura/coste/aeroporti |
| Candidate 300–999 m | 22 | Copertura intermedia limitata |
| Candidate ≥1.000 m | 13 | Insufficiente per dichiarazioni uniformi su valli e alta montagna |

L'inventario ricevuto termina per molte stazioni ad agosto 2025; non consente di dedurre l'operatività nel 2026. Inoltre registra il periodo della stazione, non la completezza di ciascuna variabile oraria. La prossima verifica deve scaricare un campione 2021–2025 delle 124 candidate e calcolare completezza, flag, duplicati e disponibilità reale di precipitazione.

Fonte: [NOAA ISD](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database), inventario pubblico `https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv`.

## Misura 2 — volume GFS Italia + buffer

È stato richiesto a NOMADS un unico subset GFS 0,25°, run `2026-08-28 00 UTC`, lead +72 h, bbox 4–22°E / 34–49°N. Il subset includeva T2m, Td2m, U/V 10 m, MSLP, precipitazione e copertura nuvolosa ai livelli appropriati.

| File campione | Dimensione misurata |
| --- | ---: |
| Lead +00 h | 4,57 MB |
| Lead +72 h | 5,46 MB |
| Valore prudenziale usato per il dimensionamento | 5,46 MB per run × lead |

La fonte è il [filtro GRIB GFS NOMADS](https://nomads.ncep.noaa.gov/), non una garanzia di dimensione futura: griglia, packing, variabili e ciclo modello possono cambiare.

### Proiezione raw — stima derivata

Assunzioni: 73 lead orari (0–72), stessa dimensione del campione, 365 giorni.

| Politica di acquisizione | Formula | Stima raw annua |
| --- | --- | ---: |
| Un solo run/die | 5,46 MB × 73 × 365 | 146 GB |
| Due run/die | 5,46 MB × 73 × 2 × 365 | 291 GB |
| Quattro run/die | 5,46 MB × 73 × 4 × 365 | 582 GB |

Queste sono stime lineari, non misure di un anno reale. Non includono livelli in quota, ensemble, altri modelli, radar o satelliti.

## Misura 3 — dimensione del dataset point-forecast

Con 124 stazioni candidate, 73 lead e quattro run/die, il dataset contiene circa **13.215.920 esempi stazione-run-lead/anno**; quattro anni generano circa **52,9 milioni** di esempi.

Il formato finale deve essere una tabella wide Parquet partizionata per `valid_date`, `run_cycle` e `model_id`, non una copia GRIB per stazione. Un envelope iniziale prudente è 2–10 GB/anno di Parquet compresso per le feature MVP e i target, da misurare dopo il primo mese: dipende da numero di feature, encoding, null, metadati e duplicazioni.

## Policy di lifecycle proposta

| Classe | Retention proposta | Motivo |
| --- | --- | --- |
| Raw GRIB subset | 14 giorni dopo normalizzazione verificata | Ripetibilità operativa e diagnosi di errori recenti |
| Raw necessario a esperimenti approvati | Snapshot/versione esplicita | Riproducibilità senza trattenere ogni run |
| Feature normalizzate Parquet | Permanente per train/validation/test | Asset scientifico principale |
| Osservazioni originali e QA | Permanente, soggetto a licenza | Evidenza del target e audit |
| Artefatti intermedi ricostruibili | 30 giorni | Ridurre costo e duplicazione |

## Compute e banda — valutazione

- Ingestione MVP: 1,6 GB/giorno nella configurazione massima GFS considerata (4 run, 0–72 h, subset misurato). CPU 2–4 core e 8–16 GB RAM sono un punto di partenza ragionevole per download, estrazione GRIB e Parquet; questa è una stima di pianificazione, non un benchmark.
- Backfill GFS 2021–2024, quattro run/die: circa 2,3 TB raw con le assunzioni sopra. Il throughput effettivo del server sorgente, retry e conversione sono più importanti della banda nominale; va eseguito con coda idempotente e checkpoint per giorno/run.
- Training tabellare MVP: i 52,9 milioni di esempi sono gestibili tramite campionamento, partizionamento e modelli a batch; non giustificano una GPU nella prima baseline statistica.

## Decisione di fattibilità

**GO condizionato.** Procedere al prototipo dati, ma con questi vincoli:

1. primo backfill limitato a 12 mesi, una run/die e lead 1–48 h;
2. misurare completezza delle osservazioni prima di scaricare più forecast;
3. normalizzare e mantenere Parquet, non raw illimitato;
4. aggiungere IFS/AIFS/ICON soltanto con una retention e licenza documentate;
5. non dichiarare “previsioni locali Italia” finché il test geografico non supera i criteri del documento di benchmark.

## Questioni aperte per Fase 4

- Completezza per variabile/stazione ISD e confronto con GHCNh.
- Numero effettivo di stazioni ARPA Piemonte con serie orarie CC-BY e relative discontinuità.
- Misura reale di CPU/RAM/tempo del primo mese di backfill.
- Costi provider-specifici di object storage, egress, VPS e backup, da stimare con listini correnti e regione cloud scelta.
