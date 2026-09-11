# Qualification sémantique des champs

Le catalogue complémentaire `tca-bp-field-semantics/1.0.0` définit les 297 champs de la trame : unité, assiette, propriétaires métier, domaine de calendrier, politique de saisie, blancs, zéros et défauts calculés. Il enrichit une copie du catalogue en mémoire. Le classeur et le manifeste scellés restent inchangés.

La qualification de la **signification du champ** reste distincte de la qualification de la **valeur du dossier**. Une définition « taux d’IS, fraction de la base imposable » ne confirme ni un taux légal, ni une exonération, ni l’éligibilité du client. Les sources, déclarations, périodes et gardes de [qualification du dossier](QUALIFICATIONS.md) restent nécessaires.

## Consultation et saisie

`ModelEngine.catalog()` et `Application.fields(case_id, sheet)` exposent les champs enrichis. Les questions du coordinateur reprennent la même unité, la même assiette et la même politique. Les [33 fiches de feuille](feuilles/README.md) les présentent avec les formules réellement lues.

Chaque entrée contient notamment :

- `unit` et `basis` : dimension de saisie et montant ou activité auquel elle s’applique ;
- `semantics.dependencies.business_owners` : identifiants des propriétaires métier ; la ligne de contrat, d’actif ou d’offre reste celle désignée par le dossier ;
- `semantics.dependencies.calculated_defaults` : les 809 défauts, avec leurs formules exactes et leurs références A1 extraites ;
- `semantics.dependencies.downstream` : requête de cellules vers le graphe scellé du modèle, dans le sens des consommateurs ;
- `semantics.calendar` : dates réelles, exercices actifs, antériorité ou fenêtre historique selon le champ ;
- `semantics.policy` : contraintes/choix, cellules requises du registre, traitement des blancs et zéros, source, et éventuelles exceptions de remplacement de défaut ;
- `semantics.status` : `ETABLI_MODELE`, `REEXAMEN_REQUIS` ou `HORS_PERIMETRE` ;
- `semantics.version` et `contract_sha256` : version et empreinte de ce contrat complémentaire.

`ETABLI_MODELE` atteste une interprétation technique documentée de la carte et des formules auditées. Ce statut n’est ni une approbation du responsable TCA, ni une validation économique ou fiscale du dossier. La règle de complétude conditionnelle demeure appliquée par le moteur central et par les qualifications par périmètre ; cette documentation ne crée aucune permission d’écriture supplémentaire.

Un champ inconnu, dont la plage, le type, les choix, les contraintes ou le défaut changent, passe en `REEXAMEN_REQUIS`. Une modification d’un témoin d’assiette ou de dimension provoque le même résultat pour ses champs liés. La préparation et l’application refusent leurs saisies. En lecture financière, seuls les propriétaires effectivement requis par le périmètre ajoutent `SEMANTIQUE_NON_ETABLIE` ; une inconnue sans lien avec le CA ne bloque pas arbitrairement le CA.

## Distinctions relues dans le modèle

| Champ | Unité et assiette |
|---|---|
| Prix d’offre et prix négocié du contrat | EUR HT par unité ; quantité et montant total restent distincts. |
| Matière, intégration, essais, autres coûts et coût manuel | EUR HT par unité de l’offre, selon la méthode retenue. |
| Logistique et garantie | Fractions du CA, confirmées par les en-têtes et le calcul du COGS. |
| Couverture du stock et délai fournisseur | Jours ; les formules relues divisent par une constante 30. Elles ne prennent pas leur diviseur dans `Control!C13`. |
| Choc de délai client | Choc relatif composé multiplicativement. |
| Retard de financement | Nombre entier de mois composé additivement. |
| Capacité industrielle | Unités par exercice ; zéro signifie absence de contrainte de capacité, pas production nulle. |
| Salaire | Brut annuel à temps plein, base du premier exercice ; présence, ETP, indexation et charges restent séparés. |
| Société/transaction comparable | CA, EBITDA et EV en millions d’EUR. |
| Equity et dette du panel bêta | Même monnaie et même facteur d’échelle documentés pour les deux montants ; le modèle calcule leur ratio. |
| Sortie VC | Année civile, distincte d’une durée ou d’un indice A1–A10. |
| Hypothèses fiscales | Taux en fraction, montants en EUR, mois et délais distincts ; régime, juridiction et période à qualifier séparément. |

Les identifiants historiques contenant `2026` à `2035` restent stables pour la compatibilité. Ils désignent les positions A1 à A10 du calendrier courant ; ils n’imposent pas ces années civiles au nouveau dossier.

## Nature des preuves

Les 297 définitions sont énumérées explicitement dans le code de définition, puis contrôlées contre le contrat de chaque champ de la carte relue. Aucune unité n’est décidée par recherche de mots dans un libellé. La revue technique s’appuie sur les entrées, les libellés explicites, les règles du moteur et les formules déjà auditées. Les champs textuels et choix possèdent une dimension documentaire explicite ; ils ne sont pas transformés en taux ou montants.

Vingt témoins supplémentaires figent des formules ou en-têtes sensibles : prix × quantité, pondération, coûts, assiettes de charges, délai client, stock et ratio bêta. Ces témoins servent à détecter une dérive de signification ; leur nombre ne prétend pas représenter 297 démonstrations économiques. Les champs restants conservent leur définition explicite et le contrôle du contrat exact de carte, avec leurs limites de qualification client. Une modification économique au-delà de ces témoins nécessite toujours la revue d’impact du parcours TCA.

Les formules sources des 809 défauts sont listées intégralement ; l’extraction A1 ne prétend pas résoudre toutes les références dynamiques. Le graphe scellé reste la source distincte pour les dépendances de calcul générales. Une réécriture équivalente du calendrier en dehors des témoins de dimension ne provoque pas un rejet global arbitraire.

## Révision et reprise

Une nouvelle définition ou un changement de signification suit une revue explicite : mettre à jour l’identifiant de version, les définitions, les preuves figées, les tests et les fiches. La production des preuves est réservée à l’outil interne de développement ; rien n’est régénéré automatiquement dans le pack client.

Un nouveau plan contient l’empreinte sémantique. Si cette empreinte change avant application, il faut préparer un nouveau plan explicite. Un plan historique sans empreinte n’est accepté que si ses cellules possèdent encore une définition établie, en plus des contrôles existants de modèle, copie, état attendu et source. Les reçus de qualification incluent également l’empreinte du catalogue : un cache Excel peut rester à jour tandis que l’interprétation nécessite une nouvelle qualification.

Les tests dédiés couvrent les 297 définitions, les 809 défauts, les distinctions d’unité, les inconnues et dérives, l’absence de mutation du schéma, la portée des blocages et la compatibilité des lots fictifs préparés. Ces tests s’exécutent sans COM. Les résultats financiers et les tables/WACC conservent leurs recettes natives propres.
