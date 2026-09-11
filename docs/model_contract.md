# Contrat du modèle générique

Le modèle est une copie versionnée, générée par `py -3.14 tools/build_model.py`.
La référence locale reste intacte. `models/generic-v1` contient la trame, le
manifeste d'entrées, le catalogue, la classification des cellules, le graphe et
le reçu de construction. Ces artefacts locaux ne sont pas des sources à publier.

Les 33 feuilles et les composants de calcul utiles sont conservés. Les données
commerciales, RH, de financement, fiscales et de marché sont à renseigner pour
chaque dossier. Les treize offres commencent inactives ; leurs identifiants
`OFFRE_01` à `OFFRE_13` sont distincts des libellés présentés aux utilisateurs.
Une absence de prix, salaire ou qualification n'est jamais une autorisation de
supposer zéro. Les registres nouveaux sont vides.

Le premier jour du modèle est une vraie date de saisie en Control C10, limitée
au 1er janvier. C59 est un entier requis entre 1 et 10. La capacité technique
reste de dix exercices. Le calendrier initial 2026 et l'horizon de cinq ans sont
des choix techniques de démarrage modifiables, pas des données d'un client.
Les identifiants API hérités portant un suffixe d'année restent des alias stables
pour les positions A1, A2, etc. Les libellés publics utilisent ces positions.

Les durées et pourcentages R&D du catalogue CAPEX sont vides. Un défaut calculé
reste une formule liée aux entrées et nécessite une qualification avant usage.
Le taux de marché ancien exprimé par une formule numérique en Valorisation D112
est explicitement supprimé. Les références de comparaison du dossier précédent
sont supprimées ; leur absence donne un résultat indisponible.
Les valeurs de la grille de sensibilité Valorisation C65:C69 et D64:F64 sont
des axes techniques d'illustration ; elles ne renseignent pas le taux central.
Un coût manuel nul explicite est accepté. Un coût absent ou négatif est refusé,
dans le moteur comme dans les contrôles Excel correspondants.

`ModelEngine.prepare` construit l'état attendu des cellules et valide l'ensemble
du lot prospectif. Les écritures exigent une preuve de dossier, refusent les
cellules de calcul, les formules libres et les écrasements non déclarés. Les
défauts calculés peuvent être remplacés uniquement avec l'exception explicite
`override_default`. `apply` publie une nouvelle copie et son journal de manière
exclusive. Un plan périmé ne peut pas être rejoué sur une autre version.

Chaque copie écrite perd les caches des formules, des graphiques et des tables
de sensibilité. Le moteur ne produit aucun résultat financier recalculé et
n'exécute aucune macro. Le service natif puis la validation des hypothèses sont
des étapes distinctes. Un recalcul réussi ne confirme pas la pertinence du
scénario, les droits fiscaux ou la sécurisation d'un financement.

Les noms techniques historiques `ISP_WACC_*` restent exclusivement pour la
compatibilité avec le module VBA conservé. Ils ne désignent aucun dossier client.
La lecture statique du source VBA refuse les secrets littéraux et les procédures
d'ouverture automatique détectées. Elle ne constitue pas une preuve exhaustive
d'absence de comportement indésirable. Les règles fiscales datées héritées
nécessitent une revue explicite de la période et du régime applicable.

Une maintenance formule par formule peut produire une variante avec un nouvel
identifiant et un répertoire distinct. `reseal_variant` exige la liste exacte des
différences et refuse les changements d'entrées, constantes, styles, validations,
protections, noms et VBA. Les formules partagées peuvent être matérialisées sans
changement de règle. Le graphe conserve les anciens liens par prudence et ajoute
les nouvelles dépendances. La variante reste EXPERIMENTALE jusqu'aux tests
indépendants et natifs ; aucun dossier existant n'est migré automatiquement.
