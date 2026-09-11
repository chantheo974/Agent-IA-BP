# Gardes du module de valorisation

La génération 1.0.1 applique quatre corrections de robustesse. Après qualification
du candidat `models/generic-v1-guards`, la même trame est installée sous
`models/generic-v1`. L'ancienne référence exacte reste conservée sous
`models/generic-v1-pre-guards`. Une comparaison de toutes les cellules confirme que seules
les formules suivantes changent, sans modification des constantes ni du VBA.
Avant promotion, une copie exacte de la référence précédente peut être conservée
dans `models/generic-v1-pre-guards`. Les tests privilégient cette copie privée
pour conserver la comparaison historique après installation du candidat.

| Cellule | Comportement lorsque les informations sont absentes |
| --- | --- |
| Valorisation B55 | Affiche que le taux n'est pas renseigné ; aucun calcul numérique sur une chaîne vide. |
| Valorisation D59 | Affiche « Non renseigné » lorsque le pre-money ou le ticket manque, et « Non déterminé » lorsque le post-money n'est pas positif. |
| Contrôles C121 | Affiche « Non renseigné » tant que les deux références de pre-money ne sont pas numériques. |
| Contrôles N121 | Affiche un contrôle non effectué ; ne produit jamais « OK » sur une référence absente. |

Un ticket agrégé nul ne prouve pas un ticket saisi : l'absence de tour produit
également zéro dans la somme de financement. La garde exige donc un ticket
strictement positif, conformément à la borne du registre des financements.
Elle ne suppose aucun taux, ticket, pre-money ou ratio par défaut.

Les tests unitaires sont dans `tests/test_model_guards.py`. La recette native
doit être lancée explicitement vers un nouveau répertoire, par exemple :

```powershell
py -3.14 -m tests.test_model_guards --native --output "$env:TEMP\tca_guards_validation"
```

Cette recette utilise exclusivement des copies et des valeurs fictives. Elle
vérifie les états vide et partiel, une dilution de 20 % pour 250 000 € apportés
sur un pre-money de 1 000 000 €, un écart de 100 000 € entre les deux références,
et un dénominateur nul artificiel. Elle contrôle les signatures du modèle, les
protections et les saisies après recalcul Excel avec macros désactivées.
Le dernier cas vérifie d'abord que l'API refuse le pre-money non positif. Il
injecte ensuite ce seul défaut dans une copie de test afin de vérifier la garde
Excel face à une modification manuelle externe ; cette copie ne représente pas
une saisie autorisée ni une situation économique validée.

Cette preuve porte uniquement sur les quatre sorties corrigées. Les autres
erreurs liées aux paramètres de valorisation manquants restent recensées dans
le reçu ; la recette n'est pas une validation économique du modèle complet.

## Preuve obtenue le 11 septembre 2026

Les cinq cas ont passé le recalcul Excel natif avec macros désactivées et un
état de calcul terminé. Les signatures du modèle, les protections et les
saisies sont conservées sur les cinq copies ; les deux trames restent intactes.

| Cas | Résultat natif vérifié |
| --- | --- |
| Vide | Taux, dilution et rapprochement indisponibles ; aucun faux contrôle OK. |
| Partiel | Taux de 12 % visible, mais absence de ticket signalée. |
| Complet | Dilution de 20 %, écart nul entre registre et synthèse, contrôle OK. |
| Divergent | Écart de −100 000 € et alerte conservée. |
| Dénominateur nul | Saisie hors domaine refusée par l'API ; copie défensive indiquant « Non déterminé ». |

Les quatre cellules corrigées ne présentent plus d'erreur Excel dans ces cas.
Les 33 `#N/A` restants sont situés dans Valorisation, avec les autres paramètres
de ce module non renseignés et l'horizon de test de cinq exercices.

Le candidat testé porte l'empreinte SHA256
`ff5ad2f940c52e8282dc4b2785847f46faa822ef91b3e8090d6466ac838e04d6`.
La référence antérieure exacte porte l'empreinte
`15815c1062653d72cd7686334a3d080aeb88b9eb8f6f6fa75b6c7195409ed663`.
Le rapport local `models/generic-v1-guards/guard_delta.json` décrit les quatre
différences ; `guard_validation/` dans ce même dossier conserve les reçus natifs
exacts et la synthèse `validation.json`.

La [recette de livraison](RECETTE_VALIDATION.md) documente les quinze oracles
financiers supplémentaires sur cette trame, puis son installation comme modèle
initial de l'application. Les copies historiques et les reçus restent conservés.
