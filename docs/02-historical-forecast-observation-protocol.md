# Historical Forecast-to-Observation Dataset Protocol

Stato: bozza per la Fase 2.

## Obiettivo

Costruire esempi di training che rappresentino esattamente l'informazione disponibile quando una previsione è stata pubblicata e l'osservazione che la verifica successivamente.

## Identificatori temporali obbligatori

| Campo | Significato |
| --- | --- |
| `run_time_utc` | Istante di inizializzazione del modello. |
| `publication_time_utc` | Primo istante verificato in cui il file era disponibile alla pipeline. |
| `lead_hours` | Differenza tra valid time e run time. |
| `valid_time_utc` | Istante o intervallo a cui si riferisce la previsione. |
| `observation_time_utc` | Istante/intervallo della misura usata come target. |
| `ingestion_time_utc` | Istante di acquisizione da Nimbus; non sostituisce publication time. |

La relazione fondamentale è:

`valid_time_utc = run_time_utc + lead_hours`

## Unità minima del dataset

Una riga punto-tempo-lead deve contenere:

- chiave della stazione o cella;
- coordinate, quota e feature statiche;
- provider, modello, versione e run;
- feature estratte soltanto dal forecast/analisi disponibili entro `publication_time_utc`;
- osservazione verificata, unità, intervallo di accumulo e flag QA;
- licenza, URL/origine, checksum e versione del processo di normalizzazione.

## Regole anti-leakage

1. Non usare osservazioni, analisi o revisioni rese disponibili dopo `publication_time_utc` come feature.
2. Non mischiare forecast emessi dopo l'evento con forecast emessi prima dell'evento.
3. Per precipitazione accumulata, allineare esattamente l'intervallo previsto e l'intervallo osservato.
4. Dividere train, validation e test nel tempo; vietato random split per record adiacenti.
5. Conservare la versione del modello meteo: i cambi di ciclo sono possibili confondenti.
6. Non usare ERA5 come feature contemporanea: una reanalisi incorpora osservazioni raccolte anche dopo il momento della previsione. ERA5 può contribuire soltanto a climatologie, anomalie e statistiche aggregate calcolate esclusivamente sul periodo precedente al cutoff del relativo split.

## Prima baseline proposta

- area: Italia con buffer meteorologico;
- target: T2m, Td2m, vento, pressione e precipitazione oraria;
- forecast: GFS 0,25°, run 00/06/12/18 UTC, lead 1–72 h;
- feature statiche: DEM; ERA5 soltanto per climatologie/aggregati calcolati sul passato del rispettivo split;
- osservazione: ISD/GHCNh, con filtro esplicito su completezza e qualità;
- split: train 2021–2024, validation 2025, test 2026, con blocchi per stagione e analisi separata degli eventi estremi.

## Vincolo aperto

La densità di ISD/GHCNh in Italia e le licenze delle reti ARPA devono essere misurate prima di dichiarare questa baseline rappresentativa dell'intero territorio italiano.
