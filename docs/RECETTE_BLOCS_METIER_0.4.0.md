# Recette des extensions métier — 13 septembre 2026

Les recettes ont utilisé des copies exclusivement fictives, Microsoft Excel 16.0, les macros et événements désactivés, puis une sauvegarde et une réouverture contrôlées. Les sources, les tentatives antérieures et les reçus sont conservés. Aucune trame publique n'a été remplacée.

## Quatorzième offre

Résultat : **succès**. L'opération qualifiée `extend_offer`, famille `produit_libre`, a étendu les blocs de neuf feuilles et scellé un nouveau modèle. Les treize offres existantes gardent leur identité ; les 84 entrées supplémentaires sont reconnues par le catalogue, les agents et les contrôles. Les nouvelles hypothèses sont initialement à compléter, sans reprendre les hypothèses de l'offre copiée.

La recette ajoute 120 unités annuelles à 100 €, coût unitaire de 40 €, paiement comptant explicite de 100 %. Le cas de départ comporte 120 000 € de chiffre d'affaires et 48 000 € de coûts annuels.

| Contrôle indépendant | Attendu | Calcul Excel |
|---|---:|---:|
| Chiffre d'affaires annuel, `Revenue!E302` après insertion | 132 000 € | 132 000 € |
| Coût annuel, `COGS!E271` après insertion | 52 800 € | 52 800 € |
| Trois rapprochements TVA, `ATELIER_CIR_IS!AA185:AA187` | 0 | 0 |

Les rapprochements sont des écarts de contrôle, pas des montants de TVA. La recette ne constitue pas une validation de règles fiscales réelles. Le recalcul `CalculateFullRebuild`, sa sauvegarde et sa réouverture ont pris environ 137 secondes, hors préparation et contrôles Python.

Une lecture complémentaire de cette même copie calculée, dont l'empreinte est vérifiée, contrôle les trois années 2026–2028 : les six agrégats annuels et les six sommes des douze mois associés respectent les mêmes oracles, soit **12 contrôles sur 12 réussis**. Aucun nouveau recalcul n'est déduit de cette seule lecture ; elle est liée au reçu natif précédent.

Preuves :

- `runtime/recette_bloc_offer_20260913_022035_0f887d/validation.json` : résultats, source et VBA préservés, reçu natif et liens vers la variante reprise.
- `runtime/recette_bloc_offer_20260913_022035_0f887d/validation_periodes.json` : 12 contrôles annuels et mensuels sur 2026–2028.
- `runtime/recette_bloc_offer_20260913_015724_08bab7/variant.variant.json` : aperçu exhaustif avant/après et réparations des références, empreinte `8a18519fc9fa3d4c76012bb16d198cace4f107ab32d0a5449de1291f8fcb55c5`.
- Copie calculée : SHA-256 `22007f94aa3e5cbff32e5abac304184da99f1d881627bc3ee9eeb084ec1972e1`.

Les premières tentatives ont permis de corriger la copie d'une fusion sur deux lignes et l'écriture de formules dans des cellules au format texte. Deux reprises ont été refusées avant Excel par le contrat d'entrée : unité au pluriel non admise, puis répartition des règlements incomplète. Seules les données fictives de recette ont été corrigées ; les contrôles métier sont conservés. Ces reçus d'échec restent présents.

## Extension du registre Effectifs

Résultat : **succès selon la convention existante du modèle**. Une ligne métier supplémentaire a été insérée au-delà de la capacité initiale, avec conservation des identifiants des lignes existantes et déplacement des agrégats. Le moteur reconnaît les nouvelles entrées comme un recrutement documenté.

Le témoin fixe un salaire annuel de 60 000 €, 40 % de charges, un ETP du 1er janvier au 31 décembre 2026. Le contrat `employee_end` existant exclut le mois dont la fin coïncide avec la sortie ; le coût attendu est donc `60 000 × 1,4 × 11/12 = 77 000 €`, obtenu par Excel. Le premier oracle de douze mois était incompatible avec ce contrat. Le classeur, sa date de sortie et ses formules n'ont pas été changés pour corriger cette erreur de recette.

Preuves : `runtime/recette_bloc_register_20260913_010613_429211/validation.json` (tentative et calcul d'origine) et `validation_convention.json` (oracle corrigé avec empreinte du reçu précédent, justification et conservation source/VBA).

L'extension qualifiée est actuellement disponible pour `Effectifs`. Les autres registres refusent une extension de capacité sans recette propre à leurs blocs de cohorte, financements et fiscalité ; l'ajout d'un enregistrement dans leur capacité existante reste distinct.

## Écriture et intégrité

Un témoin natif supplémentaire vérifie cinq formules dans des cellules au format texte, dont une cellule fusionnée, deux matrices contiguës de quatre références et la cellule intermédiaire qui doit rester intacte. Le format initial est restauré. Preuve : `runtime/recette_serialization_text_20260913_015412_c67aba/validation.json`. Ce témoin porte sur la sérialisation, sans qualifier ses résultats financiers.

Le contrôle préalable refuse une formule visant une feuille qui ne sera créée que plus tard dans le lot. Le contrôle du classeur sauvegardé refuse tout nouveau composant ou lien de classeur externe (`NEW_EXTERNAL_LINK`), y compris une nouvelle cible sous un identifiant de relation existant. Les suppressions n'autorisent pas la perte de composants appartenant à une autre feuille ni celle d'ancrages de calcul natif.

Les aperçus volumineux affichent des échantillons et donnent accès au manifeste exhaustif dont l'empreinte est liée au jeton d'approbation. Le nettoyage conserve ce manifeste et les reçus ; les requêtes intermédiaires redondantes sont remplacées par des résumés sans valeurs.

## Portée

Ces résultats valident un cas d'offre supplémentaire et un cas d'extension Effectifs sur le moteur natif. Ils ne prouvent pas toutes les combinaisons d'offres, de contrats, de fiscalité et de calendriers. Les autres recettes du prototype, notamment réalisé, WACC, livrables et navigateur, disposent de leurs propres reçus.
