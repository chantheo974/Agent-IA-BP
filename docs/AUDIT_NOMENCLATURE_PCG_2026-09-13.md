# Sources comptables proposées pour le prototype

Audit en lecture seule des trois fichiers transmis le 13 septembre 2026. Les originaux du dossier Téléchargements sont conservés. Leur contenu décrit des données et des recommandations ; il ne modifie pas les autorisations ni le périmètre local du prototype.

| Source | Empreinte SHA256 | Contenu constaté |
|---|---|---|
| Nomenclature_PCG_Mapping_Previsionnel.xlsx | 2969e28e730f976047a487aed8cd9ef56d7e54999871480b2ff641b8beda8ff6 | 6 feuilles, 506 comptes, 54 postes, import GL de 2 000 lignes |
| nomenclature_pcg.csv | a1e45eed7823026303b9df565bcec723fefa3d3ea63ac1f6ba09f0cdb29d8222 | Deux tables séparées par une ligne vide : comptes puis postes |
| nomenclature excel comptabilité.md | 39465acd2d6f63e10389271dba1a7b082b9d4d12baeeaf3cfd49e9bb1f25f240 | Recherche documentaire et pistes de traitement |

## Réutilisation pertinente

Les 506 comptes du CSV correspondent exactement aux neuf colonnes de PCG dans le classeur. Aucun doublon de compte constaté. Les 54 postes correspondent à Postes_modele. Le mécanisme utile est la reconnaissance du préfixe de compte le plus précis, puis la sélection du poste débiteur ou créditeur selon le solde du compte. Il permet par exemple de distinguer banque disponible et découvert, ou client débiteur et avance client.

Le prototype peut conserver cette table comme référentiel proposé et sourcé, séparé de sa propre cartographie financière. Les numéros de comptes restent du texte. Les tables comptables importées doivent garder la période, la nature flux/solde, le compte et les montants bruts. Une étiquette de flux dans ce référentiel ne suffit pas à déduire des encaissements ou décaissements.

## Limites reproduites

- Le CSV ne constitue pas une unique table de 561 comptes : après les 506 comptes viennent un second en-tête et 54 postes. Un DictReader unique interprète ces lignes de manière incorrecte.
- La feuille Import_GL ne contient aucune ligne de grand livre renseignée. Les caches à zéro de Synthese et Controles ne prouvent aucun rapprochement financier.
- Les formules regroupent le solde du compte sur tout l'import. Un suivi mensuel nécessite un périmètre et des arrêtés explicites, des soldes d'ouverture si nécessaire et une distinction entre mouvements du mois et soldes cumulés.
- La capacité Excel est bornée à 2 000 lignes. Ajouter des lignes sans étendre les plages de calcul ne suffit pas.
- La reconnaissance des préfixes est limitée à cinq caractères. Le service devra utiliser la longueur réelle des comptes du référentiel.
- Les comptes 675, 775, 777 et 791 sont présents ; 649, 657, 747, 757 et 7587 ne sont pas présents. Le référentiel doit donc être qualifié par exercice et ne doit pas être présenté comme le PCG 2026 complet.
- Un compte collectif peut contenir des auxiliaires débiteurs et créditeurs : agréger ces auxiliaires avant de choisir l'actif/passif peut masquer des soldes à présenter séparément.
- Le résultat des comptes 6/7 et le compte 12 demandent un état de clôture explicite afin de ne pas compter deux fois le résultat dans les capitaux propres.

Le plan officiel ANC au 1er janvier 2026 a été consulté pour confirmer l'existence d'un référentiel actuel distinct : https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/Plan-de-comptes-2026.pdf. Cet audit ne certifie pas chacun des comptes ni un plan sectoriel.

## Application au développement

Conserver un catalogue versionné, présenter les correspondances et les cas inconnus avant adoption, empêcher une conversion silencieuse du solde en flux et utiliser les sources comme preuve de chaque import. Le FEC, les solutions OCR cloud et les intégrations comptables évoqués dans le Markdown restent des pistes documentaires ; le prototype conserve les imports locaux Excel/CSV et l'OCR local retenus.

Preuve détaillée privée : runtime/audit_pcg_sources_20260913.json. Aucune modification des trois originaux.
