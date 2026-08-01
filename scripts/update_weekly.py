
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from pathlib import Path
from urllib.parse import quote_plus
import os
import shutil
import xml.etree.ElementTree as ET

import pandas as pd
import requests

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
SNAPSHOTS = DATA / "snapshots"

PROSPECTS = DATA / "prospects.csv"
TERRITORIES = DATA / "territoires.csv"
QUERIES = DATA / "requetes_veille.csv"
SIGNALS = DATA / "signaux_hebdo.csv"
CONSOLIDATED_SIGNALS = DATA / "signaux.csv"
NEW_SIGNALS = DATA / "nouveaux_signaux.csv"
LATEST = DATA / "dernieres_nouveautes.csv"
METADATA = DATA / "metadonnees_application.csv"
HISTORY = DATA / "historique_mises_a_jour.csv"
STATE = DATA / "etat_donnees.csv"
ZONE_STATE = DATA / "etat_zones.csv"

NOW = datetime.now(timezone.utc).replace(microsecond=0)
NOW_ISO = NOW.isoformat().replace("+00:00", "Z")

def safe_read(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, **kwargs)

def rss_url(query: str) -> str:
    return (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(query)}&hl=fr&gl=FR&ceid=FR:fr"
    )

def parse_date(value: str) -> str:
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).date().isoformat()
    except Exception:
        return ""

def collect_signals() -> tuple[pd.DataFrame, list[str]]:
    queries = pd.read_csv(QUERIES, dtype={"territoire": str})
    collected = []
    errors = []
    session = requests.Session()
    session.headers.update({"User-Agent": "RadarCHR/5.2 (+GitHub Actions)"})

    for row in queries.itertuples(index=False):
        try:
            response = session.get(rss_url(row.requete), timeout=30)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            for item in root.findall(".//item")[:15]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                pub_date = parse_date(item.findtext("pubDate") or "")
                source_node = item.find("source")
                source = (
                    source_node.text.strip()
                    if source_node is not None and source_node.text
                    else ""
                )
                description = (item.findtext("description") or "").strip()
                identifier = sha256(
                    f"{title}|{link}".encode("utf-8")
                ).hexdigest()[:20]

                collected.append({
                    "signal_id": identifier,
                    "date_detection_utc": NOW_ISO,
                    "date_publication": pub_date,
                    "territoire": str(row.territoire),
                    "zone": row.zone,
                    "theme": row.theme,
                    "titre": title,
                    "source": source,
                    "url": link,
                    "resume": description,
                    "requete": row.requete,
                    "statut_qualification": "À qualifier",
                })
        except Exception as exc:
            errors.append(f"{row.zone}: {exc}")

    frame = pd.DataFrame(collected)
    if frame.empty:
        frame = pd.DataFrame(columns=[
            "signal_id", "date_detection_utc", "date_publication", "territoire",
            "zone", "theme", "titre", "source", "url", "resume", "requete",
            "statut_qualification"
        ])
    return frame.drop_duplicates("signal_id"), errors

