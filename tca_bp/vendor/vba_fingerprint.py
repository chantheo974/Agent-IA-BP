"""Strict, read-only fingerprint of an OLE VBA project, independent of CFB layout.

Every logical stream is included, including compiled-code/cache streams. Only
physical allocation/tree indices, padding and creation/modification timestamps
are excluded. This does not execute, decompress, rewrite or normalize VBA code.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path
import types

SCHEMA = 'isp-vba-ole-streams/v1'
COMPATIBILITY_SCHEMA = 'isp-vba-project-metadata/v1'
OLE_MAGIC = bytes.fromhex('d0cf11e0a1b11ae1')
MAX_BYTES = 16 * 1024 * 1024
VENDOR_HASHES = {
    '__init__.py': '719e959251c94a8332354270e733ff8638781bf1ec6a9f921902a0b055692456',
    'olefile.py': 'dcce514efdcbd04fa689bc920531a1985df0837c92b57fe3af0c45c46f1bbd87',
    'LICENSE.txt': '0c349bed31cd2af10983a8d95e7455e2d15744b98585b55941ca35bd70f5bcd7',
}
_vendor_module = None


def _insist(condition, message):
    if not condition:
        raise ValueError('Projet VBA : ' + message)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _vendor():
    """Verify all vendored Python files before loading exact verified source.

    Compiling the verified bytes avoids importing an unrelated installed olefile
    package or a stale/tampered bytecode cache. No installation/network is used.
    """
    global _vendor_module
    folder = Path(__file__).resolve().parent / 'vendor' / 'olefile'
    actual_py = {p.relative_to(folder).as_posix() for p in folder.rglob('*.py')}
    expected_py = {p for p in VENDOR_HASHES if p.endswith('.py')}
    _insist(actual_py == expected_py, 'ensemble des sources olefile différent du pack vérifié.')
    verified = {}
    for name, expected in VENDOR_HASHES.items():
        path = folder / name
        _insist(path.is_file() and not path.is_symlink(), 'dépendance vendue absente ou lien inattendu : ' + name)
        data = path.read_bytes()
        _insist(_sha(data) == expected, 'empreinte de dépendance incorrecte : ' + name)
        verified[name] = data
    if _vendor_module is None:
        module = types.ModuleType('_isp_verified_olefile')
        module.__file__ = str(folder / 'olefile.py')
        exec(compile(verified['olefile.py'], module.__file__, 'exec'), module.__dict__)
        _vendor_module = module
    return _vendor_module


def inventory(data: bytes) -> dict:
    """Return a canonical logical inventory; raise ValueError on an anomaly.

    Paths preserve spelling and hierarchy. Root/storage CLSID and state flags,
    every entry type, and exact logical stream sizes and hashes are protected.
    """
    _insist(isinstance(data, bytes), 'octets binaires attendus.')
    _insist(1536 <= len(data) <= MAX_BYTES, 'taille de conteneur hors bornes.')
    _insist(data.startswith(OLE_MAGIC), 'conteneur CFB/OLE requis, sans repli permissif.')
    olefile = _vendor()
    try:
        with olefile.OleFileIO(io.BytesIO(data), raise_defects=olefile.DEFECT_UNSURE) as ole:
            _insist(not ole.parsing_issues, 'anomalie détectée pendant la lecture du conteneur.')
            paths = [[]] + ole.listdir(streams=True, storages=True)
            _insist(len(paths) <= 4096, 'annuaire trop volumineux.')
            records, seen_names, seen_sids = [], set(), set()
            total_stream_bytes = 0
            for path in paths:
                key = tuple(part.casefold() for part in path)
                _insist(key not in seen_names, 'chemin en double dans l’annuaire.')
                seen_names.add(key)
                entry = ole.root if not path else ole.direntries[ole._find(path)]
                _insist(entry.sid not in seen_sids, 'entrée d’annuaire référencée plusieurs fois.')
                seen_sids.add(entry.sid)
                _insist(entry.entry_type in (olefile.STGTY_ROOT, olefile.STGTY_STORAGE, olefile.STGTY_STREAM), 'type d’entrée non pris en charge.')
                _insist(entry.namelength >= 2 and entry.namelength <= 64 and entry.namelength % 2 == 0, 'longueur de nom invalide.')
                _insist(entry.name_raw[entry.namelength - 2:entry.namelength] == b'\x00\x00', 'nom non terminé correctement.')
                _insist(entry.name and not any(ch in entry.name for ch in '/\\:!\x00'), 'nom d’entrée interdit.')
                record = {
                    'path': list(path),
                    'name': entry.name,
                    'entry_type': entry.entry_type,
                    'clsid': entry.clsid,
                    'state_bits': entry.dwUserFlags,
                }
                if entry.entry_type == olefile.STGTY_STREAM:
                    _insist(0 <= entry.size <= MAX_BYTES, 'taille de flux invalide.')
                    total_stream_bytes += entry.size
                    _insist(total_stream_bytes <= len(data), 'taille cumulée des flux incohérente avec le conteneur.')
                    stream = ole.openstream(path).read()
                    _insist(len(stream) == entry.size, 'flux tronqué.')
                    record.update(size=len(stream), sha256=_sha(stream))
                records.append(record)
            # Do not silently ignore nonempty directory records outside the tree.
            for sid, entry in enumerate(ole.direntries):
                if entry is None:
                    entry = ole._load_direntry(sid)
                if entry.entry_type != olefile.STGTY_EMPTY:
                    _insist(sid in seen_sids, 'entrée non vide orpheline dans l’annuaire.')
            _insist(not ole.parsing_issues, 'anomalie détectée pendant la lecture des flux.')
            records.sort(key=lambda record: tuple(record['path']))
            return {'schema': SCHEMA, 'entries': records}
    except (OSError, IOError, IndexError, KeyError, UnicodeError, RecursionError) as exc:
        raise ValueError('Projet VBA : conteneur mal formé ou non pris en charge.') from exc


def fingerprint(data: bytes) -> str:
    """SHA256 of the versioned canonical inventory; no fake-data fallback."""
    value = inventory(data)
    packed = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return _sha(packed)


def normalise_project_metadata(data: bytes) -> bytes:
    """Canonicalize four non-code PROJECT fields for comparison only.

    MS-OVBA 2.3.1.2/.15/.16/.17 define ID, CMG, DPB and GC. Excel rewrites
    these values during ordinary saves. Keep keys, order, line endings and
    every other byte exact. This does not alter a workbook or its VBA data.
    """
    _insist(isinstance(data, bytes) and 0 < len(data) <= 65536, 'flux PROJECT hors bornes.')
    _insist(b'\x00' not in data, 'octet nul dans PROJECT.')
    formats = {
        b'ID': rb'\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}',
        b'CMG': rb'[0-9A-Fa-f]{22,28}',
        b'DPB': rb'[0-9A-Fa-f]{16,4096}',
        b'GC': rb'[0-9A-Fa-f]{16,22}',
    }
    seen = set(); result = []; in_root = True
    for line in data.splitlines(keepends=True):
        if line.startswith(b'['): in_root = False
        key = line.split(b'=', 1)[0].strip().upper()
        if key not in formats:
            result.append(line); continue
        _insist(in_root and key not in seen, 'champ PROJECT volatil dupliqué ou hors section racine.')
        match = re.fullmatch(key + rb'="(' + formats[key] + rb')"(\r\n|\n)', line)
        _insist(match is not None, 'format de champ PROJECT volatil invalide.')
        _insist(key == b'ID' or len(match[1]) % 2 == 0, 'nombre impair de chiffres hexadécimaux PROJECT.')
        seen.add(key)
        result.append(key + b'="<ISP_VOLATILE_' + key + b'>"' + match[2])
    _insist(seen == set(formats), 'les quatre champs PROJECT volatils sont requis.')
    return b''.join(result)


def compatibility_fingerprint(data: bytes) -> str:
    """Keep all logical streams exact except the four validated PROJECT values.

    Module source, compiled code, SRP, DIR, names, hierarchy and every other
    PROJECT line remain in the hash. Unknown compilations require a sealed
    explicit variant; source equivalence alone never authorizes one.
    """
    value = inventory(data)
    with _vendor().OleFileIO(io.BytesIO(data), raise_defects=_vendor().DEFECT_UNSURE) as ole:
        project = normalise_project_metadata(ole.openstream('PROJECT').read())
    matches = [entry for entry in value['entries'] if entry['path'] == ['PROJECT'] and entry['entry_type'] == 2]
    _insist(len(matches) == 1, 'un flux PROJECT racine exact est requis.')
    matches[0].update(size=len(project), sha256=_sha(project))
    value['schema'] = COMPATIBILITY_SCHEMA
    return _sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))
