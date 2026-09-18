> Archive documentaire de conception du 15–16 septembre 2026, publiée sans chemins personnels. Les états décrits ci-dessous précèdent l’intégration. Voir [le suivi actuel](../INTEGRATION_COCKPIT.md).

# Revue UX et UI du prototype

Revue du 15 septembre 2026. Périmètre : prototype local uniquement, sans connexion au moteur financier ni publication.

## Direction visuelle conservée et affinée

- Pastels lumineux, contrôles en verre, compagnon animé et courbes multicolores conservés.
- Les couches décoratives restent derrière les cartes ; les chiffres et actions ne se masquent plus mutuellement.
- Accueil recentré sur une décision et une prochaine action. Titres plus courts, espacements réguliers, chiffres mieux hiérarchisés.
- Barres et boutons adaptés au texte à 16 px, avec cibles d’au moins 44 px et focus contrasté.
- En-tête flottant, accès à l’accueil par la marque, notifications claires et refermables.
- Les données enregistrées sont chargées avant l’affichage des pages pour éviter le flash de chiffres ou de progression issus de l’état initial.
- Comparaisons alignées sur ordinateur ; cartes linéaires sur téléphone. Onglets du mode expert entièrement visibles à 320 px.

## Corrections de parcours

- Étapes de personnalisation cliquables avec URL propre, précédent/suivant du navigateur, conservation des saisies entre étapes et déplacement du focus.
- Enregistrement accessible à chaque étape en mode révision ; confirmation avant de quitter par les liens du site ou le bouton de sortie. Avertissement lors d’une fermeture ou actualisation avec modifications.
- États de préparation et erreurs du logo explicités, retrait du logo et exemples de documents disponibles.
- Saisies numériques intermédiaires isolées du brouillon, limites explicites et dernière valeur valide conservée après erreur.
- Simulation obligatoire avant conservation ou application. Toute modification invalide les résultats précédents.
- Historique complet : les scénarios ne sont plus supprimés au-delà de trois copies ; toutes les versions et décisions restent accessibles.
- Restauration d’une version sans perte du brouillon précédent, récupérable par l’annulation.
- Recommandation Atlas appliquée en un seul essai annulable, avec toutes ses conditions annoncées.
- Préparer une règle déjà prête ne duplique plus les messages ni ne périme inutilement la simulation.
- Suivi mensuel : distinction entre encaissements, ventes, réalisé et projections. Dates corrigées en 2026 et exemple fictif utilisable sans déposer de fichier.
- Graphiques : info-bulles lisibles, repères mensuels et parcours au clavier ; exemples financiers explicitement illustratifs.
- Compagnon : conversation annoncée aux aides techniques, envoi vide désactivé, composition de texte prise en compte et zone de saisie à hauteur limitée.

## Vérifications réalisées

- Inspection des dix routes à 1440, 1024, 390 et 320 px dans le navigateur intégré. Débordements repérés dans l’historique et les onglets expert corrigés puis revérifiés. La grille experte conserve volontairement son défilement horizontal sur écran intermédiaire.
- Parcours guidé et automatique, ouverture des impacts, lancement de comparaison et navigation vers son résultat.
- Lecture des courbes au clavier : mois et valeur exposés, notamment novembre 2026 / 227 k€ pour le scénario Atlas initial. Info-bulle contenue à 320 px.
- Modification temporaire du prénom, étape suivante, retour navigateur : saisie conservée. Avertissement de sortie vérifié puis informations d’origine rétablies sans enregistrer de nouvelle identité.
- Trois palettes sélectionnées et prévisualisées ; palette d’origine rétablie. Volet du compagnon et contrôles tactiles examinés sur téléphone.
- Dix tests de transitions d’état réussis, sans accéder au stockage de l’utilisateur : simulation fraîche, application unique, conservation de quatre variantes, absence de doublons, restauration, annulation, valeurs invalides, recommandation atomique, calcul déterministe et import mensuel isolé.
- Typage, lint des sources applicatives et tests, build et dix réponses HTTP 200.
- Empreintes des 28 fichiers du front d’origine identiques avant et après.

Les tests d’état utilisent un harnais de hooks déterministe sans effets navigateur. Ils complètent les essais UI, sans remplacer un test d’intégration React complet.

## Limites à garder visibles

Le modèle reste une démonstration à valeurs préparées. Les courbes et calculs ne constituent pas des résultats financiers réels. Aucune connexion au classeur ni génération effective Excel/PDF n’a été ajoutée.

Cette revue n’est pas une certification d’accessibilité : essais sur iPhone/Safari réel, lecteur d’écran vocal et zoom natif à 200 % restent à mener. Les règles de réduction des animations, de transparence et de repli sans flou sont conservées dans les styles.

Le lint global du socle contient des signalements préexistants dans les composants UI fournis ; le contrôle des sources applicatives modifiées est propre.

## Relancer les contrôles

Depuis ce dossier :

```text
node --test tests/demo-state.test.mjs
pnpm exec tsc --noEmit
pnpm exec oxlint app components/cockpit lib tests/demo-state.test.mjs
pnpm run build
```

Prévisualisation : http://localhost:3000/
