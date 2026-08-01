
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path
import json, time
import pandas as pd
import requests

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
API = "https://recherche-entreprises.api.gouv.fr/search"
NAF_FILE = DATA / "naf_chr.csv"
OUTPUT = DATA / "signaux_sirene.csv"
NEW_OUTPUT = DATA / "nouveaux_signaux_sirene.csv"

NOW = datetime.now(timezone.utc).replace(microsecond=0)
NOW_ISO = NOW.isoformat().replace("+00:00", "Z")
LOOKBACK_DAYS = 45
DEPARTMENTS = ["06", "83"]

def safe_read(path):
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna("")

def parse_results(payload, department, naf_code, naf_label):
    rows = []
    for company in payload.get("results", []):
        siege = company.get("siege") or {}
        establishments = company.get("matching_etablissements") or []
        if not establishments and siege:
            establishments = [siege]
        for e in establishments:
            creation = e.get("date_creation") or company.get("date_creation") or ""
            try:
                created = datetime.fromisoformat(str(creation)[:10]).date()
            except Exception:
                continue
            if created < NOW.date() - timedelta(days=LOOKBACK_DAYS):
                continue
            siret = str(e.get("siret") or siege.get("siret") or "")
            siren = str(company.get("siren") or "")
            signal_id = sha256(f"SIRENE|{siret}|{creation}".encode()).hexdigest()[:20]
            rows.append({
                "signal_id": signal_id,
                "date_detection_utc": NOW_ISO,
                "date_creation": str(creation)[:10],
                "siren": siren,
                "siret": siret,
                "nom_entreprise": company.get("nom_complet") or company.get("nom_raison_sociale") or "",
                "nom_commercial": e.get("nom_commercial") or siege.get("nom_commercial") or "",
                "code_naf": naf_code,
                "libelle_naf": naf_label,
                "adresse": e.get("adresse") or siege.get("adresse") or "",
                "code_postal": str(e.get("code_postal") or siege.get("code_postal") or ""),
                "commune": e.get("commune") or siege.get("commune") or "",
                "departement": department,
                "url_annuaire": f"https://annuaire-entreprises.data.gouv.fr/entreprise/{siren}" if siren else "",
                "type_signal": "creation_entreprise",
                "source_id": "SRC-SIRENE",
                "source": "API Recherche d'entreprises / SIRENE",
                "validation": "À qualifier",
            })
    return rows

def main():
    rules = pd.read_csv(NAF_FILE)
    rules = rules[rules["actif"] == 1]
    previous = safe_read(OUTPUT)
    previous_ids = set(previous.get("signal_id", pd.Series(dtype=str)))
    collected, errors = [], []

    session = requests.Session()
    session.headers.update({"User-Agent": "RadarCHR/7.2a"})

    for department in DEPARTMENTS:
        for row in rules.itertuples(index=False):
            try:
                params = {
                    "q": "",
                    "code_postal": department,
                    "code_naf": row.code_naf,
                    "page": 1,
                    "per_page": 25,
                }
                response = session.get(API, params=params, timeout=45)
                response.raise_for_status()
                collected.extend(parse_results(response.json(), department, row.code_naf, row.libelle))
            except Exception as exc:
                errors.append(f"{department}/{row.code_naf}: {exc}")
            time.sleep(0.18)

    frame = pd.DataFrame(collected)
    if frame.empty:
        frame = pd.DataFrame(columns=[c for c in [
            "signal_id","date_detection_utc","date_creation","siren","siret",
            "nom_entreprise","nom_commercial","code_naf","libelle_naf",
            "adresse","code_postal","commune","departement","url_annuaire",
            "type_signal","source_id","source","validation"
        ]])
    frame = frame.drop_duplicates("signal_id")
    frame["est_nouveau"] = ~frame["signal_id"].isin(previous_ids)
    new = frame[frame["est_nouveau"]].copy()

    if previous.empty:
        merged = frame
    else:
        previous["est_nouveau"] = False
        merged = pd.concat([frame, previous], ignore_index=True).drop_duplicates("signal_id", keep="first")

    merged.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    new.to_csv(NEW_OUTPUT, index=False, encoding="utf-8-sig")
    status = {
        "date_utc": NOW_ISO,
        "source": "SIRENE",
        "nouveaux_signaux": len(new),
        "total_signaux": len(merged),
        "erreurs": errors,
    }
    (DATA / "statut_sirene.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))

if __name__ == "__main__":
    main()
