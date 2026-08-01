
from __future__ import annotations
from pathlib import Path
from difflib import SequenceMatcher
import re
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"

def norm(value) -> str:
    value = str(value or "").lower()
    value = re.sub(r"[^a-z0-9àâäéèêëîïôöùûüç ]+", " ", value)
    return " ".join(value.split())

def similarity(a, b) -> float:
    return SequenceMatcher(None, norm(a), norm(b)).ratio()

def priority(score: int) -> str:
    if score >= 300:
        return "Urgent"
    if score >= 200:
        return "Prioritaire"
    if score >= 100:
        return "Intéressant"
    return "Veille"

def rebuild() -> None:
    prospects = pd.read_csv(DATA / "prospects.csv", dtype={"departement": str})
    signals = pd.read_csv(DATA / "signaux.csv", dtype={"territoire": str})
    rules = pd.read_csv(DATA / "scoring_rules.csv")
    points_map = rules[rules["actif"] == 1].set_index("type_signal")["points"].to_dict()

    if "prospect_id" not in prospects.columns:
        prospects["prospect_id"] = [f"P-{i+1:04d}" for i in range(len(prospects))]

    score_rows = []
    for _, prospect in prospects.iterrows():
        subset = signals[signals["prospect_id"] == prospect["prospect_id"]]
        points = int(subset["type_signal"].map(points_map).fillna(0).sum())
        confidence = int(pd.to_numeric(
            pd.Series([prospect.get("indice_confiance", 0)]),
            errors="coerce"
        ).fillna(0).iloc[0])
        total = min(500, points + round(confidence * 1.5) + 20)
        score_rows.append([
            prospect["prospect_id"], prospect["etablissement"],
            prospect["commune"], prospect["departement"], total,
            min(99, round(total / 5)), priority(total),
            subset["signal_id"].nunique(), subset["source_id"].nunique(),
            subset["date_evenement"].max() if not subset.empty else prospect.get("date_publication",""),
            "Score configurable"
        ])

    scores = pd.DataFrame(score_rows, columns=[
        "prospect_id","etablissement","commune","departement","score_total",
        "probabilite_ouverture_pct","priorite","nombre_signaux","nombre_sources",
        "derniere_activite","methode_calcul"
    ])
    scores.to_csv(DATA / "scores.csv", index=False, encoding="utf-8-sig")
    scores.sort_values("score_total", ascending=False).assign(
        ordre_traitement=lambda d: range(1, len(d)+1)
    ).to_csv(DATA / "priorites.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    rebuild()
