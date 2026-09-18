"""Select the packaged initial model; existing dossiers keep their own pins."""
from __future__ import annotations

import json
from pathlib import Path

from .model_registry import ModelRegistry, PIN_KEYS, model_pin

CONFIG = 'models/initial-web.json'
ARCHIVES = 'models/web-initial'
SCHEMA = 'tca-bp-initial-model/1'


def configured_pin(project_root):
    root = Path(project_root).resolve()
    path = root / CONFIG
    for part in (path, path.parent):
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('Le modèle initial ne peut être sélectionné par un lien.')
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        if set(value) != {'schema', *PIN_KEYS} or value.get('schema') != SCHEMA:
            raise ValueError('Sélection du modèle initial incompatible.')
        pin = model_pin(value)
        if not all(isinstance(v, str) and v for v in pin.values()):
            raise ValueError('Identité du modèle initial incomplète.')
        return pin
    except (OSError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('Sélection du modèle initial absente ou illisible.') from exc


def initial_engine(project_root):
    root = Path(project_root).resolve()
    pin = configured_pin(root)
    if pin is None:
        from .model_engine import ModelEngine
        return ModelEngine(root)
    directory = root / ARCHIVES
    for part in (directory, directory.parent):
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('L’archive du modèle initial ne peut être un lien.')
    if not directory.resolve().is_relative_to(root):
        raise ValueError('L’archive du modèle initial sort du projet.')
    # The registry checks every physical component, the seal, profile and schema.
    # A configured but damaged model must never silently fall back to another one.
    registry = ModelRegistry(directory, root)
    return registry.resolve(pin)
