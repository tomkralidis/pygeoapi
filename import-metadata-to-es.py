import json
import sys

from owslib.iso import MD_Metadata
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from lxml import etree

es = Elasticsearch()
index_name = 'msc-wis-dcpc'


def get_anytext(bag):
    """
    generate bag of text for free text searches
    accepts list of words, string of XML, or etree.Element
    """

    if isinstance(bag, list):  # list of words
        return ' '.join([_f for _f in bag if _f]).strip()
    else:  # xml
        text_bag = []

        if isinstance(bag, (bytes, str)):
            # serialize to lxml
            bag = etree.fromstring(bag)

        for t in bag.xpath('//gco:CharacterString', namespaces={'gco': 'http://www.isotc211.org/2005/gco'}):
            if t.text is not None:
                text_bag.append(t.text.strip())

    return ' '.join(text_bag)


# index settings
settings = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },
    'mappings': {
        'properties': {
            'geometry': {
                'type': 'geo_shape'
            },
            'properties': {
                'properties': {
                    'modified': {
                        'type':   'date',
                        'format': 'yyyy-MM-dd HH:mm:ss||yyyy||yyyy-MM-dd'
                    },
                    '_raw_metadata': {
                        'type':   'object',
                        'enabled': False
                    }
                }
            }
        }
    }
}

if es.indices.exists(index_name):
    es.indices.delete(index_name)

es.indices.create(index=index_name, body=settings, request_timeout=90)

with open(sys.argv[1]) as fh:
    xml = etree.parse(sys.argv[1])

for record in xml.findall('//{http://www.isotc211.org/2005/gmd}MD_Metadata'):
    m = MD_Metadata(record)

    _raw_metadata = m.xml.decode('utf-8')
    _anytext = get_anytext(_raw_metadata)

    identifier = m.identifier
    type_ = m.hierarchy
    title = m.identification.title
    description = m.identification.abstract
    issued = m.datestamp

    keywords = []
    for keyword_set in m.identification.keywords2:
        for keyword in keyword_set.keywords:
            keywords.append(keyword)

    bbox_crs = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'

    minx = float(m.identification.bbox.minx)
    miny = float(m.identification.bbox.miny)
    maxx = float(m.identification.bbox.maxx)
    maxy = float(m.identification.bbox.maxy)

    bbox = [minx, miny, maxx, maxy]

    te_begin = m.identification.temporalextent_start
    if te_begin == 'missing': te_begin = None
    te_end = m.identification.temporalextent_end

    json_record = {
        'id': identifier,
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [[
                [minx, miny],
                [minx, maxy],
                [maxx, maxy],
                [maxx, miny],
                [minx, miny]
            ]]
        },
        'extents': {
            'spatial': {
                'bbox': [[bbox]],
                'crs': bbox_crs
            },
            'temporal': {
                'interval': [te_begin, te_end],
                'trs': 'http://www.opengis.net/def/uom/ISO-8601/0/Gregorian'
            }
        },
        'properties': {
            'identifier': identifier,
            '@type': type_,
            'title': title,
            'description': description,
            'keywords': keywords,
            'issued': issued,
            '_raw_metadata': _raw_metadata,
            '_anytext': _anytext
        }
    }

#    print(json_record)
#    print(json.dumps(json_record, indent=4, ensure_ascii=False))

    try:
        res = es.index(index=index_name, id=identifier, body=json_record)
    except RequestError as err:
        #print(json.dumps(json_record, indent=4, ensure_ascii=False))
        print(bbox)
        print(err)

