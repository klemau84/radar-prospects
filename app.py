from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "prospects.csv"
CONTACTS_FILE = ROOT / "data" / "contacts.csv"
PRODUCT_FILE = ROOT / "data" / "opportunites_produits.csv"
TERRITORY_FILE = ROOT / "data" / "territoires.csv"
METADATA_FILE = ROOT / "data" / "metadonnees_application.csv"
DATA_STATUS_FILE = ROOT / "data" / "etat_donnees.csv"
ZONE_STATUS_FILE = ROOT / "data" / "etat_zones.csv"
LATEST_FILE = ROOT / "data" / "dernieres_nouveautes.csv"
UPDATE_HISTORY_FILE = ROOT / "data" / "historique_mises_a_jour.csv"
WEEKLY_SIGNALS_FILE = ROOT / "data" / "signaux_hebdo.csv"
NEW_SIGNALS_FILE = ROOT / "data" / "nouveaux_signaux.csv"
SCORES_FILE = ROOT / "data" / "scores.csv"
PRIORITIES_FILE = ROOT / "data" / "priorites.csv"
HISTORY_SIGNALS_FILE = ROOT / "data" / "historique_signaux.csv"
FUSION_FILE = ROOT / "data" / "fusion_prospects.csv"
SCORING_RULES_FILE = ROOT / "data" / "scoring_rules.csv"
SIRENE_SIGNALS_FILE = ROOT / "data" / "signaux_sirene.csv"
SIRENE_NEW_FILE = ROOT / "data" / "nouveaux_signaux_sirene.csv"
NAF_CHR_FILE = ROOT / "data" / "naf_chr.csv"
DATA_VERSION = "7.3.0"

STAGES = ["Projet annoncé", "Autorisation", "Travaux", "Recrutement", "Préouverture", "Ouvert", "Reprise", "À vérifier"]
HORIZONS = ["A — moins de 3 mois", "B — 3 à 6 mois", "C — plus de 6 mois", "D — date inconnue", "E — ouvert récemment", "R — reprise / transformation"]


