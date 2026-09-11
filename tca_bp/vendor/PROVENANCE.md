# Dépendances locales

Le moteur de saisie est adapté du pack de référence fourni localement. Les
sources originales restent intactes dans le dossier d'exemple et ne sont pas
nécessaires à l'exécution lorsque les artefacts génériques sont construits.

`vendor/olefile/olefile.py` est le lecteur OLE Python 3 utilisé uniquement en
lecture. Sa licence est conservée. L'ancienne variante Python 2, inutilisée et
incompatible avec Python 3.14, n'est pas distribuée. Le lecteur d'empreintes
contrôle les trois fichiers effectivement nécessaires avant de les charger.

Aucune dépendance n'est installée et aucun code VBA n'est exécuté par ce moteur.
