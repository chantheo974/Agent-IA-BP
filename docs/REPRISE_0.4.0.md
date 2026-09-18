# Pause demandée par l’utilisateur — 13 septembre 2026

**Reprise explicitement demandée le 18 septembre 2026.** Ce document conserve l’état historique de la pause ; le suivi courant se trouve dans `TASKS.md`.

**Reprise terminée et pack livré le 18 septembre 2026.** Le défaut de sauvegarde lente est corrigé, 44 tests navigateur et la recette du profil sur deux dossiers avec API réelle sont réussis. Le nouveau `dist/TCA_BP_Web_local_0.4.0.zip` est installé et vérifié dans un dossier neuf avec espaces ; les six espaces s’ouvrent. SHA256 : `ccf9b796f708ee954f80b4334bed32b1a5715da71d1d8e57f29f221d8350b3b6`. Compte rendu courant : [LIVRAISON_0.4.0.md](LIVRAISON_0.4.0.md), preuve : `runtime/validation_distribution_0.4.0.json`. Les serveurs de recette sont arrêtés. L’essai réel du fournisseur IA reste en attente de clé. Les paragraphes suivants décrivent uniquement l’état historique du 13 septembre.

## Point de reprise

Le prototype est implémenté ; la dernière correction concerne le formulaire Entreprise. Le profil API possède `years`, `activity_start_month`, `business_model`, tandis que le formulaire utilisait des alias et pouvait réenregistrer les valeurs par défaut. La correction se trouve dans `frontend/src/companyProfile.ts`, `Workshop.tsx` et `workshopTypes.ts`, avec tests associés.

La campagne `runtime/frontend_delivery_040_20260913_082729/evidence.json` indique 43 tests réussis, zéro échec, sources stables et compilation reproductible. SHA du reçu : `5226af05d30552766cd6510ef59549040c72aff0c3af6897b0d68626219a902f`. Les sources et les six fichiers compilés lui correspondent au moment de la pause ; contrôler à nouveau les empreintes au redémarrage. Le test `frontend/tests/live-profile.spec.ts` est écrit mais la recette API réelle sur deux dossiers est **non exécutée**.

Dernier point signalé par la revue, **non corrigé** : si un utilisateur modifie un champ pendant un PUT lent, le retour du serveur peut effacer cette nouvelle saisie avec `setProfile(saved.profile)`. Comparer un compteur d’édition capturé à l’enregistrement, puis tester la réponse retardée. Code et compilation restent candidats.

Tous les travaux de l’agent frontend sont arrêtés ; les ports de recette 4173 et 8788 sont fermés. Aucun serveur de recette du profil réel n’a été lancé.

## Vérifications conservées

- Suite Python complète de référence : 662 tests, `runtime/validation_web_20260913_042831_e5cae9/validation.json`.
- Dernières modifications Python : 76 tests ciblés réussis, `runtime/validation_reads_final_20260913_081148_40960d/validation.json`. Sources identifiées `698820b6275420393a8bf092790b86874de895f0183c2fb71c315d0ceb4e89d0`.
- Lenteur Scénarios/Réalisé corrigée par une copie isolée du profil par lecture. Comparaison HTTP 2,618 puis 2,068 secondes, raccord 0,702 seconde, classeur inchangé : `runtime/verification_compare_http_20260913_081105/validation.json`.
- Parité des 1 010 références : `runtime/reforecast_mapping_parity_20260913_081130_f21c2e/receipt.json`.
- Parité des caches financiers : 58 contrôles, 171 fichiers conservés, `runtime/decision_read_parity_040_20260913_081250_8d4cb3/receipt.json`. Aucun nouveau recalcul ni qualification.
- Recettes Excel, réalisé, WACC/DCF, scénarios, restauration et quatre exports détaillées dans `RECETTE_WEB_0.4.0.md` ; leurs preuves restent conservées. Ne pas rejouer un calcul financier pour une correction de formulaire.

## Archives et état de livraison

Il n’existe volontairement plus de `dist/TCA_BP_Web_local_0.4.0.zip` final au moment de la pause. Les candidats sont conservés :

- `TCA_BP_Web_local_0.4.0_candidat_installation_20260913.zip`, SHA `dde496ef2ef13e2102cf855bceae10668f67e3ad3521d4490fe237f381d4db78` : lenteur Scénarios détectée.
- `TCA_BP_Web_local_0.4.0_candidat_profil_20260913.zip`, SHA `a8a2ffb37e6cb95e95fa4e25a950eb2af7f953c18632db04edf977a4fd79b5fe` : installation et navigation passent, mais le formulaire Entreprise a révélé le défaut ci-dessus.
- Le candidat préparatoire et les anciennes versions restent présents.

Le reçu d’installation du second candidat est `runtime/Installation web finale 040 20260913_081737 c9e633/recette-installation/validation.json`. Le constat visuel est dans le même dossier. Le reçu consolidé et le compte rendu ont été renommés en `runtime/validation_distribution_0.4.0_candidat_profil.json` et `docs/LIVRAISON_0.4.0_candidat_profil.md`. Ils ne valent pas livraison finale.

Le modèle initial sélectionné reste l’archive `600b94dba37046704742b1cce802a9aeefbe3ab1cb897063bbe4bdaf73dfdacc`, trame `a34426619c1515a470e92db4fcf10f70bb1a173c0b35e04349ab69bdddae6cb9`, issue de generic-v1 1.1.2. Aucune migration implicite d’un ancien dossier.

## Après autorisation de reprise

1. Vérifier les derniers fichiers/reçus et terminer le contrôle du PUT lent ; figer et tester l’interface.
2. Confirmer la recette du profil avec serveur réel et deux dossiers, sans modification financière.
3. Actualiser les documents avec `runtime/update_profile_delivery_docs.py` en lui fournissant les reçus effectivement réussis.
4. Construire un nouveau ZIP exclusif, puis utiliser `runtime/run_final_web_installation.py` avec son SHA exact. Le validateur de navigation a été renforcé pour vérifier les valeurs du profil visible.
5. Consolider avec `runtime/finalize_distribution_040.py --frontend-receipt ...`, après installation réussie ; conserver tous les candidats précédents.

La connexion IA réelle reste en attente d’une clé enregistrée dans les réglages locaux. Les originaux comptables et les neuf exemples privés sont conservés, ces neuf fichiers ne sont pas dans l’index Git. Aucun commit ni push réalisé. Le dispositif temporaire empêchant la veille a été arrêté ; `runtime/delivery_awake.stop` est présent.
