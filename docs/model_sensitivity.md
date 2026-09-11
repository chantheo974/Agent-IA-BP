# Vérification des tables de sensibilité

Le composant `tca_bp/sensitivity_native.py` vérifie les trois tables de
`Sensi Analyses` par comparaison à 24 calculs scalaires distincts. Cette preuve
porte sur le mécanisme des tables ; elle ne certifie pas l’ensemble du modèle
financier ni les hypothèses économiques du dossier.

| Table | Résultats | Scénarios indépendants | Sorties scalaires |
|---|---:|---:|---|
| Tornado D25:G33 | 36 | 9 | D24:G24 |
| Volume C40:D45 | 12 | 6 | C39:D39 |
| Volume/aides D50:F52 | 9 | 9 | C49 |

Les axes sont vérifiés contre leur définition native. Dans la grille à deux
entrées, les colonnes agissent sur C14 (aides), les lignes sur C8 (volume).
Les neuf chocs F8:F16 doivent être explicitement non nuls pour cette campagne.
Une tolérance absolue de 0,01 euro s’applique à chaque comparaison. Les blancs,
booléens, textes, erreurs Excel, valeurs infinies et NaN sont refusés.

Le protocole exige un effet mesurable du Tornado, du volume et de chacun des
deux axes de la grille volume/aides. Une activité absente, ou un décalage
intermédiaire qui ne change pas les quatre sorties de synthèse, peut expliquer
un levier du Tornado sans effet ; cette information figure dans le reçu.
Une égalité sur ce levier ne constitue pas une preuve économique de son effet
sur chaque mois.
Une grille entièrement figée ne peut donc pas passer par égalité triviale.

La préparation valide le modèle puis fabrique 24 copies instrumentales. Seuls
les trois littéraux C8, C14 et C18 varient ; leur remise à zéro reconstitue
exactement les octets XML d’origine. Chaque autre partie ZIP, notamment les
formules, styles, protections et le VBA, doit conserver son empreinte exacte.
Ces pilotes protégés ne sont pas ajoutés à l’API de saisie métier.

Le worker utilise une seule instance Excel dédiée, identifiée par PID et handle
après exclusion des instances préexistantes. Aucun réglage ni ouverture de
classeur ne précède l’accusé de propriété. Les macros, événements et mises à
jour des liens restent désactivés ; l’itération globale est refusée.

La base calcule les tables en mode automatique, retrouve le mode sans tables,
puis est sauvegardée et rouverte. Les instruments sont ouverts successivement
en lecture seule et recalculés sans tables ; seuls les relais de sortie sont
lus. Ils ne sont jamais sauvegardés ou adoptés. La base ne reçoit aucun choc :
le reçu indique **isolation par copies**, pas une restauration COM fictive.

Après Excel, les empreintes source/instruments sont revérifiées. La nouvelle
base doit conserver la mécanique reconnue par ModelEngine, toutes les entrées,
les pilotes, le scénario, l’horizon et les cinq sorties WACC. Les caches lus
directement sur disque doivent correspondre aux valeurs relues dans Excel.
Seul le service peut ensuite décider une adoption, sous son verrou et avec
les qualifications et preuves documentaires du dossier. Le reçu retourne
toujours `adopted: false` à cette couche.

Le délai mural de chaque tentative est borné à 3 600 secondes par défaut et au
maximum. Les recalculs ordinaires mesurés dans les autres recettes durent
87–89 secondes par copie ; à 88 secondes, 24 scalaires représentent 2 112
secondes, soit environ 35 minutes, avant le coût de la base, de sa sauvegarde et
de sa réouverture. C’est une estimation, pas une mesure de cette campagne.
Les durées de la base et de chaque scénario sont émises. La campagne native
1.1.2 décrite ci-dessous a mesuré 86,04 secondes en moyenne par scalaire
(82,42 à 90,19), et 2 316,58 secondes pour l'opération supervisée complète.

Après la sauvegarde/réouverture de la base, puis après chaque scénario complet,
le superviseur vérifie les nombres et écrit un point de contrôle immuable.
Un registre d’empreintes lie ce préfixe contigu à la source, au modèle, au plan,
au code du worker/superviseur et à la base persistée. Une interruption produit
un diagnostic non adopté ; une reprise explicite réutilise seulement ces
points complets après contrôle des empreintes et de la même version Excel.
Elle relit la base dans Excel et poursuit les scénarios manquants. Aucun
résultat n’est qualifié avant les 24 scénarios et les 57 comparaisons finales.

`--resume` conserve la destination de cette même campagne et ses preuves.
Une base absente, une empreinte modifiée, un point orphelin ou un changement de
code impose une nouvelle campagne. Une reprise n’écrase pas le diagnostic de
la tentative précédente. Les fichiers scalaires restent des instruments non
adoptables, même après une interruption ; aucune source n’est remplacée.

Préparer le cas fictif sans Excel :

```powershell
py -3.14 tools/validate_sensitivity.py --model-dir models/VERSION --prepare-fixture
```

Après coordination explicite du créneau Excel, lancer la campagne préparée :

