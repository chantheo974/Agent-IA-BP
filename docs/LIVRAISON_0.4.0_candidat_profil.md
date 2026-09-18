# Livraison TCA BP Web 0.4.0

Prototype local préparé le 13 septembre 2026. Archive : `dist/TCA_BP_Web_local_0.4.0.zip`, 45,339,658 octets.

SHA256 : `a8a2ffb37e6cb95e95fa4e25a950eb2af7f953c18632db04edf977a4fd79b5fe`.

L’installation a réussi dans un nouveau répertoire avec espaces, sous Python 3.14.3. Les six espaces sont ouverts dans un navigateur réel : Entreprise, Documents, Prévisionnel, Scénarios, Réalisé, Livrables. Les 191 fichiers du manifeste correspondent au ZIP et aux fichiers installés. Les six scripts PowerShell sont analysés sans erreur. Node est utilisé uniquement par les outils de développement de la recette, aucun appel à npm pendant installation/utilisation.

Le blocage de comparaison du candidat précédent est corrigé et ses diagnostics conservés. Les contrôles comprennent la suite complète de référence de 662 tests, puis 76 tests ciblés sur les dernières modifications, 39 tests navigateur, les recettes Excel fictives et la parité des lectures finales. Ces nombres ne s’additionnent pas. Le détail des périmètres et limites est dans `RECETTE_WEB.md`.

La connexion réelle au fournisseur IA reste à valider : aucune clé n’était enregistrée dans les réglages locaux lors du contrôle. Saisir la clé dans Réglages ; elle ne doit pas être envoyée dans un message ou ajoutée au dépôt.

Pour commencer : extraire l’archive, exécuter `Installer_TCA_BP_Web.ps1`, puis ouvrir `Lancer_TCA_BP_Web.cmd`. Consulter `ATELIER_WEB.md` pour reprendre un répertoire de dossiers existant avec `--data-dir`. Aucun ancien dossier ne migre automatiquement.

Reçu extérieur lié aux octets livrés : `runtime/validation_distribution_0.4.0.json`. Reçu d’installation : `runtime/Installation web finale 040 20260913_081737 c9e633/recette-installation/validation.json`. Tous les serveurs de cette recette sont arrêtés. Les anciens ZIP, versions et preuves sont conservés.