def merge_signals(collected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    previous = safe_read(SIGNALS, dtype={"territoire": str})
    previous_ids = set(previous.get("signal_id", pd.Series(dtype=str)).astype(str))

    collected["est_nouveau"] = ~collected["signal_id"].astype(str).isin(previous_ids)
    new = collected[collected["est_nouveau"]].copy()

    if previous.empty:
        merged = collected.copy()
    else:
        previous["est_nouveau"] = False
        merged = pd.concat([collected, previous], ignore_index=True)
        merged = merged.drop_duplicates("signal_id", keep="first")

    merged = merged.sort_values(
        ["date_publication", "date_detection_utc"], ascending=False
    )
    return merged, new

def prospect_changes() -> tuple[int, int]:
    SNAPSHOTS.mkdir(exist_ok=True)
    reference = SNAPSHOTS / "prospects_reference.csv"
    current = pd.read_csv(PROSPECTS, dtype={"departement": str})
    previous = safe_read(reference, dtype={"departement": str})

    key = ["etablissement", "commune", "departement"]
    current_keys = set(map(tuple, current[key].fillna("").astype(str).values))
    previous_keys = set(map(tuple, previous[key].fillna("").astype(str).values))

    added = len(current_keys - previous_keys)
    removed_or_changed = len(previous_keys - current_keys)

    shutil.copy2(PROSPECTS, reference)
    return added, removed_or_changed

def rebuild_status(new_signal_count: int, errors: list[str]) -> None:
    prospects = pd.read_csv(PROSPECTS, dtype={"departement": str})
    territories = pd.read_csv(TERRITORIES, dtype={"territoire": str})
    signals = safe_read(SIGNALS, dtype={"territoire": str})

    prospects["date_publication"] = pd.to_datetime(
        prospects["date_publication"], errors="coerce"
    )
    territories["derniere_recherche"] = pd.to_datetime(
        territories["derniere_recherche"], errors="coerce"
    )

    # This date is the automated watch run, not a manually verified complete sweep.
    latest_signal = prospects["date_publication"].max()
    latest_manual_sweep = territories["derniere_recherche"].max()

    metadata = pd.DataFrame([
        ["version_application", "V5.2"],
        ["date_generation_utc", NOW_ISO],
        ["actualisation_automatique", "Hebdomadaire"],
        ["dernier_passage_automatique_utc", NOW_ISO],
        ["dernier_signal_publication", latest_signal.date().isoformat() if pd.notna(latest_signal) else ""],
        ["dernier_balayage_territorial", latest_manual_sweep.date().isoformat() if pd.notna(latest_manual_sweep) else ""],
        ["nombre_prospects", str(len(prospects))],
        ["nombre_signaux_a_qualifier", str(len(signals))],
        ["nouveaux_signaux_dernier_passage", str(new_signal_count)],
        ["erreurs_dernier_passage", str(len(errors))],
    ], columns=["cle", "valeur"])
    metadata.to_csv(METADATA, index=False, encoding="utf-8-sig")

    inventory = []
    for path in sorted(DATA.glob("*.csv")):
        try:
            frame = pd.read_csv(path)
            inventory.append([
                path.stem, path.name, len(frame), len(frame.columns),
                "OK", NOW_ISO
            ])
        except Exception as exc:
            inventory.append([
                path.stem, path.name, None, None,
                "Erreur", NOW_ISO
            ])
    pd.DataFrame(inventory, columns=[
        "jeu_donnees", "fichier", "enregistrements",
        "colonnes", "etat", "date_controle_utc"
    ]).to_csv(STATE, index=False, encoding="utf-8-sig")

def append_history(new_signals: int, added: int, modified: int, errors: list[str]) -> None:
    history = safe_read(HISTORY)
    row = pd.DataFrame([{
        "date_utc": NOW_ISO,
        "version": "V5.2",
        "type": "Veille hebdomadaire automatisée",
        "resultat": "Succès" if not errors else "Partiel",
        "nouveaux_prospects": added,
        "prospects_modifies": modified,
        "commentaire": (
            f"{new_signals} nouveau(x) signal(aux) à qualifier. "
            + ("; ".join(errors[:5]) if errors else "Aucune erreur.")
        ),
    }])
    pd.concat([history, row], ignore_index=True).to_csv(
        HISTORY, index=False, encoding="utf-8-sig"
    )

def run_sirene_connector() -> None:
    from collect_sirene import main as collect_sirene
    collect_sirene()

def main() -> None:
    run_sirene_connector()
    collected, errors = collect_signals()
    merged, new = merge_signals(collected)
    merged.to_csv(SIGNALS, index=False, encoding="utf-8-sig")
    new.to_csv(NEW_SIGNALS, index=False, encoding="utf-8-sig")

    consolidated = merged.copy()
    consolidated["prospect_id"] = ""
    consolidated["date_evenement"] = consolidated["date_publication"]
    consolidated["type_signal"] = consolidated["theme"].fillna("").str.lower().map(
        lambda x: "recrutement" if "recrut" in x else (
            "urbanisme" if "urbanisme" in x else "google_news"
        )
    )
    consolidated["source_id"] = "SRC-GNEWS"
    consolidated["confiance_signal_pct"] = 50
    consolidated["validation"] = "À qualifier"
    for col in [
        "signal_id","prospect_id","date_detection_utc","date_evenement",
        "territoire","zone","theme","type_signal","titre","source_id","source",
        "url","resume","requete","confiance_signal_pct","validation","est_nouveau"
    ]:
        if col not in consolidated.columns:
            consolidated[col] = ""
    consolidated[[
        "signal_id","prospect_id","date_detection_utc","date_evenement",
        "territoire","zone","theme","type_signal","titre","source_id","source",
        "url","resume","requete","confiance_signal_pct","validation","est_nouveau"
    ]].to_csv(CONSOLIDATED_SIGNALS, index=False, encoding="utf-8-sig")

    added, modified = prospect_changes()
    append_history(len(new), added, modified, errors)
    rebuild_status(len(new), errors)
    from rebuild_intelligence import rebuild as rebuild_intelligence
    rebuild_intelligence()

    print(
        f"Veille terminée: {len(new)} nouveaux signaux, "
        f"{added} nouveaux prospects, {len(errors)} erreurs."
    )

if __name__ == "__main__":
    main()
