# Recalcul Excel et preuve de conservation

`native_excel.recalculate` produit une nouvelle copie XLSM et un reçu. Son
succès signifie que Microsoft Excel a recalculé, sauvegardé puis rouvert cette
copie, avec conservation des entrées et de la mécanique contrôlée. Il ne
constitue pas une validation économique du dossier.

Le superviseur inventorie les processus Excel avant lancement. Le worker
obtient ensuite le PID de son instance COM et attend un accusé de propriété.
Le superviseur refuse un PID préexistant et conserve un handle du processus
identifié. Aucun réglage Excel ni ouverture de classeur ne précède cet accusé.
En cas de dépassement du délai ou d'échec, seul ce processus identifié et le
worker lancé par l'opération peuvent être arrêtés. L'instance doit être vide.

Les macros, événements et mises à jour des liens restent désactivés. L'itération
globale est refusée. `CalculateFullRebuild` s'exécute sur une ouverture en lecture
seule ; `SaveCopyAs` écrit une destination neuve. La copie est ensuite rouverte,
fermée sans sauvegarde et son empreinte est revérifiée.

Avant et après Excel, `workbook_proof` vérifie les formules, constantes et
éléments mécaniques pris en compte par la signature du moteur. Les caches des
tables natives sont exclus des constantes d'entrée ; leurs rectangles sont
dérivés des ancres `dataTable` du classeur. Les cinq sorties WACC sont conservées
comme constantes et ne sont pas réécrites par un recalcul ordinaire. Le service
vérifie en plus l'identité de modèle et les protections avant toute adoption.

Le reçu exige des booléens JSON stricts pour les preuves, un état de calcul
entier nul, les empreintes exactes et une liste vide d'écritures métier. À cette
couche, `adopted` reste faux. Seule la transaction du service peut adopter la
copie dans un dossier ; un fichier de sortie présent après un échec ne vaut pas
adoption.

`include_tables=True` demande un recalcul des tables et conserve le statut
`RECALCUL_DEMANDE`. La vérification des 57 résultats contre 24 scénarios isolés
relève de `sensitivity_native`, avec son propre reçu. Le recalcul ordinaire ne
lance pas le solveur WACC et ne qualifie pas ses résultats.

Les tests simulés de `tests/test_native_excel.py` couvrent le refus d'un processus
préexistant, le délai dépassé, les preuves mal typées, un changement d'entrée,
l'itération active et la distinction entre calcul et adoption. Ils n'ouvrent pas
Excel.

Première preuve native du worker durci : le 11 septembre 2026, la campagne
`runtime/recette_financiere_20260911_215558_e1b6d173` a passé ses 12 oracles de
qualification fiscale sur la trame 1.1.2, SHA
`e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.
Le reçu `dossiers/qualification_fiscal_branches/versions/v0002_excel_46815cbb.recalcul.json`
documente le PID dédié 31428, la sauvegarde/réouverture, la conservation de la
source et des entrées, avec macros et itération désactivées. Cette preuve porte
sur ce cas et cette version ; elle ne certifie pas tous les cas du modèle.
