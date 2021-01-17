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

import click
import logging

from pygeoapi.plugin import load_plugin
from pygeoapi.provider.base import ProviderConnectionError
from pygeoapi.util import (yaml_load, filter_dict_by_key_value, 
                           get_provider_by_type, get_provider_default)

LOGGER = logging.getLogger(__name__)

cli = click.Group()


def catalogue_to_record(config):
    """
    Create an OGC API - Records record from service configuration

    :param config: `dict` of configuration

    :returns: `dict` of service as a record
    """

    record = {
        'id': '-',
        'type': 'collection',
        'title': config['metadata']['identification']['title'],
        'description': config['metadata']['identification']['description'],
        'keywords': config['metadata']['identification']['keywords'],
        'extents': {
            'spatial': {
                'bbox': [-180, -90, 180, 90],
                'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
            }
        },
        'links': [],
        'providers': config['metadata']['catalogue']['providers']
    }

    return record


def resource_to_record(identifier, resource):
    """
    Create an OGC API - Records record from pygeoapi resource configuration

    :param resource: `dict` of resource definition

    :returns: `dict` of resource as a record
    """

    temporal = {}
    bbox_crs = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'

    title = resource['title']
    description = resource['description']
    keywords = resource['keywords']
    minx, miny, maxx, maxy = resource['extents']['spatial']['bbox']

    if 'temporal' in resource['extents']:
        temporal = {
            'interval': [],
            'trs': 'http://www.opengis.net/def/uom/ISO-8601/0/Gregorian'
        }

        if 'begin' in resource['extents']['temporal']:
            te_begin = resource['extents']['temporal']['begin'].isoformat()
        else:
            te_begin = None

        if 'end' in resource['extents']['temporal']:
            te_end = resource['extents']['temporal']['begin'].isoformat()
        else:
            te_end = None

        temporal['interval'] = [te_begin, te_end]

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
                'bbox': [[minx, miny, maxx, maxy]],
                'crs': bbox_crs
            }
        },
        'properties': {
            'identifier': identifier,
            '@type': 'dataset',
            'title': title,
            'description': description,
            'keywords': keywords,
#            '_raw_metadata': to_json(resource),#json.dumps(resource, indent=4, default=json_serial, ensure_ascii=False),  # noqa
            '_anytext': ' '.join([title, description, *keywords])
        }
    }

    if temporal:
        json_record['extents']['temporal'] = temporal

    return json_record


@click.command()
@click.pass_context
@click.option('--config', '-c', 'config_file', help='configuration file')
def generate_catalogue(ctx, config_file):
    """Generate records catalogue from configuration"""

    c = None

    if config_file is None:
        raise click.ClickException('--config/-c required')
    with open(config_file) as ff:
        c = yaml_load(ff)

    # load catalogue provider
    # read records from config

    LOGGER.debug('Loading provider')
    try:
        p = load_plugin('provider', get_provider_by_type(
                            c['metadata']['catalogue']['providers'],
                            'records'))
    except ProviderConnectionError as err:
        raise click.ClickException(err)

    for k, v in c['resources'].items():
        if v['type'] == 'collection':
            rr = resource_to_record(k, v)
        print(rr)
        p.insert(rr)


cli.add_command(generate_catalogue)
