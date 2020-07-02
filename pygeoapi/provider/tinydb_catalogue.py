# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2020 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import json
import logging
import os

from tinydb import TinyDB, Query

from pygeoapi.provider.base import (BaseProvider, ProviderConnectionError,
                                    ProviderQueryError,
                                    ProviderItemNotFoundError)

LOGGER = logging.getLogger(__name__)


class TinyDBCatalogueProvider(BaseProvider):
    """TinyDB Catalogue Provider"""

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition

        :returns: pygeoapi.providers.tinydb_catalogue.TinyDBCatalogueProvider
        """

        BaseProvider.__init__(self, provider_def)

        LOGGER.debug('Connecting to TinyDB db at {}'.format(self.data))

        if not os.path.exists(self.data):
            LOGGER.warning('TinyDB does not exist; creating')

        self.db = TinyDB(self.data)

        self.fields = self.get_fields()

    def get_fields(self):
        """
         Get provider field information (names, types)

        :returns: dict of fields
        """

        fields = {}

        try:
            r = self.db.all()[0]
        except IndexError as err:
            LOGGER.debug(err)
            return fields

        for p in r['properties'].keys():
            if p in ['_anytext', '_raw_metadata']:
                continue
            fields[p] = 'string'

        return fields

    def query(self, startindex=0, limit=10, resulttype='results',
              bbox=[], datetime=None, properties=[], sortby=[], q=None):
        """
        query TinyDB document store

        :param startindex: starting record to return (default 0)
        :param limit: number of records to return (default 10)
        :param resulttype: return results or hit limit (default results)
        :param bbox: bounding box [minx,miny,maxx,maxy]
        :param datetime: temporal (datestamp or extent)
        :param properties: list of tuples (name, value)
        :param sortby: list of dicts (property, order)
        :param q: full-text search term(s)

        :returns: dict of 0..n records
        """

        return self.db.all()
        query = {'track_total_hits': True, 'query': {'bool': {'filter': []}}}
        filter_ = []

        feature_collection = {
            'type': 'FeatureCollection',
            'features': []
        }

        if resulttype == 'hits':
            LOGGER.debug('hits only specified')
            limit = 0

        if bbox:
            LOGGER.debug('processing bbox parameter')
            minx, miny, maxx, maxy = bbox
            bbox_filter = {
                'geo_shape': {
                    'geometry': {
                        'shape': {
                            'type': 'envelope',
                            'coordinates': [[minx, maxy], [maxx, miny]]
                        },
                        'relation': 'intersects'
                    }
                }
            }

            query['query']['bool']['filter'].append(bbox_filter)

        if datetime is not None:
            LOGGER.debug('processing datetime parameter')
            if self.time_field is None:
                LOGGER.error('time_field not enabled for collection')
                raise ProviderQueryError()

            time_field = self.mask_prop(self.time_field)

            if '/' in datetime:  # envelope
                LOGGER.debug('detected time range')
                time_begin, time_end = datetime.split('/')

                range_ = {
                    'range': {
                        time_field: {
                            'gte': time_begin,
                            'lte': time_end
                        }
                    }
                }
                if time_begin == '..':
                    range_['range'][time_field].pop('gte')
                elif time_end == '..':
                    range_['range'][time_field].pop('lte')

                filter_.append(range_)

            else:  # time instant
                LOGGER.debug('detected time instant')
                filter_.append({'match': {time_field: datetime}})

            LOGGER.debug(filter_)
            query['query']['bool']['filter'].append(filter_)

        if properties:
            LOGGER.debug('processing properties')
            for prop in properties:
                pf = {
                    'match': {
                        self.mask_prop(prop[0]): prop[1]
                    }
                }
                query['query']['bool']['filter'].append(pf)

        if sortby:
            LOGGER.debug('processing sortby')
            query['sort'] = []
            for sort in sortby:
                LOGGER.debug('processing sort object: {}'.format(sort))

                sp = sort['property']

                if self.fields[sp] == 'string':
                    LOGGER.debug('setting ES .raw on property')
                    sort_property = '{}.raw'.format(self.mask_prop(sp))
                else:
                    sort_property = self.mask_prop(sp)

                sort_order = 'asc'
                if sort['order'] == 'D':
                    sort_order = 'desc'

                sort_ = {
                    sort_property: {
                        'order': sort_order
                    }
                }
                query['sort'].append(sort_)

        if q is not None:
            query['query']['bool']['must'] = {'query_string': {'query': q}}

        query['_source'] = {'excludes': [
            'properties._raw_metadata',
            'properties._anytext'
        ]}

        if self.properties:
            LOGGER.debug('including specified fields: {}'.format(
                self.properties))
            query['_source'] = {
                'includes': list(map(self.mask_prop, self.properties))
            }
            query['_source']['includes'].append(self.mask_prop(self.id_field))
            query['_source']['includes'].append('type')
            query['_source']['includes'].append('geometry')
        try:
            LOGGER.debug('querying Elasticsearch')
            print('query: {}'.format(json.dumps(query, indent=4)))
            LOGGER.debug('query: {}'.format(json.dumps(query, indent=4)))

            LOGGER.debug('Setting ES paging zero-based')
            if startindex > 0:
                startindex2 = startindex - 1
            else:
                startindex2 = startindex

            results = self.es.search(index=self.index_name,
                                     from_=startindex2, size=limit,
                                     body=query)
            results['hits']['total'] = results['hits']['total']['value']

        except Exception as err:
            LOGGER.error(err)
            raise ProviderQueryError()

        feature_collection['numberMatched'] = results['hits']['total']

        if resulttype == 'hits':
            return feature_collection

        feature_collection['numberReturned'] = len(results['hits']['hits'])

        LOGGER.debug('serializing features')
        for feature in results['hits']['hits']:
            feature_ = self.esdoc2geojson(feature)
            feature_collection['features'].append(feature_)

        return feature_collection

    def get(self, identifier):
        """
        Get TinyDB document by id

        :param identifier: record id

        :returns: `dict` of single record
        """

        LOGGER.debug('Fetching identifier {}'.format(identifier))

        Record = Query()
        record = self.db.get(Record.identfier == identifier)
        if len(record) < 1:
            raise ProviderItemNotFoundError('record does not exist')

        return record

    def insert(self, record):
        self.db.insert(record)

    def __repr__(self):
        return '<TinyDBCatalogueProvider> {}'.format(self.data)
