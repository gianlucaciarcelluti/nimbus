# Registro delle fonti e delle licenze

Questo registro separa la licenza del software Nimbus dalle condizioni applicabili a dati, API, output e artefatti di terzi.

| Fonte | Stato di utilizzo in Nimbus | Licenza / condizioni da verificare | Regola repository |
| --- | --- | --- | --- |
| ECMWF IFS e AIFS | Candidata | CC-BY-4.0 per prodotti Open Data; retention e accesso al catalogo storico separati | Non committare GRIB o output senza verifica puntuale |
| NOAA GFS, ISD/GHCNh | Candidata | Public domain/CC0 per dati federali, salvo metadati specifici | Pubblicare al massimo script di acquisizione e metadati |
| Copernicus ERA5 | Candidata | CC-BY, con attribuzione C3S/Copernicus | Nessun dato grezzo nel repository |
| DWD ICON / ICON-EU | In verifica | Condizioni specifiche dell'output NWP da confermare | Nessuna ridistribuzione finché non validata |
| EUMETSAT | In verifica | Dipende dalla collezione: Core o Recommended | Nessun asset satellitare/radar nel repository |
| ARPA, Protezione Civile, MeteoAM | In verifica | Dataset e regione specifici | Nessuna integrazione prima del censimento legale |

Ogni futura pipeline dovrà registrare `provider`, `dataset`, `product_version`, `licence`, `retrieval_time`, `publication_time`, checksum e politica di retention.
