"""Remplacements documentaires explicites issus de la revue de confidentialité.

Aucune formule économique ni clé de catalogue n’est modifiée par ce registre.
Les qualifications fiscales restantes exigent des contrôles fonctionnels séparés.
"""

DOCUMENTARY_REPLACEMENTS = {
    ('ATELIER_CIR_IS', 'B67'): 'Taux réduit retenu — qualification Oui/Non requise, sinon résultat indisponible',
    ('ATELIER_CIR_IS', 'B86'): 'Taxe additionnelle activée — statut Oui/Non requis, sinon résultat indisponible',
    ('ATELIER_CIR_IS', 'B91'): 'CFE annuelle selon avis / base documentée — montant à qualifier avant utilisation des résultats',
    ('DATA Contrats', 'A1'): 'DATA CONTRATS — registre des contrats du dossier',
    ('DATA Contrats', 'A2'): 'Un contrat = une ligne. Les objectifs commerciaux se renseignent dans Assumptions ; les contrats signés et probables sont documentés dans ce registre. Saisir uniquement les champs autorisés. Les prix négociés peuvent varier d’un client à l’autre ; les colonnes de service rappellent le tarif de référence et l’écart.',
    ('KPI Dashboard', 'B12'): 'Livraisons de l’offre 05',
    ('Contrôles', 'B25'): 'Trésorerie d’ouverture retenue — source et date à documenter (€)',
    ('Charges_Externes', 'A54'): 'Documenter les charges externes et leurs inducteurs : base fixe, effectif, volumes, chiffre d’affaires, actifs et stocks. Examiner leur évolution avec l’activité et éviter les doublons avec les coûts directs et les charges de personnel. Toute comparaison sectorielle doit citer une source adaptée au dossier.',
    ('Charges_Externes', 'M32'): 'Surface louée et coûts immobiliers à documenter selon les locaux, effectifs et moyens nécessaires.',
    ('Effectifs', 'I16'): 'Salaire brut annuel (EUR, base premier exercice du modèle)',
    ('Modèle financier', 'B240'): 'Détail hérité des cinq premiers exercices ; total et ventilation complète dans Revenue.',
    ('Valorisation', 'E107'): 'Le mode Manuel utilise le taux documenté saisi en D108. Structure cible utilise le D/E saisi. Itération utilise les fonds propres économiques issus du DCF.',
    ('Compte de Résultat', 'B93'): 'Volume cumulé issu du module commercial (unité et périmètre à qualifier)',
    ('KPI Dashboard', 'B9'): 'Revenus des offres 06 à 08 (récurrence à qualifier)',
    ('Revenue', 'A275'): 'Base installée consolidée : déclenche le seuil de l’offre 06 et l’assiette de maintenance de l’offre 07 après la garantie. Qualifier ces règles avant d’activer ces offres pour le dossier.',
    ('Sensi TCA', 'B17'): 'COMPARAISON AVEC UNE RÉFÉRENCE DU DOSSIER',
    ('Sensi TCA', 'D18'): 'CA de référence',
    ('Sensi TCA', 'G18'): 'Trésorerie de référence',
    ('Contrôles', 'B114'): 'Sensibilité : écart de CA depuis la référence enregistrée (€)',
    ('Contrôles', 'B115'): 'Sensibilité : écart de trésorerie depuis la référence enregistrée (€)',
    ('CALCUL_CIR', 'A1'): 'CALCUL DE L’ASSIETTE DU CIR — règles datées, éligibilité et applicabilité à qualifier',
    ('CALCUL_CIR', 'A23'): 'CALCUL DE L’ASSIETTE — à interpréter après qualification fiscale',
    ('DATA COGS', 'A2'): 'Choisir un mode de coût pour chaque offre active : Manuel (coût unitaire explicite), Cible (marge brute documentée par exercice actif) ou Catalogue (composition documentée). Le calendrier peut couvrir dix exercices, soit 120 mois. Les charges de personnel sont calculées dans Effectifs : éviter leur double compte dans les coûts directs.',
    ('BFR', 'A33'): 'Des effets de fin d’horizon peuvent modifier le BFR de clôture. Examiner les créances, avances, stocks, dettes et conditions futures du dossier. Qualifier les paramètres et contrôler la norme permanente avant d’utiliser le DCF.',
}

REMOVED_DOCUMENTARY_HASHES = {
    '4349ec7665f1bfa509f5eed849ecaf1a5db571d9db3bd74cbdd5aee935d9a206',
    '5c47fe26bd317c022d4ad52e4b0f24910d8aee77b447fc1772de01ce55833de2',
    '03ee0deb0503f3031210e11bf6d01525c7ab3154d8a6d77df3cf5a4aab0ec888',
    'a678860d2c2e5abb41302689d823cc02a1c332096dad924657a108c0fca24bba',
    '207eb043f4ccbd8e68c8ca6b78b67f4613409556bc0ae89330a433a0c674131c',
    'faf587065820c4d45356f9bb4b145edbe58d2713ff9790b902ab7359b2fa868a',
    '113af3a3af912f31e400f398ac7d336b4b5eb563002292d05155954b35c585e8',
    'd21b14ed0e460ee3a32e582edf744e4dbbd675bfeda9d1060f026782fe0b82bd',
    '2b884c924669211fccc8ba7bb1c0daec9f859edfa488fbbd2225385b267e7df6',
    '92ee187287bbff6a2cdf589b2d82540c17c8654edfbbe837f91b56553ebcb1f1',
    '285ebbfa01c4ca227cdd65a00f9848f31d7396dd1629448aa43b77cda296ce43',
    'd82ccc84ffab4c65308b362fec6bba685ae1745f57987764a254cb56c80a445e',
    'ad357221f1208718e7568bd0e052eeec856d31aa032ce8f86fe69f0e4de38727',
    'ed8e7475c49746d26bef4b69aeb73a499da84acda20a5abacbb8e2e622b25985',
    '73911dad8e2a0c54235f8cb9aa7954c956e19da42d4635a30c12b576a880b9df',
    '275b023e5636108630900b4789282a15109de06b941b0be6f1f45449265b233d',
    '44c1a8d16befe7bcd42e8571cb1f67db39350eff881445f51650b51e0f026dab',
    'a030ee2fe791a0afa3c94eb014dbf7ac5735ec01c7be6c102918efc5d4646847',
    '248db4fe3e04343d8da2a60fa3ade0a034bc0809dc671f2195aa9bdc14abf341',
    '2377d6a4f04d712801088f3739acd74f574daabaeb4a09675813a74ddf1858a0',
    'f1c2e0bdea12c4c387784dd154a42b9c7ed5c53e802abf59e964752d80c3b516',
    'db23d199eeaa3755d9f54e87a282abb5f1afb0adc4ca3ff4a52b6e428767c373',
    '677a40dfd325c137a983b38ed9baa95f8c99a54c2baac8438cf3f46cb101238d',
    'e49a4cc75dc7e99b87dfd96a0fa78e50eace63f8f1c0a8aaf58ef80808e06328',
}
