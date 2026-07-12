# Radar prospects boissons — 06 & 83 · V2.2

Pré-version Streamlit d'un radar commercial destiné à détecter les nouveaux établissements, reprises, transformations et niches pertinentes pour un grossiste en boissons.

## Fonctionnalités

- filtres par département, stade, horizon et confiance ;
- tableau de bord des signaux prioritaires ;
- qualification des ouvertures, reprises et transformations ;
- ajout manuel et import/export CSV ;
- bibliothèque de sources et de requêtes de veille ;
- correspondance entre concepts détectés et familles du catalogue.

Le jeu initial contient uniquement des établissements réels accompagnés d'une source publique. Les projets dont l'ouverture ou l'activité actuelle n'a pas été confirmée sont explicitement marqués à revalider.

## Lancer localement

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Community Cloud

1. Créer un dépôt GitHub et y pousser les fichiers.
2. Dans Streamlit Community Cloud, sélectionner le dépôt et la branche.
3. Choisir `app.py` comme fichier principal.
4. Déployer.

## Format d'import

L'onglet **Importer / ajouter** permet de télécharger un modèle CSV vide. La pré-version conserve les ajouts en mémoire pendant la session ; une base persistante sera ajoutée après validation de la structure.

## Suite proposée

- connecteurs de veille RSS et recherche web ;
- dédoublonnage par établissement, adresse et exploitant ;
- historique des changements et alertes ;
- validation humaine des signaux ;
- stockage persistant ;
- enrichissement SIRENE/RNE/BODACC.