```powershell
py -3.14 tools/validate_sensitivity.py --model-dir models/VERSION --directory runtime/recette_sensitivity_ID --native --timeout 3600
```

Pour poursuivre une tentative interrompue disposant de points de contrôle,
ajouter `--resume` à la même commande. Cela lance aussi Excel et demande la
même coordination du créneau natif.

Pour un nouvel essai conservant les échecs précédents, `--attempt NOM` crée
une nouvelle destination et de nouveaux reçus sur les mêmes instruments
scellés. Le nom accepte seulement lettres, chiffres, tirets et soulignements.
Une reprise utilise le même nom avec `--resume` ; elle ne remplace ni la source,
ni les reçus des tentatives antérieures. Un changement de version du modèle
exige une nouvelle fixture, construite depuis cette version.

La fixture économique indépendante documente un minimum de cash de −48 000
euros : en janvier, 8 000 euros d’achats (dont 4 000 de stock) et un équipement
de 100 000 euros, contre une aide reçue de 60 000 euros, sans encaissement client.
Le grand livre mensuel fictif prévoit un cash final de 305 400 euros. Pour les
axes étudiés, le minimum vaut `-48000 - 8000 × choc_volume + 60000 × choc_aide`.
Les neuf résultats de la grille ont donc des attentes indépendantes, notamment
−106 400 euros à volume −20 % et aide −100 %. Les 14 attentes économiques ont
passé la recette native 1.1.2 ci-dessous ; elles ne sont pas copiées des formules
Excel.

Cette fixture de calcul ne constitue pas un dossier commercial complètement
qualifié. Son diagnostic documentaire exige encore les déclarations de modules
et la qualification des charges externes. Le reçu de la campagne directe ne
prouve donc pas une adoption par le service ou un affichage métier dans l'UI.
Les tests de publication du service sont des preuves distinctes ; aucun reçu
externe n'est injecté pour simuler une adoption native de cette fixture.

Le constructeur enrichit désormais le graphe avec les douze noms WACC, ses
références de formule exactes, le contrat des cinq écritures natives et les
263 références d’empreinte réparties en 124/94/45/0. Les rectangles des tables,
leurs pilotes protégés, l’orientation des axes, les relais scalaires et les
scénarios y figurent aussi. Générer ces métadonnées ne marque aucune exécution
native comme réussie ; un nouveau build est nécessaire pour les incorporer
dans les artefacts d’une version.

Les tests `tests/test_sensitivity_native.py` couvrent les comparaisons,
orientations, faux succès, modifications non autorisées et une interruption
simulée après deux scénarios. Leur réussite ne constitue pas une exécution
Excel. Une preuve native doit citer le reçu, le SHA source et la version de
modèle de la campagne effectivement terminée.

## Recette native du 11 septembre 2026

La campagne `runtime/recette_sensitivity_20260911_215958_4b26e5cb` a terminé
les 24 scénarios avec **57 comparaisons exactes sur 57**, un écart maximal nul
et les quatre critères de non-dégénérescence satisfaits. Le reçu est
`verification_qualified_v4.json` ; les **14 oracles économiques sur 14** sont
documentés dans `business_oracle_verification_qualified_v4.json`.

- Trame 1.1.2 : `e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12`.
- Source : `5dcfb520f90b9643b3a53754d97a7ee24ef2d177d32152221719b3020d80640e`.
- Copie recalculée : `d6feb43ae5867830f9afb0e1adfa57b2e1c36b8840c17f1e14c05e5fb6a5afde`.

Le reçu vérifie la conservation de la source, des instruments, des entrées,
des formules et des protections, ainsi que la sauvegarde et la réouverture.
Les macros et l'itération globale restent désactivées. Les 25 points de contrôle
(base et 24 scénarios) sont liés à leurs empreintes. Aucun processus Excel ne
subsistait au contrôle suivant l'opération.

Les leviers Tornado sans effet sur ces sorties sont les charges externes,
les effectifs et le retard du financement. Les deux premiers postes sont
absents de ce cas fictif ; le dernier déplace un encaissement intermédiaire
sans changer son point bas ni sa clôture. Cette recette ne démontre pas tous
leurs comportements mensuels.

La copie conserve 44 valeurs `#N/A` du périmètre DCF, dont les hypothèses sont
absentes de cette fixture. Aucune erreur n'est attribuée à CA, COGS, CASH ou
FISCALITE. `adopted:false` et `financial_model_globally_validated:false` sont
maintenus. Les qualifications documentaires manquantes sont explicites dans
`qualification_readonly_diagnostic.json` ; cette campagne ne prouve pas une
publication par le service ni un affichage qualifié de la sensibilité dans l'UI.

Les échecs antérieurs du 11 septembre sont conservés dans la campagne
`runtime/recette_sensitivity_20260911_214051_c4a5d7a5`. Le diagnostic des caches
sur la trame 1.1.1 y a révélé la propagation d'une fiscalité hors horizon vers
les agrégats actifs. La correction de la trame 1.1.2 fait l'objet d'une recette
distincte de 12 oracles ; aucun reçu antérieur n'a été réécrit en succès.
