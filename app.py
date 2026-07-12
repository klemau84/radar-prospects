from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "prospects_demo.csv"

STAGES = ["Projet annoncé", "Autorisation", "Travaux", "Recrutement", "Préouverture", "Ouvert", "Reprise", "À vérifier"]
HORIZONS = ["A — moins de 3 mois", "B — 3 à 6 mois", "C — plus de 6 mois", "D — date inconnue", "R — reprise / transformation"]


st.set_page_config(page_title="Radar CHR 06/83", page_icon="📡", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    [data-testid="stMetric"] {background:#f6f8f7;border:1px solid #e4e9e6;padding:14px;border-radius:12px;}
    .signal {background:#eef7f2;border-left:5px solid #147a4b;padding:12px 16px;border-radius:8px;margin-bottom:10px;}
    .muted {color:#5f6b66;font-size:.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_demo() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE, dtype={"departement": str})


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["date_publication", "date_ouverture_estimee"]:
        if col in out:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    out["departement"] = out["departement"].astype(str).str.replace(".0", "", regex=False).str.zfill(2)
    out["indice_confiance"] = pd.to_numeric(out["indice_confiance"], errors="coerce").fillna(0).astype(int)
    return out


if "prospects" not in st.session_state:
    st.session_state.prospects = prepare(load_demo())

df = st.session_state.prospects

st.title("Radar prospects boissons · 06 & 83")
st.caption("Détecter les ouvertures, reprises et nouveaux concepts avant leur présence dans les annuaires classiques.")

with st.sidebar:
    st.header("Filtres")
    departments = st.multiselect("Département", ["06", "83"], default=["06", "83"])
    selected_stages = st.multiselect("Stade", STAGES, default=STAGES)
    selected_horizons = st.multiselect("Horizon", HORIZONS, default=HORIZONS)
    min_confidence = st.slider("Confiance minimale", 0, 100, 40, 5)
    search = st.text_input("Recherche libre", placeholder="rooftop, Cannes, hôtel…")
    st.divider()
    st.caption("Pré-version · les lignes marquées DÉMO servent uniquement à valider le fonctionnement.")

filtered = df[
    df["departement"].isin(departments)
    & df["stade"].isin(selected_stages)
    & df["horizon"].isin(selected_horizons)
    & (df["indice_confiance"] >= min_confidence)
].copy()
if search:
    mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
    filtered = filtered[mask]

tab_dashboard, tab_radar, tab_import, tab_sources, tab_catalogue = st.tabs(
    ["Vue d’ensemble", "Radar", "Importer / ajouter", "Sources & requêtes", "Catalogue"]
)

with tab_dashboard:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Signaux visibles", len(filtered))
    c2.metric("Ouvertures < 3 mois", int((filtered["horizon"] == HORIZONS[0]).sum()))
    c3.metric("Reprises / transformations", int((filtered["horizon"] == HORIZONS[4]).sum()))
    c4.metric("Confiance moyenne", f"{filtered['indice_confiance'].mean():.0f}%" if len(filtered) else "—")

    st.subheader("À traiter en priorité")
    priority = filtered.sort_values(["indice_confiance", "date_publication"], ascending=[False, False]).head(6)
    if priority.empty:
        st.info("Aucun signal ne correspond aux filtres.")
    for _, row in priority.iterrows():
        opening = row["date_ouverture_estimee"]
        opening_text = opening.strftime("%d/%m/%Y") if pd.notna(opening) else "date inconnue"
        st.markdown(
            f"<div class='signal'><b>{row['etablissement']}</b> · {row['commune']} ({row['departement']})"
            f"<br>{row['type_concept']} — <b>{row['stade']}</b> — ouverture {opening_text}"
            f"<br><span class='muted'>{row['signal']} · confiance {row['indice_confiance']}%</span></div>",
            unsafe_allow_html=True,
        )

    left, right = st.columns(2)
    with left:
        st.subheader("Par stade")
        st.bar_chart(filtered["stade"].value_counts())
    with right:
        st.subheader("Par niche")
        st.bar_chart(filtered["niche"].value_counts().head(10))

with tab_radar:
    st.subheader("Signaux détectés")
    display_columns = [
        "etablissement", "commune", "departement", "type_concept", "niche", "stade", "horizon",
        "date_ouverture_estimee", "signal", "familles_produits", "indice_confiance", "source_url", "statut_donnee"
    ]
    shown = filtered[display_columns].sort_values(["indice_confiance", "date_publication"], ascending=[False, False])
    st.dataframe(
        shown,
        use_container_width=True,
        hide_index=True,
        column_config={
            "source_url": st.column_config.LinkColumn("Source"),
            "indice_confiance": st.column_config.ProgressColumn("Confiance", min_value=0, max_value=100, format="%d%%"),
            "date_ouverture_estimee": st.column_config.DateColumn("Ouverture estimée", format="DD/MM/YYYY"),
        },
    )
    st.download_button(
        "Télécharger la sélection CSV",
        data=shown.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"radar_prospects_{date.today().isoformat()}.csv",
        mime="text/csv",
    )

with tab_import:
    st.subheader("Importer des résultats de veille")
    st.write("Le CSV doit reprendre les colonnes du modèle. Les données importées restent en mémoire pendant la session.")
    template = df.head(0).to_csv(index=False).encode("utf-8-sig")
    st.download_button("Télécharger le modèle CSV", template, "modele_import_prospects.csv", "text/csv")
    uploaded = st.file_uploader("Importer un CSV", type=["csv"])
    if uploaded is not None:
        try:
            incoming = prepare(pd.read_csv(uploaded, dtype={"departement": str}))
            missing = set(df.columns) - set(incoming.columns)
            if missing:
                st.error("Colonnes manquantes : " + ", ".join(sorted(missing)))
            else:
                st.session_state.prospects = pd.concat([df, incoming[df.columns]], ignore_index=True)
                st.success(f"{len(incoming)} ligne(s) ajoutée(s). Rechargez la page pour actualiser les filtres.")
        except Exception as exc:
            st.error(f"Import impossible : {exc}")

    st.subheader("Ajouter un signal manuellement")
    with st.form("add_signal", clear_on_submit=True):
        a, b, c = st.columns(3)
        name = a.text_input("Établissement / projet *")
        city = b.text_input("Commune *")
        department = c.selectbox("Département", ["06", "83"])
        concept = a.text_input("Type de concept", placeholder="Boutique-hôtel, beach club…")
        niche = b.text_input("Niche", placeholder="Hôtellerie lifestyle")
        stage = c.selectbox("Stade", STAGES)
        horizon = a.selectbox("Horizon", HORIZONS)
        opening_date = b.date_input("Ouverture estimée", value=None)
        confidence = c.slider("Confiance", 0, 100, 50, 5)
        signal = st.text_area("Signal observé *", placeholder="Publication de recrutement pour l’équipe d’ouverture…")
        products = st.text_input("Familles pertinentes", placeholder="Champagne | spiritueux | mixers")
        source = st.text_input("URL source *")
        submitted = st.form_submit_button("Ajouter au radar", type="primary")
        if submitted:
            if not name or not city or not signal or not source:
                st.error("Renseignez les champs marqués d’un astérisque.")
            else:
                row = {col: "" for col in df.columns}
                row.update({
                    "etablissement": name, "commune": city, "departement": department,
                    "type_concept": concept, "niche": niche, "stade": stage, "horizon": horizon,
                    "date_ouverture_estimee": pd.Timestamp(opening_date) if opening_date else pd.NaT,
                    "date_publication": pd.Timestamp(datetime.now()), "signal": signal,
                    "familles_produits": products, "indice_confiance": confidence,
                    "source_url": source, "statut_donnee": "SAISI MANUELLEMENT"
                })
                st.session_state.prospects = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                st.success("Signal ajouté.")

with tab_sources:
    st.subheader("Canaux de détection")
    sources = pd.DataFrame([
        ["Presse locale et professionnelle", "Projet, ouverture, reprise, rénovation", "Quotidienne"],
        ["RNE / SIRENE / BODACC", "Création, établissement secondaire, cession de fonds", "Hebdomadaire"],
        ["Mairies, CDAC, concessions", "Urbanisme, plages, ports, locaux commerciaux", "Hebdomadaire"],
        ["LinkedIn et sites de recrutement", "Équipe d'ouverture, directeur, F&B, bar", "Quotidienne"],
        ["Instagram / Facebook", "Travaux, préouverture, lancement de saison", "Quotidienne"],
        ["Architectes et agenceurs CHR", "Projets avant communication officielle", "Hebdomadaire"],
        ["Transactions de fonds", "Reprise, location-gérance, changement d'exploitant", "Hebdomadaire"],
    ], columns=["Canal", "Signal", "Rythme conseillé"])
    st.dataframe(sources, use_container_width=True, hide_index=True)

    st.subheader("Bibliothèque de requêtes")
    cities = ["Nice", "Cannes", "Antibes", "Menton", "Grasse", "Toulon", "Hyères", "Fréjus", "Saint-Raphaël", "Saint-Tropez", "Draguignan"]
    patterns = [
        '"ouverture prochaine" restaurant {ville}',
        '"recrute pour son ouverture" bar {ville}',
        '"nouveau rooftop" {ville}',
        '"réouverture" hôtel {ville}',
        '"nouveau beach club" {ville}',
        '"changement de propriétaire" restaurant {ville}',
        '"nouveau complexe de padel" {ville}',
        '"appel à manifestation d’intérêt" restaurant {ville}',
    ]
    selected_city = st.selectbox("Commune", cities)
    queries = [pattern.format(ville=selected_city) for pattern in patterns]
    st.code("\n".join(queries), language=None)

with tab_catalogue:
    st.subheader("Familles à détecter dans les concepts")
    catalogue = pd.DataFrame([
        ["Cocktails / nightlife", "Spiritueux, liqueurs, sirops, jus, tonics, énergisants"],
        ["Petit-déjeuner", "Café, thé, jus, eaux"],
        ["Plage / piscine", "Eaux, softs, bières, rosés, cocktails"],
        ["Événementiel", "Champagnes, vins, spiritueux, eaux, softs, café"],
        ["Bière pression", "Fûts, bières bouteilles et sans alcool"],
        ["Premium international", "Champagnes, spiritueux premium, vins, eaux premium"],
        ["No/low alcohol", "Bières 0,0 %, jus, sirops, tonics et eaux"],
    ], columns=["Usage détecté", "Familles du catalogue"])
    st.dataframe(catalogue, use_container_width=True, hide_index=True)
    st.info("La pré-version utilise les familles identifiées dans la liste de 1 378 articles. Elle n’effectue aucun calcul de rentabilité.")
