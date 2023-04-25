
import json

with open('items') as f:
    d = json.load(f)

    for f in d['features']:
        filename = f"{f['id']}.json"
        with open(filename, 'w') as fh2:
            json.dump(f, fh2)
