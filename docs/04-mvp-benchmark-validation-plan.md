# Piano MVP, benchmark e validazione

Stato: Fase 2. Questo documento definisce il primo esperimento che può confutare o sostenere l'ipotesi di valore di Nimbus senza dichiarare un miglioramento non dimostrato.

## Decisione di perimetro

| Dimensione | MVP nazionale | Pilota locale consigliato |
| --- | --- | --- |
| Area | Italia, con buffer di 3° attorno al territorio | Piemonte; estensione successiva Emilia-Romagna |
| Target | T2m, Td2m, pressione, velocità/direzione vento, precipitazione oraria | T2m e precipitazione giornaliera; oraria solo dopo audit API/QA |
| Forecast storico | GFS 0,25°, run 00/06/12/18 UTC, lead 1–72 h | Idem, più confronto con dataset regionale se legalmente approvato |
| Osservazioni | GHCNh/ISD | ARPA Piemonte CC-BY-4.0, più GHCNh come controllo indipendente |
| Feature statiche | DEM, latitudine, longitudine, quota, distanza costa, calendario | Come MVP nazionale |
| Feature dinamiche | Solo output disponibili nel forecast GFS al run selezionato | Come MVP nazionale |

Nessuna reanalisi o osservazione posteriore a `publication_time_utc` può entrare nelle feature. ERA5 è ammesso solo per costruire, all'interno del training set, climatologie passate e anomalie senza contaminare validation/test.

## Struttura logica dei record

Chiave primaria proposta:

`source_station_id, variable, run_time_utc, lead_hours, valid_start_utc, valid_end_utc, model_id, model_version`

Campi obbligatori: `forecast_value`, `forecast_unit`, `observation_value`, `observation_unit`, `observation_qa_level`, `publication_time_utc`, `lat`, `lon`, `station_elevation_m`, `model_grid_elevation_m`, `source_url`, `licence_id`, `raw_checksum`, `normalization_version`.

Per le quantità accumulate, come la pioggia, il target è l'intervallo `[valid_start_utc, valid_end_utc)` e non un singolo timestamp.

## Split e blocchi di valutazione

| Split | Periodo proposto | Uso consentito |
| --- | --- | --- |
| Train | 2021-01-01 – 2024-12-31 | Fit di trasformazioni, calibrazione e modelli |
| Validation | 2025-01-01 – 2025-12-31 | Scelta iperparametri e soglie, una sola volta |
| Test congelato | 2026-01-01 – 2026-12-31 | Report finale; mai usato per tuning |

Il test viene inoltre segmentato per: macro-area (Alpi, Pianura Padana, Appennini, coste/Tirreno, Adriatico, isole), stagione, ora locale, fascia altimetrica, lead 1–6/7–24/25–48/49–72 h e classi evento. Se il 2026 non è ancora completo al momento dell'esecuzione, il test si sposta all'ultimo anno completo non usato per tuning.

## Baseline obbligatorie

1. Persistenza per lead molto brevi, quando una precedente osservazione è disponibile.
2. Climatologia stagionale e oraria calcolata solo sul train.
3. GFS raw, con stessa interpolazione stazione-griglia usata dal modello Nimbus.
4. Bias correction semplice: correzione media/quantile per stazione, mese e lead, fitted soltanto sul train.
5. Primo modello ML soltanto se supera le quattro baseline su validation e test congelato.

Non è accettabile confrontare il modello ML con una versione del GFS interpolata diversamente o valutata su campioni diversi.

## Metriche pubblicate

| Target | Metriche primarie | Segmenti obbligatori |
| --- | --- | --- |
| Temperatura / Td / pressione | MAE, RMSE, bias mediano e signed bias | Stazione, altitudine, stagione, lead |
| Vento | MAE su velocità, errore vettoriale, bias; raffiche separatamente | Costa/montagna/pianura, lead |
| Precipitazione quantità | MAE e RMSE sui positivi; quantili d'errore | 0.1, 1, 5, 10, 20 mm e percentile 95/99 |
| Evento pioggia | Precision, recall, F1, CSI, POD, FAR | Soglie e lead |
| Probabilità / ensemble | Brier Score e Brier Skill Score, CRPS/CRPSS, reliability diagram, sharpness e ROC-AUC | Evento, stazione, stagione e numerosità del bin |

La WMO richiede verifiche oggettive standardizzate per confrontare prodotti; ECMWF descrive Brier, CRPS, reliability e ROC come misure complementari. Una reliability curve senza istogramma di sharpness o intervalli di confidenza non è sufficiente per comunicare una “confidence”.

## Criterio go / no-go del primo ML

Il candidato ML passa alla Fase 3 soltanto se, sul test congelato:

- migliora la baseline GFS raw e la bias correction semplice su almeno due metriche primarie per T2m;
- non peggiora materialmente le metriche di probabilità/calibrazione;
- il miglioramento resta presente in almeno tre macro-aree e in due stagioni;
- il report include intervalli di confidenza bootstrap per stazione-giorno, non soltanto per singolo record;
- per pioggia forte non si dichiara superiorità se i campioni sono troppo pochi.

Non fissiamo ora una percentuale minima di miglioramento: va stimata dopo il baseline report e accompagnata da intervalli di incertezza.

## Decision log

| Data | Decisione | Alternative | Evidenza | Conseguenza |
| --- | --- | --- | --- | --- |
| 2026-08-29 | Separare MVP nazionale e pilota locale | Un unico modello “iperlocale Italia” | Osservazioni e licenze sono frammentate | Le dichiarazioni di copertura saranno differenziate |
| 2026-08-29 | Usare GFS come prima fonte forecast storica | IFS/AIFS/ICON subito | GFS 0,25° è archiviato dal 2021; gli archivi ECMWF hanno accesso contrattuale | Baseline più riproducibile, ma non ancora ensemble completo |
| 2026-08-29 | Piemonte come pilota prioritario | Lombardia, FVG, Sicilia | CC-BY-4.0 e API/storico dichiarati; altri vincoli più incerti o restrittivi | Verifica tecnica focalizzata prima di estendere |
| 2026-08-29 | Test temporale congelato | Random split | Le serie meteo hanno autocorrelazione e rischio di leakage | Metriche più conservative ma credibili |

## Fonti metodologiche

- [WMO — Forecast Verifications](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-integrated-processing-and-prediction-system-wipps/forecast-verifications)
- [WMO — qualità e controllo delle osservazioni](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/instruments-and-methods-of-observation-programme-imop)
- [ECMWF — reliability, Brier e ROC](https://confluence.ecmwf.int/spaces/FUG/pages/673551584/Section%2B8.3.5%2BUsing%2Bverification%2Bmetrics%2Bwith%2Bthe%2Boutput)
- [ECMWF — RMSE, Brier, CRPS e verifica](https://www.ecmwf.int/en/about/media-centre/science-blog/2026/separating-signal-noise)
