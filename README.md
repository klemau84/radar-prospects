# Radar CHR — V7.3

Cette version ajoute une base de contacts professionnels publics reliée aux prospects par `prospect_id`.

## Nouveautés V7.3

- nouvel onglet **Contacts** avec nom, fonction, organisation, téléphone, e-mail, source et fiabilité ;
- filtre **Avec contact identifié uniquement** dans la barre latérale ;
- coordonnées principales visibles dans le tableau des projets et les priorités ;
- liste automatique des prospects dont le contact reste à identifier ;
- export CSV et ajout manuel pendant la session Streamlit ;
- conservation des contacts dans `data/contacts.csv`, séparément de la veille automatisée.

Les coordonnées proviennent uniquement de sources professionnelles publiques. Un numéro de standard, un contact presse ou une autorité administrative ne sont pas considérés automatiquement comme décideurs achats. Le champ `type_contact` et les notes précisent cette distinction.

La détection SIRENE reste active pour les créations CHR récentes du 06 et du 83. Aucun signal n'est converti automatiquement en prospect.

Génération UTC : 2026-08-02
