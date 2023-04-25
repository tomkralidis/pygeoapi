
from glob import glob
from owslib.ogcapi.features import Features

f = Features('http://localhost:5000')
collection_id = 'canada-surface-weather-obs'

for g in glob('test-data/*.json'):
    print(g)
    # insert metadata

    with open(g) as feature:
        try:
            f.collection_item_create(collection_id, feature.read())
        except:
            print(f"{g} not inserted")
            pass
