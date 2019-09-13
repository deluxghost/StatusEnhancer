import json
import os

FILE = 'statusenhancer.json'
DEFAULT_COLUMNS = {
    'steam64': True,
    'steam2': False,
    'steam3': False,
    'connected': False,
    'profile': True,
    'custom': list()
}


def load_options():
    default = {
        'columns': DEFAULT_COLUMNS
    }
    if os.path.isfile(FILE):
        with open(FILE, encoding='utf-8') as f:
            try:
                d = json.load(f)
            except Exception:
                return default
            if 'columns' not in d:
                return default
            return {
                'columns': {
                    'steam64': d['columns'].get('steam64', False),
                    'steam2': d['columns'].get('steam2', False),
                    'steam3': d['columns'].get('steam3', False),
                    'connected': d['columns'].get('connected', False),
                    'profile': d['columns'].get('profile', False),
                    'custom': clean_custom(d['columns'].get('custom', list()))
                }
            }
    return default


def save_options(opt):
    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(opt, f, indent=2)


def clean_custom(customs):
    out = list()
    for c in customs:
        if not isinstance(c, dict):
            continue
        if 'name' not in c or 'format' not in c:
            continue
        if not c['name']:
            continue
        custom = {
            'name': c['name'],
            'format': c['format']
        }
        out.append(custom)
    return out
