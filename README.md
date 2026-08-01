
# Radar CHR — V7.1b

## Nouveautés

- fiche prospect 360° ;
- tableau commercial **À traiter** ;
- fichiers `actions_commerciales.csv` et `contacts.csv` ;
- suivi des relances ;
- validation manuelle des propositions de fusion ;
- reconstruction CRM avec `scripts/rebuild_crm.py` ;
- mise à jour automatique du CRM après la veille hebdomadaire.

## Saisie des actions

Compléter `data/actions_commerciales.csv`, puis lancer :

```bash
python scripts/rebuild_crm.py
```

Aucune fusion de prospects n'est appliquée automatiquement.

Génération UTC : 2026-08-01T14:14:42Z
