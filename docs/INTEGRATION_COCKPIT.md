# Intégration du cockpit visuel dans le prototype local

Travail autorisé le 18 septembre 2026 : reprendre les réalisations de `visuel web test` dans l'application locale et publier les sources correspondantes sur GitHub.

Les trois documents fournis (plan de suite, passation et revue UX/UI) décrivent une démonstration et les fonctions restant à construire. Ils ne constituent pas des preuves de raccordement au moteur. Leur lecture est rapprochée du code réel pour suivre les critères F0–F5 et C0–C5.

## Sources et architecture

- Le dossier fourni reste intact. Son inventaire initial est conservé localement dans `runtime/cockpit_visual_source_20260918.json`.
- La copie applicative est `frontend/src/cockpit`. Le style pastel, les composants de présentation, les icônes Iconoir, le compagnon, les parcours et préférences sont conservés.
- Vite produit des fichiers statiques servis par FastAPI. Node reste un outil de développement ; les configurations Cloudflare/Vinext de la maquette ne deviennent pas des dépendances du pack local.
- `/demo` désigne explicitement des données fictives, avec un stockage navigateur distinct. Les nouveaux dossiers réels ne prennent jamais Atlas, ses courbes ou ses métriques comme valeur de secours.
- Le cockpit connecté utilise un contrôleur unique : dossiers, sources, événements, intentions persistantes, brouillon, aperçu, approbation, travaux et versions restent ceux du service existant.
- Les écritures ordinaires du cockpit sont limitées aux champs métier reconnus côté serveur. Le mode de maintenance structurelle reste distinct. Aucun calcul financier n'est réimplémenté dans React.
- Les sources sont publiables ; les classeurs, archives de modèle, dossiers clients, clés, historiques de conversations et reçus locaux ne sont pas ajoutés au dépôt public.

## Suivi vérifiable

| Lot | État | Vérification requise |
|---|---|---|
| F0, état partagé et migration | Terminé | Migration v1 et séparation de stockage : 15 tests d'état, recette UI détaillée |
| F1, 33 feuilles | Terminé | 33 destinations ouvertes avec métier/grille/liens dans la recette démo à 44 contrôles |
| F2, Ventes démo | Terminé | Deux variantes Atlas, invalidation des autres combinaisons, simulation/adoption/restauration testées |
| F3, cinq autres thèmes démo | Terminé | Cinq cycles thématiques nommés, adoption puis relecture après actualisation |
| F4, parcours transversaux démo | Terminé | Faits fictifs, réalisé, aperçus explicitement web et compagnon contextuel vérifiés |
| F5, recette visuelle | Terminé | 48 contrôles UI, 3 gardes finales ; palettes, clavier, 320–1440 px, zoom et préférences |
| C0, dossier réel | Terminé | Recette navigateur/API réelle sur dossier fictif isolé, identité et révision conservées, aucune valeur Atlas |
| C1, lectures moteur | Terminé | Projections qualifiées liées au même instantané ; références déplacées/renommées contrôlées. Navigateur réel sur copie Excel calculée : trois flux commerciaux, trésorerie, annuels, unités et cellules sources concordants |
| C2, Ventes connecté | Terminé | Excel natif : 12 contrôles et 17 oracles indépendants ; copie calculée isolée, conservation, aperçu approuvé, adoption puis restauration traçable |
| C3, autres thèmes connectés | À vérifier | Raccord des registres/paramètres implémenté ; contrôles HTTP par thème et oracles historiques du moteur. Une recette native spécifique de chaque thème à travers le cockpit reste à compléter |
| C4, imports et rapports | À vérifier | Raccord implémenté aux services existants et sources du vrai serveur testés ; nouvelle recette de 37 contrôles avec quatre vrais fichiers, instantané commun, réimport identique et restauration. Le parcours navigateur complet d'import du réalisé reste à vérifier dans le nouvel habillage |
| C5, recette complète | À vérifier | Reprise, conflits, idempotence et protections testés ; essai du fournisseur IA réel en attente d'une clé locale |
| Distribution et GitHub | Terminé | Pack 0.5.0 vérifié et installé dans un nouveau répertoire avec espaces ; six espaces ouverts, 294 fichiers vérifiés, sources publiées dans la demande de fusion nº 1. Détail et limites : `LIVRAISON_0.5.0.md` |

La livraison 0.4.0 antérieure reste conservée. Elle ne prouve pas le fonctionnement des nouvelles routes. La connexion réelle à un fournisseur IA nécessite toujours une clé configurée localement ; aucun essai simulé ne remplace cette validation.

Preuves et limites : `RECETTE_COCKPIT_0.5.0.md` et `RECETTE_COCKPIT_DEMO_2026-09-18.md`. Le statut des lignes C3, C4 et C5 désigne une limite de recette, pas un remplacement des opérations par des notifications fictives. Les calculs restent ceux du moteur et les résultats non qualifiés ne sont pas affichés comme exploitables.
