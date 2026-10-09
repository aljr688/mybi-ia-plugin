"""Load local JSON references, including readable distribution shards."""
import json
from pathlib import Path


def load_reference(path):
    path = Path(path)
    value = json.loads(path.read_text(encoding='utf-8'))
    if value.get('format') != 'mybi-reference-parts-v1':
        return value
    entries = {}
    for relative in value['parts']:
        target = (path.parent / relative).resolve()
        if not target.is_relative_to(path.parent.resolve()):
            raise ValueError('Reference outside local directory')
        part = json.loads(target.read_text(encoding='utf-8'))
        if entries.keys() & part.keys():
            raise ValueError('Duplicate reference entries')
        entries.update(part)
    if len(entries) != value['entryCount']:
        raise ValueError('Incomplete reference')
    if value['collection']:
        return {**value['metadata'], value['collection']: entries}
    return entries
