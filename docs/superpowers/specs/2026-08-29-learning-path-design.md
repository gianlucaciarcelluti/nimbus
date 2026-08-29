# Percorso didattico interattivo — design

Versione: 1.0 · Data: 2026-08-29 · Stato: approvato in brainstorming, non ancora implementato.

## 1. Scopo e collocazione

Costruire in `learning/` un percorso formativo in cinque notebook Python che porti una persona senza esperienza dal nulla fino a una stima di previsione elementare, passando per scarico dati da fonti pubbliche, lettura di mappe NWP, join forecast-osservazione e valutazione.

Il percorso ha due destinatari nello stesso artefatto: è il banco di prova personale del maintainer, ma è scritto con la cura necessaria a servire in seguito come onboarding per nuovi contributor.

### Cosa NON è

Questa distinzione va dichiarata in apertura del `learning/README.md` e ripetuta nel notebook 01.

- Non è la pipeline Nimbus né un suo prototipo: la pipeline vera comincia da M0 del [piano MVP](../../08-mvp-implementation-plan.md).
- Non è autorevole sui contratti dati: la fonte di verità resta `docs/`.
- Non produce previsioni pubblicabili né validate: nessun output di `learning/` può essere presentato come forecast Nimbus.
- Il suo codice non confluisce nel futuro package `nimbus`; le sue dipendenze non vincolano quelle della pipeline.

## 2. Decisioni

| Ambito | Decisione | Alternative escluse | Motivazione |
| --- | --- | --- | --- |
| Destinatario | Banco di prova personale, scritto per servire poi da onboarding | Divulgazione generale; onboarding puro | Il rigore Nimbus va insegnato, non solo rispettato |
| Strategia dati | Ibrido a due velocità: campione piccolo eseguibile in minuti, comando reale documentato per scalare | Solo dati live; solo archivio storico completo | Un percorso che richiede ore di download prima della prima cella utile non viene completato |
| Onestà scientifica | Il limite del campione si insegna esplicitamente | Arrivare a un numero che sembri una conclusione | Coerente con la distinzione misura/stima dei doc esistenti |
| Struttura | 5 notebook sequenziali che si passano file su disco + `common.py` minimale | Notebook unico; package che incapsula il download | La staffetta via file insegna l'artefatto intermedio; incapsulare il download nasconde ciò che si vuole insegnare |
| GRIB | `cfgrib`/eccodes affrontato di petto, con verifica ambiente diagnostica | API a dati puntuali (Open-Meteo); doppio percorso | Evitare la griglia produce uno studente che non ha mai visto il problema che il post-processing risolve |
| Selezione area | Bounding box regionale scritta a mano, con area sempre visualizzata | Point-in-polygon con confini ISTAT e `geopandas` | Sufficiente per filtrare un inventario; evita una dipendenza pesante. L'imprecisione diventa visibile sulla mappa |
| Default area | Piemonte | Nessun default | Coerente con il pilota prioritario dei doc 03 e 04 |

## 3. Struttura dei file

```
learning/
  README.md              # cos'è, cosa non è, come si esegue, ordine dei notebook
  requirements.txt       # dipendenze pinnate
  common.py              # path, config, bbox regionali, download con cache+checksum
  test_common.py         # test del solo common.py
  notebooks/
    01-setup-e-fondamenti.ipynb
    02-osservazioni-isd.ipynb
    03-forecast-gfs-grib.ipynb
    04-join-e-anti-leakage.ipynb
    05-baseline-e-previsione.ipynb
  data/                  # gitignorato, generato dai notebook
  .venv/                 # gitignorato
```

Il venv è locale a `learning/`. Verificato il 2026-08-29: i pattern `data/` e `.venv/` del `.gitignore` esistente coprono già `learning/data/` e `learning/.venv/`; nessuna riga aggiuntiva è necessaria.

`common.py` contiene esclusivamente ciò che è ripetitivo e non didattico: costanti di path, la tabella dei bounding box regionali, e un helper di download con cache su disco e verifica checksum. Ogni contenuto meteorologico o statistico resta visibile nelle celle dei notebook.

## 4. Contratto tra notebook

Ogni notebook legge solo file, mai variabili in memoria di un altro notebook. Nessun notebook sovrascrive l'output di un altro.

