# Censimento delle osservazioni meteorologiche italiane

Data della verifica: 2026-08-29. Stato: Fase 2, prima ricognizione. “Disponibile” non equivale a “approvato per l'ingestion”: ogni fonte dovrà superare i controlli su licenza, API, metadati, QA e continuità.

## Esito operativo

Non esiste una rete nazionale unica pronta per il riuso commerciale e per il training orario ad alta risoluzione. La strategia corretta è a due livelli:

1. MVP nazionale: GHCNh/ISD come target puntuale comune, con copertura dichiaratamente limitata.
2. Pilota locale: Piemonte e, dopo una prova tecnica, Emilia-Romagna. Sono le fonti più promettenti per densità, dati machine-readable e condizioni aperte esplicite.

## Matrice delle fonti

| Area / fornitore | Evidenza verificata | Dati e accesso | Licenza / vincolo | Decisione Fase 2 |
| --- | --- | --- | --- | --- |
| NOAA ISD / GHCNh | Archivio globale di osservazioni orarie/sinottiche; ISD dal 1901, aggiornamento quotidiano; GHCNh introduce anche Parquet | T, Td, pressione, vento/gust, nuvole, visibilità, fenomeni e precipitazioni quando presenti | Dati federali NOAA normalmente public domain/CC0; verificare eventuali contributi di terzi nel record | **Baseline nazionale approvata**, con audit di copertura e qualità | 
| ARPA Piemonte | Open Data dichiarati CC-BY-4.0 salvo diversa indicazione; rete >400 stazioni nel capitolato 2026; API real-time/storica documentate | Realtime degli ultimi 6 giorni; storico giornaliero/mensile dall'avvio dei singoli sensori; T, precipitazione, UR, radiazione, vento; radar 5 min, realtime | Attribuzione obbligatoria; non è garantita continuità di API/dataset | **Pilota locale prioritario**; verificare in test che l'API storica renda serie idonee e i campi siano effettivamente CC-BY | 
| ARPAE Emilia-Romagna | Catalogo CKAN filtra dataset meteo come CC-BY; include osservati e radar HDF5 | API catalogo; dettagli di endpoint, profondità storica e QA da ispezionare | CC-BY indicato dal catalogo per dataset meteo selezionati | **Pilota alternativo / estensione** dopo test di metadati | 
| ARPA Lombardia | Rete dichiarata di 318 stazioni, aggiornate 10 min; form rende CSV gratuiti, inclusi dati suborari/orari/giornalieri e anagrafica | Risposta via email; massimo 7 parametri; l'operatore completa validazione entro 30 giugno dell'anno successivo | Pagina rimanda al regolamento per uso di logo e dati; licenza dataset non confermata qui | **In verifica legale e di automazione**; non è fonte MVP finché non esiste autorizzazione/termine riuso chiaro | 
| ARPA FVG / OSMER | >160 stazioni regionali, archivio per stazioni prioritarie; radar e reti disponibili | Download per stazione; fonte utile scientificamente | Tariffario: dati/radar e previsioni sul sito consentiti ai soli end-user; fornitura può essere onerosa e non trasferibile | **Esclusa dal dataset pubblico/commerciale** fino ad accordo esplicito | 
| ARPAL Liguria | Portale OMIRL rende consultabili/esportabili alcuni dati; Piemonte condivide anche radar Monte Settepani | Da ispezionare endpoint, storico e licenza del dataset specifico | Non verificata una licenza commerciale uniforme | **Candidata, non approvata** | 
| ARPA Sicilia | L'agenzia dichiara di non produrre un dataset meteo regionale adatto ai bollettini | Indica SIAS, servizio idrologico e Protezione Civile come enti territoriali | Da verificare direttamente con i fornitori indicati | **Nessuna fonte ARPA utilizzabile** | 
| Meteo Aeronautica Militare | Disponibilità e cessione dati disciplinate da listino e licenze | Richiesta/accordo | Non trattare come open data | **Fuori MVP** |

## Regole di accettazione di una stazione

Una stazione entra nel dataset soltanto se possiede: identificatore persistente, coordinate WGS84, quota, fuso/timestamp documentato, variabile/unità, intervallo di aggregazione, periodo di attività del sensore, flag QA, licenza esplicita e almeno il 90% di completezza nel periodo di valutazione. Le serie devono essere spezzate quando cambia sensore, posizione, quota o metodo di misura.

La validazione automatica non è equivalente a validazione finale: ARPA Lombardia dichiara esplicitamente una validazione operatore differita; ARPA Piemonte avverte che i dati suborari possono essere soggetti a correzioni. Tali record devono avere `qa_level` e non essere promossi automaticamente a ground truth definitivo.

## Fonti ufficiali

- [NOAA ISD](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database) e [documentazione GHCNh](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf)
- [ARPA Piemonte — Open Data](https://www.arpa.piemonte.it/dato/open-data), [note legali](https://www.arpa.piemonte.it/note-legali), [banca dati storica](https://www.arpa.piemonte.it/dato/banca-dati-storica-dati-giornalieri-mensili)
- [Catalogo meteo ARPAE CC-BY](https://dati.arpae.it/tr/dataset/?groups=meteo&license_id=cc-by&organization=arpa-emilia-romagna)
- [ARPA Lombardia — richiesta dati](https://www.arpalombardia.it/temi-ambientali/meteo-e-clima/form-richiesta-dati/)
- [ARPA FVG — servizio e condizioni](https://arpa.fvg.it/temi/temi/meteo-e-clima/news/dati-meteorologici-interpolati-sul-territorio-un-nuovo-servizio-di-arpa-fvg/) e [tariffario](https://www.arpa.fvg.it/arpa/agenzia/tariffario/)
- [ARPA Sicilia — FAQ](https://www.arpa.sicilia.it/urp/domande-frequenti-faq/)
- [MeteoAM — disponibilità dati](https://www.meteoam.it/it/disponibilita-dati)
