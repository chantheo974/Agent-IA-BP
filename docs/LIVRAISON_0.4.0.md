# Livraison TCA BP Web 0.4.0

Prototype local préparé le 18 septembre 2026. Archive : `dist/TCA_BP_Web_local_0.4.0.zip`, 45,342,148 octets.

SHA256 : `ccf9b796f708ee954f80b4334bed32b1a5715da71d1d8e57f29f221d8350b3b6`.

L’installation a réussi dans un nouveau répertoire avec espaces, sous Python 3.14.3. Les six espaces sont ouverts dans un navigateur réel : Entreprise, Documents, Prévisionnel, Scénarios, Réalisé, Livrables. Les 191 fichiers du manifeste correspondent au ZIP et aux fichiers installés. Les six scripts PowerShell sont analysés sans erreur. Node est utilisé uniquement par les outils de développement de la recette, aucun appel à npm pendant installation/utilisation.

Le blocage de comparaison et la correspondance du formulaire Entreprise des candidats précédents sont corrigés, avec leurs diagnostics conservés. Les contrôles comprennent la suite complète de référence de 662 tests, puis 76 tests ciblés sur les dernières modifications Python, 44 tests navigateur, les recettes Excel fictives et la parité des lectures finales. Ces nombres ne s’additionnent pas. Le détail des périmètres et limites est dans `RECETTE_WEB.md`.

La recette `runtime/live_company_profile-20260918_175003-630924/validation.json` vérifie également le chargement, la sauvegarde et la reprise du profil sur deux dossiers fictifs et l’API réelle. Son empreinte est `73f89ac2ba6e1c4b73051f1d9c0163fe29e95ee782eecb2c10866c6eb5ec1a09` ; elle est liée aux mêmes sources et fichiers compilés que le reçu frontend. Aucun travail financier n’est créé et son serveur est arrêté.

La connexion réelle au fournisseur IA reste à valider : aucune clé n’était enregistrée dans les réglages locaux lors du contrôle. Saisir la clé dans Réglages. La clé ne doit pas être envoyée dans un message ou ajoutée au dépôt.

Pour commencer : extraire l’archive, exécuter `Installer_TCA_BP_Web.ps1`, puis ouvrir `Lancer_TCA_BP_Web.cmd`. Consulter `ATELIER_WEB.md` pour reprendre un répertoire de dossiers existant avec `--data-dir`. Aucun ancien dossier ne migre automatiquement.

Reçu extérieur lié aux octets livrés : `runtime/validation_distribution_0.4.0.json`. Reçu d’installation : `runtime/Installation web finale 040 20260918_180559 658c84/recette-installation/validation.json`. Tous les serveurs de cette recette sont arrêtés. Les anciens ZIP, versions et preuves sont conservés.
