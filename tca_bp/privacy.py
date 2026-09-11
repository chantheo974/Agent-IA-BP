"""Repérer les fragments documentaires privés sans publier leurs valeurs."""
from __future__ import annotations

import hashlib
import re
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


PRIVATE_TOKEN_HASHES = frozenset({
    '10b05c446ea776cdcae1ab10f5dcdbad5eeb9250a8b6f62752e6d4e755850fab',
    '197316ef3e74b4f9c280bf7eee7184eaace168365e12f1face6a31a08e2f23f9',
    '13c24edf86a2446c258e7d2ec06d3ed95dc059c619d6be334b2f5674b2b650cc',
    'd066f8c757b4cba13d3c8a21a2fb369d927df06c52b93624e872075da6de37d4',
    '37f6cfd2f17342f54c13ebe070b4b31abcd77927824bcf672dbdb48790a53ef6',
    '10e7cb810d59691ee0357576994c977731198ef9d6567407fd545f9624f5ac06',
})

REMOVED_DOCUMENTARY_HASHES = frozenset({
    '113af3a3af912f31e400f398ac7d336b4b5eb563002292d05155954b35c585e8',
    '207eb043f4ccbd8e68c8ca6b78b67f4613409556bc0ae89330a433a0c674131c',
    '2377d6a4f04d712801088f3739acd74f574daabaeb4a09675813a74ddf1858a0',
    '248db4fe3e04343d8da2a60fa3ade0a034bc0809dc671f2195aa9bdc14abf341',
    '275b023e5636108630900b4789282a15109de06b941b0be6f1f45449265b233d',
    '285ebbfa01c4ca227cdd65a00f9848f31d7396dd1629448aa43b77cda296ce43',
    '2b884c924669211fccc8ba7bb1c0daec9f859edfa488fbbd2225385b267e7df6',
    '44c1a8d16befe7bcd42e8571cb1f67db39350eff881445f51650b51e0f026dab',
    '677a40dfd325c137a983b38ed9baa95f8c99a54c2baac8438cf3f46cb101238d',
    '73911dad8e2a0c54235f8cb9aa7954c956e19da42d4635a30c12b576a880b9df',
    '92ee187287bbff6a2cdf589b2d82540c17c8654edfbbe837f91b56553ebcb1f1',
    'a030ee2fe791a0afa3c94eb014dbf7ac5735ec01c7be6c102918efc5d4646847',
    'a678860d2c2e5abb41302689d823cc02a1c332096dad924657a108c0fca24bba',
    'ad357221f1208718e7568bd0e052eeec856d31aa032ce8f86fe69f0e4de38727',
    'd21b14ed0e460ee3a32e582edf744e4dbbd675bfeda9d1060f026782fe0b82bd',
    'd82ccc84ffab4c65308b362fec6bba685ae1745f57987764a254cb56c80a445e',
    'db23d199eeaa3755d9f54e87a282abb5f1afb0adc4ca3ff4a52b6e428767c373',
    'e49a4cc75dc7e99b87dfd96a0fa78e50eace63f8f1c0a8aaf58ef80808e06328',
    'ed8e7475c49746d26bef4b69aeb73a499da84acda20a5abacbb8e2e622b25985',
    'f1c2e0bdea12c4c387784dd154a42b9c7ed5c53e802abf59e964752d80c3b516',
    'faf587065820c4d45356f9bb4b145edbe58d2713ff9790b902ab7359b2fa868a',
})


def private_fragment_found(text: str, fingerprints=None) -> bool:
    """Ponctuation finale et initiale ponctuée sont deux cas distincts.

    Conserver les candidats historiques (initiales incluses) ET les mots sans
    ponctuation évite que « NOM. » échappe à l'empreinte de « nom ».
    """
    if not text or not text.strip():
        return False
    if fingerprints is None and hashlib.sha256(text.encode('utf-8')).hexdigest() in REMOVED_DOCUMENTARY_HASHES:
        return True
    hashes = PRIVATE_TOKEN_HASHES if fingerprints is None else fingerprints
    normalized = ''.join(c for c in unicodedata.normalize('NFKC', text).casefold()
                         if unicodedata.category(c) != 'Cf')
    candidates = set()
    for tokens in (re.findall(r'\w+\.?', normalized), re.findall(r'\w+', normalized)):
        candidates.update(tokens)
        candidates.update(' '.join(tokens[i:i+2]) for i in range(len(tokens)-1))
    return any(hashlib.sha256(token.encode('utf-8')).hexdigest() in hashes for token in candidates)


def audit_workbook_documentation(path: Path) -> dict:
    """Scanner tous les composants XML textuels, y compris les cellules masquées.

    Le rapport expose uniquement la localisation ; jamais le texte détecté.
    Le VBA binaire est vérifié séparément par le protocole de scellement.
    """
    hits, parts = [], 0
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(('.xml', '.rels', '.vml')):
                continue
            parts += 1
            current_cell = None
            with archive.open(name) as stream:
                for event, node in ET.iterparse(stream, events=('start', 'end')):
                    tag = node.tag.rsplit('}', 1)[-1]
                    if event == 'start':
                        if tag == 'c' and re.fullmatch(r'[A-Z]{1,3}[1-9][0-9]*', node.get('r', '')):
                            current_cell = node.get('r')
                        continue
                    location = {'part': name, 'element': tag}
                    if current_cell:
                        location['cell'] = current_cell
                    text = node.text or ''
                    if tag == 'f':
                        # Les références et opérateurs sont des identifiants
                        # techniques ; les chaînes de formule sont affichables.
                        text = ' '.join(re.findall(r'"((?:[^"]|"")*)"', text))
                    if text and not text.replace('.', '', 1).replace('-', '', 1).isdigit() and private_fragment_found(text):
                        hits.append({**location, 'kind': 'text'})
                    for key, value in node.attrib.items():
                        if private_fragment_found(value):
                            hits.append({**location, 'attribute': key, 'kind': 'attribute'})
                    if tag == 'c':
                        current_cell = None
                    node.clear()
    return {'status': 'PASS' if not hits else 'FAIL', 'xml_parts_checked': parts,
            'hits': hits, 'scope': 'Empreintes documentaires auditées, contenus XML et attributs ; VBA scellé séparément.'}
