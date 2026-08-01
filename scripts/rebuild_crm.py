
from __future__ import annotations
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"

def rebuild() -> None:
    prospects = pd.read_csv(DATA / "prospects.csv", dtype={"departement": str})
    scores = pd.read_csv(DATA / "scores.csv", dtype={"departement": str})
    signals = pd.read_csv(DATA / "signaux.csv", dtype={"territoire": str})
    actions = pd.read_csv(DATA / "actions_commerciales.csv")
    contacts = pd.read_csv(DATA / "contacts.csv")

    result = prospects.merge(
        scores,
        on=["prospect_id","etablissement","commune","departement"],
        how="left"
    )

    if signals.empty:
        signal_summary = pd.DataFrame(columns=[
            "prospect_id","signaux_total","types_signaux",
            "sources_signaux","derniere_detection"
        ])
    else:
        signal_summary = signals.groupby("prospect_id", as_index=False).agg(
            signaux_total=("signal_id","nunique"),
            types_signaux=("type_signal", lambda s: ", ".join(sorted(set(map(str, s.dropna()))))),
            sources_signaux=("source", lambda s: ", ".join(sorted(set(map(str, s.dropna()))))),
            derniere_detection=("date_evenement","max"),
        )

    result = result.merge(signal_summary, on="prospect_id", how="left")
    result["signaux_total"] = result["signaux_total"].fillna(0).astype(int)
    result["types_signaux"] = result["types_signaux"].fillna("")
    result["sources_signaux"] = result["sources_signaux"].fillna("")

    if actions.empty:
        action_summary = pd.DataFrame(columns=[
            "prospect_id","actions_realisees","derniere_action",
            "prochaine_relance","statut_commercial"
        ])
    else:
        actions["date_action"] = pd.to_datetime(actions["date_action"], errors="coerce")
        actions["prochaine_relance"] = pd.to_datetime(actions["prochaine_relance"], errors="coerce")
        action_summary = actions.sort_values("date_action").groupby("prospect_id", as_index=False).agg(
            actions_realisees=("action_id","count"),
            derniere_action=("date_action","max"),
            prochaine_relance=("prochaine_relance","max"),
            statut_commercial=("statut","last"),
        )

    result = result.merge(action_summary, on="prospect_id", how="left")
    result["actions_realisees"] = result["actions_realisees"].fillna(0).astype(int)
    result["statut_commercial"] = result["statut_commercial"].fillna("Non contacté")

    def action(row):
        if row.get("priorite") == "Urgent":
            return "Qualifier sous 48 h et identifier le décideur"
        if row.get("priorite") == "Prioritaire":
            return "Contacter cette semaine"
        if row.get("stade") != "Ouvert":
            return "Surveiller le calendrier d'ouverture"
        return "Veille mensuelle"

    result["action_recommandee"] = result.apply(action, axis=1)
    result.to_csv(DATA / "prospects_360.csv", index=False, encoding="utf-8-sig")

    board = result[[
        "prospect_id","etablissement","commune","departement","stade",
        "score_total","probabilite_ouverture_pct","priorite","signaux_total",
        "derniere_detection","statut_commercial","action_recommandee"
    ]].copy()

    order = {"Urgent":1,"Prioritaire":2,"Intéressant":3,"Veille":4}
    board["ordre_priorite"] = board["priorite"].map(order).fillna(9)
    board = board.sort_values(
        ["ordre_priorite","score_total","derniere_detection"],
        ascending=[True,False,False]
    )
    board["ordre_traitement"] = range(1, len(board)+1)
    board.to_csv(DATA / "a_traiter.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    rebuild()