st.set_page_config(page_title="Radar CHR 06/83/Monaco", page_icon="📡", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    [data-testid="stMetric"] {
        background:rgba(127,127,127,.10);
        border:1px solid rgba(127,127,127,.28);
        padding:14px;
        border-radius:12px;
    }
    [data-testid="stMetric"] * {color:inherit !important;}
    .signal {
        background:rgba(20,122,75,.14);
        border:1px solid rgba(20,122,75,.35);
        border-left:5px solid #2da66a;
        color:inherit;
        padding:12px 16px;
        border-radius:8px;
        margin-bottom:10px;
    }
    .signal b {color:inherit;}
    .muted {color:inherit;opacity:.78;font-size:.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def load_prospects() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE, dtype={"departement": str})

def load_contacts() -> pd.DataFrame:
    columns = [
        "contact_id", "prospect_id", "etablissement", "contact_nom", "fonction",
        "organisation", "telephone", "email", "type_contact", "source_url",
        "date_verification", "niveau_fiabilite", "notes",
    ]
    if not CONTACTS_FILE.exists():
        return pd.DataFrame(columns=columns)
    contacts = pd.read_csv(CONTACTS_FILE, dtype=str).fillna("")
    for column in columns:
        if column not in contacts.columns:
            contacts[column] = ""
    return contacts[columns]

def load_product_opportunities() -> pd.DataFrame:
    return pd.read_csv(PRODUCT_FILE)

def load_territories() -> pd.DataFrame:
    return pd.read_csv(TERRITORY_FILE, dtype={"territoire": str})

def load_metadata() -> pd.DataFrame:
    return pd.read_csv(METADATA_FILE)

def load_data_status() -> pd.DataFrame:
    return pd.read_csv(DATA_STATUS_FILE)

def load_zone_status() -> pd.DataFrame:
    return pd.read_csv(ZONE_STATUS_FILE, dtype={"territoire": str})

def load_latest_signals() -> pd.DataFrame:
    return pd.read_csv(LATEST_FILE, dtype={"departement": str})

def load_update_history() -> pd.DataFrame:
    return pd.read_csv(UPDATE_HISTORY_FILE)

def load_weekly_signals() -> pd.DataFrame:
    return pd.read_csv(WEEKLY_SIGNALS_FILE, dtype={"territoire": str})

def load_new_signals() -> pd.DataFrame:
    return pd.read_csv(NEW_SIGNALS_FILE, dtype={"territoire": str})

def load_scores() -> pd.DataFrame:
    return pd.read_csv(SCORES_FILE, dtype={"departement": str})

def load_priorities() -> pd.DataFrame:
    return pd.read_csv(PRIORITIES_FILE, dtype={"departement": str})

def load_signal_history() -> pd.DataFrame:
    return pd.read_csv(HISTORY_SIGNALS_FILE)

def load_fusion_proposals() -> pd.DataFrame:
    return pd.read_csv(FUSION_FILE)

def load_scoring_rules() -> pd.DataFrame:
    return pd.read_csv(SCORING_RULES_FILE)

def load_sirene_signals() -> pd.DataFrame:
    return pd.read_csv(SIRENE_SIGNALS_FILE, dtype=str).fillna("")

def load_sirene_new() -> pd.DataFrame:
    return pd.read_csv(SIRENE_NEW_FILE, dtype=str).fillna("")

def load_naf_chr() -> pd.DataFrame:
    return pd.read_csv(NAF_CHR_FILE)


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["date_publication", "date_ouverture_estimee"]:
        if col in out:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    out["departement"] = out["departement"].astype(str).str.replace(".0", "", regex=False).str.zfill(2)
    out["indice_confiance"] = pd.to_numeric(out["indice_confiance"], errors="coerce").fillna(0).astype(int)
    return out


if st.session_state.get("data_version") != DATA_VERSION:
    st.session_state.prospects = prepare(load_prospects())
    st.session_state.contacts = load_contacts()
    st.session_state.product_opportunities = load_product_opportunities()
    st.session_state.territories = load_territories()
    st.session_state.metadata = load_metadata()
    st.session_state.data_status = load_data_status()
    st.session_state.zone_status = load_zone_status()
    st.session_state.latest_signals = load_latest_signals()
    st.session_state.update_history = load_update_history()
    st.session_state.weekly_signals = load_weekly_signals()
    st.session_state.new_signals = load_new_signals()
    st.session_state.scores = load_scores()
    st.session_state.priorities = load_priorities()
    st.session_state.signal_history = load_signal_history()
    st.session_state.fusion_proposals = load_fusion_proposals()
    st.session_state.scoring_rules = load_scoring_rules()
    st.session_state.sirene_signals = load_sirene_signals()
    st.session_state.sirene_new = load_sirene_new()
    st.session_state.naf_chr = load_naf_chr()
    st.session_state.data_version = DATA_VERSION

df = st.session_state.prospects
contacts_df = st.session_state.contacts
products_df = st.session_state.product_opportunities
territories_df = st.session_state.territories
metadata_df = st.session_state.metadata
data_status_df = st.session_state.data_status
zone_status_df = st.session_state.zone_status
latest_signals_df = st.session_state.latest_signals
update_history_df = st.session_state.update_history
weekly_signals_df = st.session_state.weekly_signals
new_signals_df = st.session_state.new_signals
scores_df = st.session_state.scores
priorities_df = st.session_state.priorities
signal_history_df = st.session_state.signal_history
fusion_proposals_df = st.session_state.fusion_proposals
scoring_rules_df = st.session_state.scoring_rules
sirene_signals_df = st.session_state.sirene_signals
sirene_new_df = st.session_state.sirene_new
naf_chr_df = st.session_state.naf_chr
metadata_map = dict(zip(metadata_df["cle"], metadata_df["valeur"])) if not metadata_df.empty else {}

st.title("Radar prospects boissons · 06, 83 & Monaco")
st.caption("Détecter les ouvertures, reprises et nouveaux concepts avant leur présence dans les annuaires classiques.")

with st.container(border=True):
    u1, u2, u3, u4 = st.columns(4)
    u1.metric("Version des données", metadata_map.get("version_application", "V5.1"))
    u2.metric("Dernier signal intégré", metadata_map.get("dernier_signal_publication", "N/D"))
    u3.metric("Dernier balayage", metadata_map.get("dernier_balayage_territorial", "N/D"))
    u4.metric("Veille automatique", metadata_map.get("actualisation_automatique", "Hebdomadaire"))
    st.caption(
        "La veille GitHub Actions recherche de nouveaux signaux chaque lundi. "
        "Ces signaux restent à qualifier avant d'entrer dans la base des prospects."
    )

with st.sidebar:
    st.header("Filtres")
    departments = st.multiselect("Territoire", ["06", "83", "MC"], default=["06", "83", "MC"])
    selected_stages = st.multiselect("Stade", STAGES, default=[s for s in STAGES if s != "Ouvert"])
    selected_horizons = st.multiselect("Horizon", HORIZONS, default=HORIZONS)
    min_confidence = st.slider("Confiance minimale", 0, 100, 40, 5)
    contact_only = st.checkbox("Avec contact identifié uniquement", value=False)
    search = st.text_input("Recherche libre", placeholder="rooftop, Cannes, hôtel…")
    st.divider()
    st.caption("V7.3 · contacts publics sourcés, créations SIRENE et veille hebdomadaire.")

filtered = df[
    df["departement"].isin(departments)
    & df["stade"].isin(selected_stages)
    & df["horizon"].isin(selected_horizons)
    & (df["indice_confiance"] >= min_confidence)
].copy()
if contact_only:
    filtered = filtered[filtered["prospect_id"].isin(set(contacts_df["prospect_id"]))]
if search:
    mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
    contact_matches = set(
        contacts_df.loc[
            contacts_df.astype(str).apply(
                lambda col: col.str.contains(search, case=False, na=False)
            ).any(axis=1),
            "prospect_id",
        ]
    )
    filtered = filtered[mask | filtered["prospect_id"].isin(contact_matches)]

tab_dashboard, tab_radar, tab_priority, tab_contacts, tab_intelligence, tab_sirene, tab_coverage, tab_products, tab_archive, tab_import, tab_signals, tab_status, tab_sources, tab_catalogue = st.tabs(
    ["Avant ouverture", "Projets", "À traiter", "Contacts", "Intelligence", "Créations SIRENE", "Couverture territoriale", "Opportunités produits", "Ouverts / archive", "Importer / ajouter", "Signaux hebdo", "État des données", "Sources & requêtes", "Tendances & catalogue"]
)

with tab_dashboard:
    st.subheader("Dernières données intégrées")
    recent = latest_signals_df.head(5).copy()
    if recent.empty:
        st.info("Aucune nouveauté enregistrée.")
    else:
        for _, row in recent.iterrows():
            st.markdown(
                f"<div class='signal'><b>{row['etablissement']}</b> · "
                f"{row['commune']} ({row['departement']})"
                f"<br>{row['type_concept']} — <b>{row['stade']}</b>"
                f"<br><span class='muted'>Publication {row['date_publication']} · "
                f"confiance {row['indice_confiance']}%</span></div>",
                unsafe_allow_html=True,
            )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Projets visibles", len(filtered))
    c2.metric("Ouvertures < 3 mois", int((filtered["horizon"] == HORIZONS[0]).sum()))
    c3.metric("En travaux / recrutement", int(filtered["stade"].isin(["Travaux", "Recrutement", "Préouverture"]).sum()))
    c4.metric("Confiance moyenne", f"{filtered['indice_confiance'].mean():.0f}%" if len(filtered) else "—")
    c5.metric("Avec contact", int(filtered["prospect_id"].isin(set(contacts_df["prospect_id"])).sum()))

    st.subheader("À traiter en priorité")
    priority = filtered.sort_values(["indice_confiance", "date_publication"], ascending=[False, False]).head(6)
    if priority.empty:
        st.info("Aucun signal ne correspond aux filtres.")
    for _, row in priority.iterrows():
        opening = row["date_ouverture_estimee"]
        opening_text = opening.strftime("%d/%m/%Y") if pd.notna(opening) else "date inconnue"
        project_contacts = contacts_df[contacts_df["prospect_id"] == row["prospect_id"]]
        contact_text = ""
        if not project_contacts.empty:
            contact = project_contacts.iloc[0]
            identity = contact["contact_nom"] or contact["fonction"] or contact["organisation"]
            details = " · ".join(value for value in [contact["telephone"], contact["email"]] if value)
            contact_text = f"<br><span class='muted'>Contact : {identity}{' · ' + details if details else ''}</span>"
        st.markdown(
            f"<div class='signal'><b>{row['etablissement']}</b> · {row['commune']} ({row['departement']})"
            f"<br>{row['type_concept']} — <b>{row['stade']}</b> — ouverture {opening_text}"
            f"<br><span class='muted'>{row['signal']} · confiance {row['indice_confiance']}%</span>"
            f"{contact_text}</div>",
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
    st.subheader("Projets avant ouverture")
    primary_contacts = contacts_df.drop_duplicates("prospect_id")[
        ["prospect_id", "contact_nom", "fonction", "telephone", "email"]
    ].rename(columns={"fonction": "fonction_contact"})
    display_columns = [
        "etablissement", "commune", "departement", "type_concept", "niche", "stade", "horizon",
        "date_ouverture_estimee", "contact_nom", "fonction_contact", "telephone", "email",
        "signal", "familles_produits", "indice_confiance", "source_url", "statut_donnee"
    ]
    shown = filtered.merge(primary_contacts, on="prospect_id", how="left").sort_values(
        ["indice_confiance", "date_publication"], ascending=[False, False]
    )[display_columns]
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

with tab_products:
    st.subheader("Potentiel de nouvelles gammes")
    st.caption("Les marges sont des hypothèses comparatives, pas des marges constatées. Elles devront être remplacées par les devis fournisseurs.")
    editable_columns = ["famille", "segments_cibles", "demande_score", "marge_score", "mutualisation_score", "effort_referencement", "risque_stock", "minimum_achat", "conservation", "statut_hypothese"]
    edited = st.data_editor(
        products_df[editable_columns], use_container_width=True, hide_index=True, num_rows="fixed",
        column_config={
            "demande_score": st.column_config.NumberColumn("Demande /5", min_value=1, max_value=5, step=1),
            "marge_score": st.column_config.NumberColumn("Marge probable /5", min_value=1, max_value=5, step=1),
            "mutualisation_score": st.column_config.NumberColumn("Multi-segments /5", min_value=1, max_value=5, step=1),
            "effort_referencement": st.column_config.NumberColumn("Effort /5", min_value=1, max_value=5, step=1),
            "risque_stock": st.column_config.NumberColumn("Risque stock /5", min_value=1, max_value=5, step=1),
        }, key="product_editor",
    )
    scored = edited.copy()
    scored["score_opportunite"] = (scored["demande_score"] * scored["marge_score"] * scored["mutualisation_score"] / (scored["effort_referencement"] * scored["risque_stock"])).round(1)
    scored["decision"] = pd.cut(scored["score_opportunite"], bins=[-1, 4, 10, float("inf")], labels=["Veille", "Test pilote", "Prioritaire"]).astype(str)
    p1, p2, p3 = st.columns(3)
    p1.metric("Gammes étudiées", len(scored))
    p2.metric("Prioritaires", int((scored["decision"] == "Prioritaire").sum()))
    p3.metric("Tests pilotes", int((scored["decision"] == "Test pilote").sum()))
    ranking = scored.sort_values("score_opportunite", ascending=False)
    st.dataframe(ranking[["famille", "segments_cibles", "score_opportunite", "decision", "minimum_achat", "conservation", "statut_hypothese"]], use_container_width=True, hide_index=True)
    st.download_button("Télécharger l'arbitrage produits", ranking.to_csv(index=False).encode("utf-8-sig"), "arbitrage_nouvelles_gammes.csv", "text/csv")
    with st.expander("Comment l'indice est calculé"):
        st.code("(Demande × Marge probable × Mutualisation) / (Effort de référencement × Risque de stock)")
        st.write("Cet indice compare les gammes entre elles. Ce n'est ni un taux de marge ni un chiffre d'affaires prévisionnel.")


with tab_priority:
    st.subheader("Priorités commerciales calculées")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Urgents", int((priorities_df["priorite"] == "Urgent").sum()))
    p2.metric("Prioritaires", int((priorities_df["priorite"] == "Prioritaire").sum()))
    p3.metric("Intéressants", int((priorities_df["priorite"] == "Intéressant").sum()))
    p4.metric("Veille", int((priorities_df["priorite"] == "Veille").sum()))
    st.dataframe(
        priorities_df[
            ["ordre_traitement","etablissement","commune","departement",
             "score_total","probabilite_ouverture_pct","priorite",
             "nombre_signaux","nombre_sources","derniere_activite"]
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "Le score sert à ordonner le travail commercial. "
        "La probabilité affichée est un indicateur interne, pas une probabilité statistique."
    )

with tab_contacts:
    st.subheader("Contacts publics associés aux prospects")
    st.caption(
        "Coordonnées professionnelles trouvées dans des sources publiques. "
        "Le niveau de fiabilité porte sur la coordonnée, pas sur le pouvoir de décision achats."
    )

    projects_with_contacts = set(contacts_df["prospect_id"])
    preopening = df[df["stade"] != "Ouvert"].copy()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Projets avec contact", preopening["prospect_id"].isin(projects_with_contacts).sum())
    k2.metric("Personnes nommées", int(contacts_df["contact_nom"].ne("").sum()))
    k3.metric("Téléphones", int(contacts_df["telephone"].ne("").sum()))
    k4.metric("E-mails", int(contacts_df["email"].ne("").sum()))

    f1, f2 = st.columns(2)
    contact_types = f1.multiselect(
        "Type de contact",
        sorted(value for value in contacts_df["type_contact"].unique() if value),
    )
    reliability = f2.multiselect(
        "Fiabilité",
        sorted(value for value in contacts_df["niveau_fiabilite"].unique() if value),
    )
    contact_view = contacts_df.copy()
    if contact_types:
        contact_view = contact_view[contact_view["type_contact"].isin(contact_types)]
    if reliability:
        contact_view = contact_view[contact_view["niveau_fiabilite"].isin(reliability)]

    st.dataframe(
        contact_view[
            ["etablissement", "contact_nom", "fonction", "organisation", "telephone",
             "email", "type_contact", "niveau_fiabilite", "date_verification",
             "source_url", "notes"]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={"source_url": st.column_config.LinkColumn("Source")},
    )
    st.download_button(
        "Télécharger les contacts CSV",
        contact_view.to_csv(index=False).encode("utf-8-sig"),
        f"contacts_prospects_{date.today().isoformat()}.csv",
        "text/csv",
    )

    st.subheader("Contacts restant à identifier")
    missing_contacts = preopening[~preopening["prospect_id"].isin(projects_with_contacts)]
    st.dataframe(
        missing_contacts[["prospect_id", "etablissement", "commune", "departement", "stade"]],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Ajouter un contact pendant cette session"):
        st.info(
            "L'ajout reste dans la session Streamlit. Téléchargez ensuite le CSV pour "
            "remplacer data/contacts.csv dans GitHub."
        )
        project_options = {
            f"{row.etablissement} · {row.commune} ({row.departement})": row.prospect_id
            for row in df.itertuples()
        }
        with st.form("add_contact", clear_on_submit=True):
            project_label = st.selectbox("Prospect *", list(project_options))
            a, b = st.columns(2)
            contact_name = a.text_input("Nom du contact")
            contact_role = b.text_input("Fonction")
            organisation = a.text_input("Organisation")
            phone = b.text_input("Téléphone")
            email = a.text_input("E-mail")
            contact_type = b.text_input("Type de contact", placeholder="Direction, groupe, autorité projet…")
            contact_source = st.text_input("URL de la source publique *")
            contact_reliability = a.selectbox("Fiabilité", ["Élevée", "Moyenne", "Faible"])
            contact_note = st.text_area("Notes")
            add_contact = st.form_submit_button("Ajouter le contact", type="primary")
            if add_contact:
                if not contact_source or not any([contact_name, phone, email]):
                    st.error("Ajoutez une source et au moins un nom, un téléphone ou un e-mail.")
                else:
                    prospect_id = project_options[project_label]
                    project = df[df["prospect_id"] == prospect_id].iloc[0]
                    numeric_ids = pd.to_numeric(
                        contacts_df["contact_id"].str.extract(r"(\d+)", expand=False),
                        errors="coerce",
                    )
                    next_number = int(numeric_ids.max()) + 1 if numeric_ids.notna().any() else 1
                    new_contact = {
                        "contact_id": f"C-{next_number:04d}",
                        "prospect_id": prospect_id,
                        "etablissement": project["etablissement"],
                        "contact_nom": contact_name,
                        "fonction": contact_role,
                        "organisation": organisation,
                        "telephone": phone,
                        "email": email,
                        "type_contact": contact_type,
                        "source_url": contact_source,
                        "date_verification": date.today().isoformat(),
                        "niveau_fiabilite": contact_reliability,
                        "notes": contact_note,
                    }
                    st.session_state.contacts = pd.concat(
                        [contacts_df, pd.DataFrame([new_contact])], ignore_index=True
                    )
                    st.success("Contact ajouté à la session.")

with tab_intelligence:
    st.subheader("Règles de scoring")
    st.dataframe(
        scoring_rules_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Propositions de fusion")
    if fusion_proposals_df.empty:
        st.info("Aucune proposition de fusion.")
    else:
        st.dataframe(
            fusion_proposals_df.sort_values("score_rapprochement_pct", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Historique consolidé des signaux")
    st.dataframe(
        signal_history_df.sort_values("date_evenement", ascending=False),
        use_container_width=True,
        hide_index=True,
    )


with tab_sirene:
    st.subheader("Créations CHR détectées via SIRENE")
    s1, s2, s3 = st.columns(3)
    s1.metric("Nouveautés du dernier passage", len(sirene_new_df))
    s2.metric("Signaux conservés", len(sirene_signals_df))
    s3.metric("Codes NAF surveillés", int((naf_chr_df["actif"] == 1).sum()))
    st.warning(
        "Une création juridique ne prouve pas une ouverture commerciale immédiate. "
        "Chaque ligne reste à qualifier."
    )
    if sirene_new_df.empty:
        st.info("Lance le workflow GitHub Actions pour effectuer le premier passage SIRENE.")
    else:
        st.dataframe(
            sirene_new_df[
                ["date_creation","nom_entreprise","nom_commercial","code_naf",
                 "libelle_naf","commune","departement","adresse",
                 "url_annuaire","validation"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    st.subheader("Tous les signaux SIRENE")
    st.dataframe(sirene_signals_df, use_container_width=True, hide_index=True)
    st.subheader("Activités surveillées")
    st.dataframe(naf_chr_df, use_container_width=True, hide_index=True)

with tab_coverage:
    st.subheader("Couverture géographique · 06, 83 et Monaco")
    st.caption("Une commune sans résultat n'est considérée comme couverte que si une recherche structurée y a réellement été exécutée.")
    cov = territories_df[territories_df["territoire"].isin(departments)].copy()
    observed = df.groupby(["departement", "commune"]).size().rename("prospects_detectes").reset_index()
    cov = cov.merge(observed, how="left", left_on=["territoire", "commune"], right_on=["departement", "commune"])
    cov["prospects_detectes"] = cov["prospects_detectes"].fillna(0).astype(int)
    k1, k2, k3 = st.columns(3)
    k1.metric("Zones suivies", len(cov))
    k2.metric("Couverture complète", int((cov["statut_couverture"] == "Complète").sum()))
    k3.metric("À balayer", int((cov["statut_couverture"] == "Non balayée").sum()))
    st.dataframe(
        cov[["territoire", "bassin", "commune", "priorite", "statut_couverture", "derniere_recherche", "prospects_detectes", "notes"]],
        use_container_width=True, hide_index=True,
    )
    st.download_button("Télécharger la couverture", cov.to_csv(index=False).encode("utf-8-sig"), "couverture_06_83_monaco.csv", "text/csv")

with tab_archive:
    st.subheader("Établissements déjà ouverts")
    st.caption("Ces lignes sont conservées pour mémoire mais ne figurent plus dans les priorités commerciales.")
    archive = df[df["stade"] == "Ouvert"].sort_values("date_ouverture_estimee", ascending=False)
    st.dataframe(
        archive[["etablissement", "commune", "departement", "type_concept", "date_ouverture_estimee", "source_url", "statut_donnee"]],
        use_container_width=True,
        hide_index=True,
        column_config={"source_url": st.column_config.LinkColumn("Source")},
    )

with tab_import:
    st.subheader("Importer des résultats de veille")
    st.write("Le CSV doit reprendre les colonnes du modèle. Les données importées restent en mémoire pendant la session.")
    template = df.head(0).to_csv(index=False).encode("utf-8-sig")
    st.download_button("Télécharger le modèle CSV", template, "modele_import_prospects.csv", "text/csv")
    uploaded = st.file_uploader("Importer un CSV", type=["csv"])
    import_clicked = st.button("Ajouter le fichier au radar", disabled=uploaded is None)
    if uploaded is not None and import_clicked:
        try:
            incoming = prepare(pd.read_csv(uploaded, dtype={"departement": str}))
            missing = set(df.columns) - set(incoming.columns)
            if missing:
                st.error("Colonnes manquantes : " + ", ".join(sorted(missing)))
            else:
                st.session_state.prospects = prepare(
                    pd.concat([df, incoming[df.columns]], ignore_index=True)
                )
                st.success(f"{len(incoming)} ligne(s) ajoutée(s).")
        except Exception as exc:
            st.error(f"Import impossible : {exc}")

    st.subheader("Ajouter un signal manuellement")
    with st.form("add_signal", clear_on_submit=True):
        a, b, c = st.columns(3)
        name = a.text_input("Établissement / projet *")
        city = b.text_input("Commune *")
        department = c.selectbox("Territoire", ["06", "83", "MC"])
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



with tab_signals:
    st.subheader("Nouveaux signaux détectés automatiquement")
    n1, n2, n3 = st.columns(3)
    n1.metric("Nouveaux au dernier passage", len(new_signals_df))
    n2.metric("Total à qualifier", len(weekly_signals_df))
    n3.metric(
        "Dernier passage automatique",
        metadata_map.get("dernier_passage_automatique_utc", "Pas encore exécuté"),
    )

    st.warning(
        "Un signal RSS n'est pas un prospect confirmé. Vérifie la source, "
        "le lieu, le calendrier et l'exploitant avant de l'ajouter à prospects.csv."
    )

    if new_signals_df.empty:
        st.info(
            "Aucun passage automatique n'a encore été exécuté depuis cette livraison, "
            "ou aucun nouveau signal n'a été trouvé."
        )
    else:
        st.dataframe(
            new_signals_df[
                ["date_publication", "territoire", "zone", "theme",
                 "titre", "source", "url", "statut_qualification"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Tous les signaux à qualifier")
    st.dataframe(
        weekly_signals_df,
        use_container_width=True,
        hide_index=True,
    )

with tab_status:
    st.subheader("État général des données")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Prospects", metadata_map.get("nombre_prospects", "0"))
    s2.metric("Avant ouverture", metadata_map.get("nombre_projets_avant_ouverture", "0"))
    s3.metric("Communes suivies", metadata_map.get("nombre_communes_suivies", "0"))
    s4.metric("Signaux à qualifier", metadata_map.get("nombre_signaux_a_qualifier", str(len(weekly_signals_df))))
    s5.metric("Contacts", metadata_map.get("nombre_contacts", str(len(contacts_df))))

    st.subheader("Automatisation hebdomadaire")
    a1, a2, a3 = st.columns(3)
    a1.metric("Fréquence", "Chaque lundi")
    a2.metric("Nouveaux signaux", metadata_map.get("nouveaux_signaux_dernier_passage", "0"))
    a3.metric("Erreurs du dernier passage", metadata_map.get("erreurs_dernier_passage", "0"))
    st.caption(
        "Le workflow `.github/workflows/veille_hebdomadaire.yml` peut aussi être "
        "lancé manuellement depuis l'onglet Actions de GitHub."
    )

    st.subheader("Fraîcheur par territoire")
    st.dataframe(
        zone_status_df.sort_values(["jours_depuis_maj", "territoire"], na_position="last"),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Inventaire des fichiers")
    st.dataframe(
        data_status_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Historique des mises à jour")
    st.dataframe(
        update_history_df.sort_values("date_utc", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "La date de génération du ZIP ne prouve pas qu'un balayage externe a été effectué. "
        "Les nouveautés correspondent uniquement aux lignes présentes dans prospects.csv."
    )

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
    st.subheader("Tendances internationales transférables")
    trends = pd.DataFrame([
        ["No/low premium", "Espagne, Royaume-Uni, pays nordiques", "Bars à mocktails, hôtels bien-être, restaurants premium", "Bières 0,0 %, jus, sirops, tonics, eaux"],
        ["Spritz et faible degré", "Italie, Espagne, États-Unis", "Aperitivo, rooftops, plages et lieux de fin de journée", "Apéritifs, vins effervescents, sirops, eaux gazeuses"],
        ["Casual luxe", "Royaume-Uni, Portugal, Italie", "Hôtels lifestyle, clubs, restaurants accessibles premium", "Champagne, vins, café, eaux premium"],
        ["Competitive socialising", "Royaume-Uni, États-Unis", "Padel, bowling, karaoké, jeux et restauration", "Bière, cocktails, softs, énergisants"],
        ["Boissons fonctionnelles", "États-Unis, Royaume-Uni", "Fitness premium, spas, concepts healthy et coworking", "Jus, thé, eaux, sans-alcool"],
        ["Nature et agritourisme", "Italie, Portugal, Grèce", "Domaines, fermes-auberges, glampings et retraites", "Vins, bières locales, jus, café, eaux"],
    ], columns=["Tendance", "Marchés témoins", "Niches à rechercher dans le 06/83", "Familles concernées"])
    st.dataframe(trends, use_container_width=True, hide_index=True)

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
    st.info("Le radar croise les 1 378 articles existants avec les tendances internationales et les opportunités de nouvelles gammes.")