| Notebook | Legge | Scrive |
| --- | --- | --- |
| 01 setup | — | `data/00_env_report.json` |
| 02 osservazioni | inventario ISD remoto | `data/01_stations.csv`, `data/02_observations.parquet` |
| 03 forecast | `data/01_stations.csv` | `data/03_forecast_points.parquet`, GRIB in `data/raw/` |
| 04 join | `data/02_*`, `data/03_*` | `data/04_dataset.parquet` (con colonna `split`) |
| 05 baseline | `data/04_dataset.parquet` | `data/05_metrics.json`, grafici |

Tre proprietà volute:

- **Il notebook 03 scrive già punti-stazione, non griglie.** L'interpolazione griglia-stazione avviene dove la griglia è sotto mano e disegnabile; il notebook 04 riceve due tabelle omogenee e si concentra interamente sul tempo.
- **Lo split è una colonna, non tre file.** Il notebook 05 filtra `split == 'train'` per il fit e il test resta visibile e intoccato; con file separati caricare quello sbagliato è più facile da nascondere.
- **I GRIB grezzi restano in `data/raw/` con retention dichiarata**, rispecchiando la policy dei 14 giorni del [doc 05](../../05-mvp-data-feasibility.md).

Conseguenza accettata: saltare un notebook rompe il successivo. Ogni notebook si apre quindi con un controllo degli input che nomina il notebook mancante, invece di sollevare un `FileNotFoundError` nudo.

## 5. Selezione dell'area

La scelta della regione coinvolge lo studente mostrandogli l'errore del modello vicino a casa propria, ma la copertura ISD italiana non è uniforme: delle 124 stazioni candidate, 89 sono sotto 300 m e 13 sopra 1.000 m.

- Il parametro `REGIONE` si imposta una sola volta, in cima al notebook 02, e si propaga ai successivi tramite `data/01_stations.csv`.
- La selezione è geografica per bounding box: l'inventario ISD ha coordinate, non un campo regione.
- Dopo il filtro, il notebook 02 conta le stazioni e le classifica per fascia altimetrica. **Sotto le 3 stazioni non procede**: dichiara quante ne ha trovate, mostra la mappa nazionale delle candidate e propone di allargare alla macro-area o alle regioni confinanti. Degrado esplicito, mai un risultato su campione insufficiente.
- Il bbox regionale restringe anche il subset GFS del notebook 03, che diventa più rapido da scaricare. Il notebook 03 deve comunque mostrare almeno una volta l'Italia intera prima di zoomare.

### Visualizzazione dell'area (requisito)

La mappa dell'area è obbligatoria in tre momenti:

1. **Notebook 02** — Italia con tutte le candidate in grigio, il bbox come rettangolo, le stazioni selezionate evidenziate con nome e quota. Rende visibile anche l'imprecisione del bbox sui confini.
2. **Notebook 03** — Italia intera con griglia GFS a 0,25°, poi zoom sull'area con celle e punti-stazione sovrapposti. È la figura che mostra il concetto centrale: la stazione sta dentro una cella di 25 km la cui quota non è la sua.
3. **Notebook 05** — stazioni colorate per MAE. Mostra dove il modello sbaglia di più, tipicamente in quota.

Libreria: `matplotlib` con `cartopy`. Avendo `cartopy` dipendenze binarie (GEOS/PROJ), entra nella verifica ambiente del notebook 01 con lo stesso trattamento diagnostico di eccodes. Fallback se non installabile: disegnare senza confini costieri, perdendo il contorno ma non stazioni e griglia.

## 6. Contenuto dei notebook

Ogni notebook segue lo schema: **cosa impari → contesto minimo → codice eseguibile commentato → cosa hai ottenuto → il limite di quello che hai fatto**. L'ultima voce ricorre in ogni notebook, non solo nel quinto.

### 01 — Setup e fondamenti (~30 min, nessun download pesante)

Creazione venv, installazione, verifica. La cella centrale verifica `cfgrib`/eccodes e `cartopy`, trattando la dipendenza binaria come argomento esplicito: perché è diversa da una pura-Python, cosa fare se fallisce su macOS. Il fallimento produce un messaggio diagnostico, non un `ImportError` criptico.

Nozioni minime: cos'è un modello NWP e perché ha una griglia; run time, valid time, lead; UTC e perché non si usa l'ora locale; cos'è GRIB e perché non è un CSV.

### 02 — Osservazioni ISD (~45 min, download leggero)

Scarica l'inventario `isd-history.csv`, lo stesso usato per la Misura 1 del doc 05: lo studente **riproduce numeri presenti nella documentazione del progetto** (318 record `CTRY=IT`, 124 candidate). Primo punto di contatto reale fra percorso e repo.

