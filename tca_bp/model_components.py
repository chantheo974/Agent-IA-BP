"""Read sealed JSON components in legacy plain or bounded gzip storage."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from .storage import canonical

MAX_COMPONENT_BYTES = 1024 * 1024 * 1024


def component_path(path):
    path=Path(path)
    return path if path.exists() else path.with_name(path.name+'.gz')


def component_exists(path):
    return component_path(path).is_file()


def read_component(path):
    path=Path(path)
    physical=component_path(path)
    if physical.is_symlink() or (hasattr(physical,'is_junction') and physical.is_junction()) or physical.resolve().parent!=path.parent.resolve():
        raise ValueError('Un composant de modèle ne peut suivre un lien externe.')
    if physical==path:
        return path.read_bytes()
    seal=json.loads((path.parent/'seal.json').read_text(encoding='utf-8'))
    unsigned={k:v for k,v in seal.items() if k!='model_ref'}
    if seal.get('schema')!='tca-bp-model-archive/2' or hashlib.sha256(canonical(unsigned).encode()).hexdigest()!=seal.get('model_ref'):
        raise ValueError('Sceau de composant compressé invalide.')
    storage=seal.get('storage',{}).get(path.name,{})
    size=storage.get('size')
    if storage.get('codec')!='gzip' or storage.get('path')!=physical.name or type(size) is not int or not 0<=size<=MAX_COMPONENT_BYTES:
        raise ValueError('Définition de composant compressé invalide.')
    with physical.open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=storage.get('stored_sha256'):
            raise ValueError('Le composant compressé a changé.')
    with gzip.open(physical,'rb') as stream:
        raw=stream.read(size+1)
    if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=seal['files'].get(path.name):
        raise ValueError('Décompression du composant non conforme à son empreinte.')
    return raw
