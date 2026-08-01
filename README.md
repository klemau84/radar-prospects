
# Radar CHR — V5.2

## Veille hebdomadaire

GitHub Actions lance `scripts/update_weekly.py` chaque lundi à 05:30 UTC.

Le script :

- interroge des flux Google News RSS ciblés sur le 06, le 83 et Monaco ;
- détecte les nouveaux signaux ;
- conserve les signaux dans `data/signaux_hebdo.csv` ;
- place les nouveautés dans `data/nouveaux_signaux.csv` ;
- met à jour les métadonnées et l'historique ;
- crée automatiquement un commit si les fichiers ont changé.

## Limite importante

Les signaux détectés ne sont pas ajoutés automatiquement aux prospects confirmés.
Ils doivent être vérifiés dans l'onglet **Signaux hebdo**.

## Activation

Après le premier push :

1. ouvrir l'onglet **Actions** du dépôt GitHub ;
2. ouvrir **Veille hebdomadaire Radar CHR** ;
3. cliquer sur **Run workflow** pour effectuer un premier test ;
4. vérifier que GitHub Actions dispose de l'autorisation d'écriture :
   `Settings > Actions > General > Workflow permissions > Read and write permissions`.
