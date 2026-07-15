#!/usr/bin/env python3
"""Scraper dei dati AREU (missioni 118 Regione Lombardia).

Interroga l'API JSON pubblica che alimenta la pagina
https://www.areu.lombardia.it/web/home/missioni-aat-real-time
ed estrae le righe relative agli "Eventi di Ieri", accodandole
a tre CSV:

- chiamate_pervenute.csv   (una riga per SOREU)
- motivi_intervento.csv    (una riga per AAT - Soccorsi Primari con missione)
- missioni_primari.csv     (una riga per AAT - Missioni per i Soccorsi Primari)

Lo script è idempotente: se la data di "ieri" è già presente nei CSV
non aggiunge nulla, quindi può essere eseguito più volte al giorno.
"""

import csv
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

API_URL = (
    "https://www.areu.lombardia.it/api/jsonws/"
    "eventiregionejson.eventiregionejson/statistiche-regione"
)

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "data"

# colonna CSV -> chiave nel JSON dell'API
CHIAMATE_FIELDS = {
    "totale": "totale_traffico_tel",
    "soccorso_primario": "soccorso_primario",
    "soccorso_secondario": "soccorso_secondario",
    "informazione": "informazioni",
    "consulenza": "consulenza",
    "trasporto_organi": "trasporto_organi",
    "altro": "altro",
}

MOTIVI_FIELDS = {
    "totale": "totale_missioni",
    "medico_acuto": "medico_acuto",
    "caduta": "caduta",
    "incidente_stradale": "incidente_stradale",
    "infortunio": "infortunio",
    "evento_violento": "evento_violento",
    "intossicazione": "intossicazione",
    "animali": "animali",
    "calamita_naturale": "calamita_naturale",
    "evento_massa": "evento_massa",
    "incidente_acqua": "incidente_acqua",
    "incidente_montano": "incidente_montano",
    "incidente_speleo": "incidente_speleo",
    "soccorso_persona": "soccorso_persona",
    "altro_non_noto": "non_noto",
    "altri_motivi": "motivo_altro",
}

MISSIONI_FIELDS = {
    "totale": "missioni",
    "codice_rosso": "rosso",
    "codice_giallo": "giallo",
    "codice_verde": "verde",
    "codice_bianco": "bianco",
    "msb": "msb",
    "msa1": "msi",
    "msa2": "msa",
    "elisoccorso": "elisoccorso",
    "soccorso_alpino": "soccorso_alpino",
    "soccorso_acqua": "soccorso_acqua",
}


def fetch_data():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "areu-scraper"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def to_iso(day_data):
    """'14/07/2026' -> '2026-07-14'"""
    return datetime.strptime(day_data.strip(), "%d/%m/%Y").date().isoformat()


def to_int(value):
    value = (value or "").strip()
    return int(value) if value else ""


def append_rows(path, header, rows, iso_date):
    """Accoda le righe al CSV, saltando se la data è già presente."""
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            if any(row and row[0] == iso_date for row in csv.reader(f)):
                print(f"{path.name}: data {iso_date} già presente, salto.")
                return
        mode = "a"
    else:
        mode = "w"
    with open(path, mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(header)
        writer.writerows(rows)
    print(f"{path.name}: aggiunte {len(rows)} righe per il {iso_date}.")


def main():
    data = fetch_data()
    ieri = [r for r in data.get("del_giorno", []) if r.get("day") == "IERI"]
    if not ieri:
        sys.exit("Nessuna riga 'IERI' nella risposta dell'API.")

    iso_date = to_iso(ieri[0]["day_data"])
    OUT_DIR.mkdir(exist_ok=True)

    # Chiamate pervenute: i dati telefonici sono per SOREU e l'API li valorizza
    # su una sola AAT per SOREU (le altre righe sono vuote).
    chiamate = [
        [iso_date, r["soreu"].strip()]
        + [to_int(r[k]) for k in CHIAMATE_FIELDS.values()]
        for r in ieri
        if r.get("totale_traffico_tel", "").strip()
    ]
    append_rows(
        OUT_DIR / "chiamate_pervenute.csv",
        ["data", "soreu", *CHIAMATE_FIELDS],
        chiamate,
        iso_date,
    )

    motivi = [
        [iso_date, r["aat"].strip(), r["soreu"].strip()]
        + [to_int(r[k]) for k in MOTIVI_FIELDS.values()]
        for r in ieri
    ]
    append_rows(
        OUT_DIR / "motivi_intervento.csv",
        ["data", "aat", "soreu", *MOTIVI_FIELDS],
        motivi,
        iso_date,
    )

    missioni = [
        [iso_date, r["aat"].strip(), r["soreu"].strip()]
        + [to_int(r[k]) for k in MISSIONI_FIELDS.values()]
        for r in ieri
    ]
    append_rows(
        OUT_DIR / "missioni_primari.csv",
        ["data", "aat", "soreu", *MISSIONI_FIELDS],
        missioni,
        iso_date,
    )


if __name__ == "__main__":
    main()