Selezione di 3-5 stazioni nell'area scelta con contrasto pianura/montagna, download di pochi mesi di osservazioni, e la parte sporca: formato a larghezza fissa, valori sentinella, flag QA, fusi, buchi.

Limite insegnato: completezza della stazione ≠ completezza della variabile.

### 03 — Forecast GFS e GRIB (~45 min, download medio)

Subset GFS via NOMADS con bbox, stessa procedura della Misura 2 del doc 05: lo studente vede da dove viene il valore di 5,46 MB. Apertura con `xarray` + `cfgrib`, esplorazione delle dimensioni, **prima mappa** — il momento gratificante arriva al terzo notebook, non al quinto.

Poi il passaggio concettuale dalla griglia al punto: interpolazione nearest vs bilineare, e differenza di quota fra cella del modello e stazione reale, che è la ragione fisica per cui il post-processing funziona.

Limite insegnato: NOMADS conserva circa 10 giorni, quindi non è un archivio storico. Il comando per l'archivio S3 (`noaa-gfs-bdp-pds`) è mostrato ma non eseguito.

### 04 — Join e anti-leakage (~40 min, nessun download)

Il notebook concettualmente più importante: giustifica l'esistenza del [protocollo anti-leakage](../../02-historical-forecast-observation-protocol.md).

Costruzione della tabella stazione-run-lead unendo 02 e 03 con intervalli half-open `[start, end)`.

**Il leakage si insegna facendolo.** Si costruisce deliberatamente una feature che usa un'osservazione posteriore a `publication_time_utc`, si mostra che il modello risultante sembra eccellente, si spiega perché è una bugia. Stessa tecnica per lo split casuale contro quello temporale: su serie autocorrelate il random split produce metriche migliori e false.

**Vincolo di sicurezza:** il codice deliberatamente scorretto va marcato in modo inequivocabile — cella preceduta da un avviso e nomi di variabile autoesplicativi del tipo `feature_SBAGLIATA_non_usare` — perché nessuno lo copi per errore.

### 05 — Baseline e previsione basic (~40 min, nessun download)

Rispetta l'ordine obbligatorio del progetto: climatologia → persistenza → GFS raw → bias correction. Ognuna sullo stesso campione e con lo stesso metodo di interpolazione, perché il confronto sia equo.

Metriche MAE/RMSE/bias, errore per lead e per stazione, mappa dell'errore.

Conclusione onesta: su 3-5 stazioni e pochi mesi un eventuale miglioramento **non è statisticamente dimostrabile**. Si mostra l'intervallo bootstrap che rende visibile l'incertezza e si elenca cosa servirebbe davvero — le 124 stazioni, gli anni di storico, i segmenti obbligatori del [piano benchmark](../../04-mvp-benchmark-validation-plan.md). Chiude indicando M0 del piano MVP come seguito serio.

## 7. Testing

L'unico componente con logica non didattica è `common.py`, ed è l'unico che si testa, in TDD:

- risoluzione dei path e creazione delle directory di output;
- tabella bbox: copertura delle regioni previste, coerenza dei valori (lat/lon plausibili, min < max);
- helper di download: cache hit senza rete, verifica checksum, comportamento su checksum errato.

I notebook non hanno test automatici. La loro verifica è l'esecuzione completa in ordine su un ambiente pulito, che va eseguita prima di considerare il percorso concluso.

## 8. Rischi

| Rischio | Mitigazione |
| --- | --- |
| eccodes o cartopy non si installano sulla macchina dello studente | Verifica diagnostica nel notebook 01; fallback documentato per cartopy |
| Regione scelta con copertura ISD insufficiente | Soglia di 3 stazioni con arresto esplicito e proposta di allargamento |
| Endpoint NOMADS o ISD cambiano formato o URL | Il percorso dichiara la data di verifica; il fallimento del download produce un messaggio che rimanda alla fonte ufficiale |
| Il codice di esempio scorretto del notebook 04 viene copiato | Marcatura esplicita e nomi di variabile autoesplicativi |
| I notebook divergono dai docs con l'evolvere del progetto | Il README dichiara che `docs/` prevale; i numeri riprodotti citano il documento di origine |
| Output committati per errore (dati, GRIB, notebook eseguiti) | `.gitignore` già copre `learning/data/` e `learning/.venv/`; gli output delle celle vanno ripuliti prima del commit dei notebook |

## 9. Fuori perimetro

Nowcasting, radar, deep learning, ensemble multi-modello, downscaling, dati ARPA, backfill esteso, qualunque forma di pubblicazione o serving. Il percorso si ferma alla bias correction su un campione dichiaratamente non conclusivo.
