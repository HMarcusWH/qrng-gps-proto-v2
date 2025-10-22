import json
def dump(obj) -> bytes:
    return json.dumps(obj, indent=2, sort_keys=True).encode()
