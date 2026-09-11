# Versions de modèle et dossiers

Chaque nouveau dossier conserve l'identifiant du modèle, le SHA-256 de sa trame, celui de son schéma et une référence calculée sur l'ensemble de ses composants archivés. Une archive locale dans `modeles/` est partagée par les dossiers utilisant exactement les mêmes composants. Le classeur initial de chaque dossier demeure dans `versions/v0000.xlsm`.

Installer un modèle plus récent change le modèle disponible pour les nouveaux dossiers. Les dossiers existants continuent à utiliser leur archive exacte pour lire les champs, préparer et appliquer une saisie, expliquer une feuille et recalculer. Les plans, reçus et événements de calcul portent cette même référence. La suppression des anciens fichiers de développement ne supprime pas leur archive locale.

Une archive manquante ou modifiée bloque les opérations qui en dépendent. La fiche du dossier, ses sources et son historique restent consultables avec un diagnostic. L'application ne reconstruit pas une archive manquante et ne lui substitue pas le modèle courant. Le journal de création permet aussi de détecter un changement ultérieur de la référence inscrite dans le dossier.

## Dossiers créés avant l'épinglage

Les nouveaux champs de stockage restent vides pour ces dossiers. Aucun rapprochement n'est déduit du seul nom du modèle. Dans **Vue d'ensemble**, **Rattacher l'ancien modèle** permet de choisir le répertoire de cette version, puis de vérifier et confirmer le rattachement. Les opérations utilisent le service commun, également disponible par API :

```python
from pathlib import Path
from tca_bp.service import Application

app = Application(data_dir=Path("espace_de_donnees"))
app.bind_legacy_case("identifiant_du_dossier", Path("ancienne_version_du_modele"))
```

Cette opération exige une version antérieure complète, la copie `v0000.xlsm` identique à sa trame, un journal de création cohérent et un classeur courant intact et conforme. Elle archive la version et ajoute les références et un événement de rattachement ; elle ne change ni le classeur ni sa révision. En l'absence de ces preuves, le rattachement est refusé. Un plan ancien sans références exactes doit être préparé à nouveau.

Le rattachement ne permet pas de migrer un dossier déjà épinglé. Il n'existe pas de procédure de migration automatique entre deux modèles. Une éventuelle migration métier doit faire l'objet d'un développement et d'une validation distincts.

La commande équivalente est `python -m tca_bp bind-model identifiant_du_dossier --model-dir ancienne_version_du_modele`. En MCP, `bp_bind_legacy_model` prend `case_id` et `model_dir`. Le répertoire doit être explicitement désigné par l'utilisateur. Pour les fiches et agents, utiliser `agents --case identifiant_du_dossier`, `explain Control --case identifiant_du_dossier` ou le paramètre MCP `case_id` de `bp_agents` et `bp_explain`. L'interface passe automatiquement le dossier sélectionné.

## Périmètre des contrôles

Les tests `tests/test_model_versions.py` utilisent des classeurs OOXML fictifs et vérifient la coexistence de formules et de contraintes distinctes, les changements de source, l'intégrité des archives, la reprise, les reçus et les refus de migration. Ils n'exécutent ni Excel ni VBA et ne constituent pas une validation économique des modèles.

Les empreintes et les journaux détectent les modifications par rapport aux références conservées. Ils ne constituent pas une signature d'un tiers ni une protection contre un acteur capable de falsifier simultanément toute la base locale et ses archives. Sauvegarder l'espace de données complet, incluant `modeles/`, la base et les dossiers.
