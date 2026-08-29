# Data & Model Landscape — Fase 1

Data della verifica: 2026-08-29.

## Conclusione

Il primo esperimento riproducibile deve usare GFS storico, ERA5, osservazioni NOAA ISD/GHCNh e un DEM. IFS, AIFS e ICON-EU sono fonti importanti, ma non devono essere assunte come archivi storici gratuiti e completi: la raccolta prospettica e la verifica contrattuale sono necessarie.

## Fonti primarie

- ECMWF Open Data: <https://www.ecmwf.int/en/forecasts/datasets/open-data>
- ECMWF Archive Catalogue: <https://www.ecmwf.int/en/forecasts/accessing-forecasts/order-historical-datasets>
- ECMWF AIFS: <https://www.ecmwf.int/en/forecasts/dataset/aifs-machine-learning-data>
- NOAA GFS archive: <https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast>
- NOAA ISD: <https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database>
- ERA5: <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels>
- DWD Open Data: <https://opendata.dwd.de/weather/nwp/>
- EUMETSAT licensing: <https://user.eumetsat.int/resources/user-guides/data-registration-and-licensing>

## Decisioni provvisorie

1. Non basare l'MVP su radar, satellite o dati ARPA non ancora autorizzati.
2. Non trattare ERA5 come se fosse una previsione storica emessa al tempo T.
3. Archiviare prospetticamente un subset Italia + buffer di IFS, AIFS e ICON-EU.
4. Mantenere un registro per run, valid time, versione e licenza di ogni dato ingerito.
