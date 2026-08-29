# Nimbus

Piattaforma open-source per ricerca e sperimentazione su previsioni meteorologiche locali per l'Italia: ensemble multi-modello, post-processing statistico e machine learning.

## Stato

Il progetto è nella fase di discovery e fattibilità. Non contiene ancora codice operativo né fornisce previsioni al pubblico.

## Principi

- Riproducibilità: benchmark, split temporali e metriche devono essere documentati.
- Trasparenza: ogni previsione deve poter essere ricondotta a dati, run e licenze.
- Legalità dei dati: nel repository non sono inclusi dati grezzi, credenziali o output redistribuibili senza una verifica esplicita della licenza.
- Rigore: un miglioramento ML è valido soltanto se supera baseline meteorologiche con una validazione temporale e geografica indipendente.

## Documentazione

- [Data & Model Landscape](docs/01-data-model-landscape.md)
- [Historical Forecast-to-Observation Dataset Protocol](docs/02-historical-forecast-observation-protocol.md)
- [Censimento delle osservazioni italiane](docs/03-italy-observation-source-census.md)
- [Piano MVP, benchmark e validazione](docs/04-mvp-benchmark-validation-plan.md)
- [Misure di fattibilità del dataset MVP](docs/05-mvp-data-feasibility.md)
- [Architettura di riferimento](docs/06-reference-architecture.md)
- [Registro delle fonti e delle licenze](docs/data-sources-register.md)

## Licenza software

Il codice di Nimbus è distribuito con licenza Apache-2.0. Le licenze dei dati restano quelle dei rispettivi fornitori e sono indipendenti dalla licenza del software.
