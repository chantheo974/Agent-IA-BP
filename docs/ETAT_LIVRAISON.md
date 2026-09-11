# État de livraison — TCA BP 0.2.0

L'application Windows et son moteur de saisie sont construits en Python 3.14. La trame courante est le build **1.1.2**, modèle `tca-bp-template/1`. Ce document décrit la version locale 0.2.0, ses fonctions et ses limites ; la recette identifie séparément chaque preuve logicielle et native.

Le plan initial est conservé dans son état d'origine. Les dix documents initiaux ont été audités et leurs empreintes sont restées inchangées. Le premier pack 0.1.0 est archivé et retiré de la distribution ; cette version le remplace après correction des commentaires hérités.

## Fonctions construites

| Périmètre | Comportement |
|---|---|
| Trame | 33 feuilles, 297 champs, 14 315 entrées autorisées, 809 défauts calculés, 363 865 formules protégées ; registres client vidés et offres à identifiants génériques stables. |
| Connaissance | 33 contrats et 33 fiches, 297 définitions explicites avec unités, bases, calendriers et propriétaires métier. Les 809 défauts sont liés à leurs formules et références. Un contrat sémantique incompatible suspend les champs concernés. Le graphe distingue les formules, noms, défauts, tables et la résolution WACC. |
| Dossiers | État SQLite, client et dossier identifiés, sources locales, copies versionnées, journaux et reprise. La version exacte du modèle est archivée par empreintes et conservée lors d'une mise à jour. |
| Propositions | Saisie par champs ou registre, état prospectif du lot, aperçu, sources du même dossier, refus de formule libre et de plan périmé, rejeu idempotent. Les propositions de plusieurs agents sont conciliées avant préparation ; un conflit suspend le seul lot concerné. |
| Qualifications | États explicites, inactivité déclarée sans effacer les valeurs, sources vérifiées, revue fiscale datée et cinq périmètres de disponibilité. Une hypothèse ne devient pas confirmée après un calcul. |
| Calcul | Excel séparé, macros désactivées, nouvelle copie et contrôle des signatures. Les résultats enregistrés sont invalidés après une saisie. |
| WACC | Résolution locale bornée, cinq sorties autorisées, contrôle du résidu, sauvegarde et réouverture. Le service publie une nouvelle version seulement après vérification des entrées et des sources. |
| Sensibilités | Trois tables confrontées à 24 copies scalaires, soit 57 comparaisons ; contrôles de conservation, de persistance et d'effet réel des axes. Une campagne interrompue ne devient jamais une preuve partielle. |
| Maintenance TCA | Proposition de modification d'une formule existante, impact, variante scellée, attentes indépendantes, calcul natif et descripteur d'approbation distinct. Le pack client ne contient aucun générateur ou moteur de maintenance. |
| Interfaces | Fenêtre Windows, CLI JSON et serveur MCP local utilisent le même service. Aucune clé API n'est nécessaire à la saisie guidée. |

## Trame et preuves

SHA256 de la trame courante : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.

SHA256 de son schéma : `f0da6d7da5df3fda899adc23ec33b5d40f413821481dced7a11f46d78d8867eb`.

La revue documentaire a examiné les textes du classeur et ses composants XML. Le scanner final contrôle 62 parties XML, y compris attributs, objets et éléments masqués, sans publier les fragments privés recherchés. Les macros conservées ont été inspectées statiquement et sont scellées ; elles ne sont pas exécutées par l'application. Les anciens secrets de protection ont été retirés, tandis que les drapeaux de protection des feuilles sont conservés.

La révision finale est comparée à la trame documentaire précédente : trois libellés et 45 formules de garde ou de diagnostic changent explicitement. Les autres formules, valeurs d'entrée, styles effectifs et composants utiles sont préservés. Les gardes fiscales n'accordent plus un régime favorable à une condition inconnue. Les années hors horizon valide sont neutralisées dans ces gardes ; les inconnues des années actives restent indisponibles. Douze attentes natives vérifient ces branches. Les résultats restent soumis à la qualification du dossier.

Les recettes sont décrites dans la [recette de validation](RECETTE_VALIDATION.md). Elles comprennent les opérations commerciales et de trésorerie, les actifs et aides, les branches fiscales, le solveur WACC et les tables. Chaque reçu conserve le modèle, les entrées, la copie et les attentes effectivement vérifiés. Le nombre de tests logiciels ne remplace pas une preuve financière native.

## Limites d'utilisation

Le dialogue intégré est guidé par les contrats et les règles métier. Un assistant externe peut raisonner via MCP ; le logiciel ne transforme pas automatiquement une pièce jointe en donnée validée et ne réalise pas d'OCR.

Les conventions fiscales et comptables héritées doivent être revues pour la juridiction, les dates et l'activité de chaque dossier. La disponibilité d'un périmètre signifie que ses prérequis ont été qualifiés et son calcul effectué ; elle ne constitue pas une certification financière ou fiscale.

Le parcours de maintenance fourni modifie des formules ordinaires existantes. Une nouvelle feuille, un nouvel inducteur structurel, une modification de macro ou de table exige une évolution du générateur dans le dépôt TCA, suivie de sa propre cartographie et recette. Aucun dossier client n'est migré automatiquement.

L'application est locale, destinée à un utilisateur Windows. La protection des feuilles ne chiffre pas les fichiers. L'accès aux pièces relève des permissions du stockage choisi et de la protection du compte Windows ; le logiciel n'ajoute pas une authentification multiutilisateur.

## Guides et vérifications

[Interface](INTERFACE.md), [catalogue sémantique](CATALOGUE_SEMANTIQUE.md), [qualifications](QUALIFICATIONS.md), [versions](MODELES_ET_VERSIONS.md), [conflits](PROPOSITIONS_ET_CONFLITS.md), [WACC](model_wacc.md), [sensibilités](model_sensitivity.md), [distribution](DISTRIBUTION.md).

Dans le dépôt TCA, les tests sont exécutables avec `py -3.14 -m unittest discover -s tests -v`. Les recettes natives demandent Microsoft Excel et sont lancées séparément sur des dossiers fictifs. Le pack client utilise la trame déjà construite et n'inclut ni les références privées, ni les jeux de test, ni leurs reçus internes.
