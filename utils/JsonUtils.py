import json

from collections import namedtuple


def _json_object_hook(d):
    return namedtuple('item', d.keys())(*d.values())


def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)


def get_data(filename):
    r = []

    with open(filename, 'r') as f:
        r = json2obj(f.read().replace('\n', ''))

    return r


def isnamedtupleinstance(x):
    _type = type(x)
    bases = _type.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(_type, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    return all(type(i) == str for i in fields)


def unpack(obj):
    '''
    Convert namedtuples recursively unpacking
    '''
    if isinstance(obj, dict):
        return {key: unpack(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [unpack(value) for value in obj]
    elif isnamedtupleinstance(obj):
        return {key: unpack(value) for key, value in obj._asdict().items()}
    elif isinstance(obj, tuple):
        return tuple(unpack(value) for value in obj)
    else:
        return obj


def save_data(filename, dataset):
    with open(filename, 'w') as f:
        json.dump(unpack(dataset), f, indent=4)
