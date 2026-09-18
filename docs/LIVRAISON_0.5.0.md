# Livraison TCA BP Web 0.5.0

Cockpit intégré et pack local préparé le 18 septembre 2026. Archive : `dist/TCA_BP_Web_local_0.5.0.zip`, **45 666 923 octets**.

SHA256 : `1157abd0cecbc8a31029acbe99224751578fae754a472f76b8a7fd5f5da491e7`.

## Utiliser le prototype

1. Extraire le ZIP dans un nouveau dossier, exécuter `Installer_TCA_BP_Web.ps1`, puis `Lancer_TCA_BP_Web.cmd`.
2. Créer ou choisir un dossier dans le cockpit. Les six thèmes, documents, simulations, suivi mensuel, livrables et compagnon utilisent le service local existant. Consulter `ATELIER_WEB.md` pour reprendre un stockage existant avec `--data-dir`.
3. Depuis une feuille, préparer une modification sourcée, examiner le brouillon et ses impacts, simuler sur une copie, puis approuver l'aperçu avant adoption. Les valeurs calculées et les formules restent protégées dans le parcours ordinaire.

Python 3.14 et Excel sont nécessaires. Node n'est pas nécessaire à l'utilisation. `/demo` contient des exemples explicitement fictifs ; `/atelier` conserve la maintenance détaillée.

## Distribution vérifiée

L'installation a réussi dans un **nouveau répertoire avec espaces**, sous Python 3.14.3. Les **294 fichiers du manifeste** correspondent exactement aux **295 entrées du ZIP**, manifeste inclus. Les six scripts PowerShell extraits passent le parseur ; l'installation n'appelle pas npm. Le navigateur ouvre les six espaces du cockpit, le catalogue retrouve les 33 feuilles et les 33 agents. Les icônes sont servies avec leur licence. Le modèle initial corrigé reste distinct du modèle générique et correspond aux empreintes du manifeste.

L'essai d'installation ne crée aucun travail Excel ou IA. Son serveur est arrêté. Le contrôle financier est distinct : simulation native avec 12 contrôles et 17 oracles, suivie de 37 contrôles des quatre exports, du réimport identique et de la restauration. Le navigateur a ensuite vérifié les chiffres de cette copie calculée, leurs périodes, unités et cellules sources. Les derniers tests comprennent 65 parcours navigateur et 86 contrôles Python ciblés sur sources figées, en complément de la suite complète de 702 tests décrite avec sa limite d'empreinte dans `RECETTE_COCKPIT_0.5.0.md`.

Preuves locales :

- `runtime/validation_distribution_0.5.0.json` : reçu extérieur lié aux octets du ZIP, au build et aux vérifications.
- `runtime/Installation web cockpit 050 20260918_212909 7e6201/recette-installation/validation.json` : installation et lancement.
- `runtime/recette_cockpit_front_20260918_2125/validation.json` : tests navigateur, deux recettes serveur réel et captures.
- `runtime/cockpit_pack_source_parity.json` : 177 fichiers du produit identiques aux fichiers du pack, dont le backend, l'interface compilée et les lanceurs.
- `runtime/cockpit_preservation_final.json` : 175 fichiers visuels d'origine inchangés et pack 0.4.0 conservé à l'identique.

La matrice de suivi embarquée dans le ZIP est antérieure à sa vérification d'installation. Ce reçu extérieur et le présent document consignent le résultat final, sans modifier rétroactivement l'archive vérifiée.

## GitHub et périmètre restant

Les sources sont publiées dans la branche `codex/cockpit-visuel-local` et la [demande de fusion nº 1](https://github.com/chantheo974/Agent-IA-BP/pull/1). Le commit de code livré est `2c1aaabb9da5c80e2bcc2144a1b84c5663df48ff`. Les commits documentaires suivants ajoutent les reçus de livraison et le suivi. Les classeurs, modèles privés, clés et dossiers d'exécution ne sont pas publiés. La demande de fusion reste en brouillon ; elle n'est pas fusionnée dans `main`.

Les limites restent explicites : appel réel au fournisseur IA à tester après saisie d'une clé dans les réglages ; recette native de chaque thème hors ventes via le nouvel écran à compléter ; import complet du réalisé non rejoué dans le nouvel habillage. Les services correspondants sont raccordés et disposent de tests ciblés, mais ces tests ne remplacent pas ces recettes complètes. Une nouvelle tentative d'ajout d'une source documentaire après perte de réponse peut encore créer une entrée documentaire supplémentaire, sans doubler une écriture financière.

Pour tes retours, relever le dossier et la révision, l'action, le résultat attendu et le résultat obtenu. Les originaux, le pack 0.4.0, les versions et les diagnostics restent conservés.
