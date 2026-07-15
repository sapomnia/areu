# Scraper AREU — Missioni 118 Lombardia, agosto 2026

Raccoglie ogni giorno i dati pubblicati da AREU (Agenzia Regionale Emergenza
Urgenza della Lombardia) sulla pagina
[Missioni 118](https://www.areu.lombardia.it/web/home/missioni-aat-real-time),
per tutti i 31 giorni di **agosto 2026**.

## Come funziona

Le tabelle della pagina sono popolate via JavaScript da un'API JSON pubblica:

```
https://www.areu.lombardia.it/api/jsonws/eventiregionejson.eventiregionejson/statistiche-regione
```

L'API espone solo i dati di **oggi** e di **ieri**: per questo lo scraper gira
ogni giorno dal 2 agosto al 1° settembre 2026 e salva ogni volta i dati di
"ieri" (completi, riferiti all'intera giornata precedente).

[scraper.py](scraper.py) accoda le righe a tre CSV nella cartella `data/`:

| File | Contenuto | Righe per giorno |
|---|---|---|
| `chiamate_pervenute.csv` | Chiamate pervenute per tipologia | 4 (una per SOREU) |
| `motivi_intervento.csv` | Motivi di intervento per i Soccorsi Primari con missione | 12 (una per AAT) |
| `missioni_primari.csv` | Missioni per i Soccorsi Primari (codici colore e mezzi) | 12 (una per AAT) |

Note sui dati:

- le date sono in formato ISO (`2026-08-01`);
- nelle chiamate pervenute i campi vuoti (es. `trasporto_organi`) sono valori
  che l'API restituisce vuoti, non zeri;
- in `missioni_primari.csv` le colonne `msa1` e `msa2` corrispondono ai campi
  API `msi` e `msa` (le etichette della pagina sono MSA1 e MSA2).

## Automazione

Il workflow [.github/workflows/scrape.yml](.github/workflows/scrape.yml) gira
due volte al giorno (07:10 e 19:10 ora italiana) dal 2 agosto al 1° settembre
2026: la seconda esecuzione è una rete di sicurezza nel caso la prima fallisca
(i cron di GitHub Actions possono subire ritardi o essere saltati). Lo script è
idempotente, quindi la doppia esecuzione non crea duplicati. I CSV aggiornati
vengono committati direttamente nel repository.

Il workflow può anche essere lanciato a mano dalla tab **Actions → Scraper
AREU agosto 2026 → Run workflow** (utile per un test subito dopo il push).

## Esecuzione manuale

```bash
python3 scraper.py
```

Nessuna dipendenza esterna: basta Python 3 (libreria standard).

## Attenzione

- **Se una giornata viene persa non è recuperabile**: l'API pubblica solo oggi
  e ieri. Da qui la doppia esecuzione giornaliera. Per sicurezza, controllare
  ogni tanto ad agosto che i commit automatici stiano arrivando.
- GitHub disabilita i cron nei repository senza attività da 60 giorni: se il
  repo viene creato ora e resta fermo fino ad agosto, fare un commit (o
  ri-abilitare il workflow dalla tab Actions) a fine luglio 2026.
