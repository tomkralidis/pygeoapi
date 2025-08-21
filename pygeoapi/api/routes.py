# =================================================================

# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2025 Tom Kralidis
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


from http import HTTPStatus
import json
import logging
from typing import Tuple

from pygeoapi.plugin import load_plugin
from pygeoapi.util import to_json, filter_dict_by_key_value

from . import APIRequest, API, F_HTML
from pygeoapi.util import render_j2_template

LOGGER = logging.getLogger(__name__)

CONFORMANCE_CLASSES = [
    'http://www.opengis.net/spec/ogcapi-routes-1/1.0.0-draft.1/conf/core'
]


def get_routes(api: API, request: APIRequest) -> Tuple[dict, int, str]:
    """
    Returns available routes

    :param api: An API object
    :param request: A request object

    :returns: tuple of headers, status code, content
    """

    headers = request.get_response_headers(**api.api_headers)

    response = {
        'links': []
    }

    if request.format == F_HTML:  # render
        response = render_j2_template(
            api.tpl_config, api.config['server']['templates'],
            'routes/index.html', response, request.locale)

        return headers, HTTPStatus.OK, response

    return headers, HTTPStatus.OK, to_json(response, api.pretty_print)


def calculate_route(api: API, request: APIRequest) -> Tuple[dict, int, str]:
    """
    Calculates a route

    :param api: An API object
    :param request: A request object

    :returns: tuple of headers, status code, content
    """

    headers = request.get_response_headers(**api.api_headers)

    data = request.data
    if not data:
        msg = 'missing request data'
        return api.get_exception(
            HTTPStatus.BAD_REQUEST, headers, request.format,
            'MissingParameterValue', msg)

    try:
        # Parse bytes data, if applicable
        data = data.decode()
        LOGGER.debug(data)
    except (UnicodeDecodeError, AttributeError):
        pass

    try:
        data = json.loads(data)
    except (json.decoder.JSONDecodeError, TypeError):
        # Input does not appear to be valid JSON
        msg = 'invalid request data'
        return api.get_exception(
            HTTPStatus.BAD_REQUEST, headers, request.format,
            'InvalidParameterValue', msg)

    LOGGER.debug(data)

    routes = filter_dict_by_key_value(api.config['resources'],
                                      'type', 'route')

    # NOTE: OGC API - Routes do not have more than one
    # routing executor.  Take the first one from config
    route_to_load = next(iter(routes.items()))[1]

    router = load_plugin('route', route_to_load['router'])

    mimetype, response = router.calculate_route(data)

    headers['Content-Type'] = mimetype

    return headers, HTTPStatus.OK, to_json(response, api.pretty_print)


def get_oas_30(cfg: dict, locale: str) -> tuple[list[dict[str, str]], dict[str, dict]]:  # noqa
    """
    Get OpenAPI fragments

    :param cfg: `dict` of configuration
    :param locale: `str` of locale

    :returns: `tuple` of `list` of tag objects, and `dict` of path objects
    """

    from pygeoapi.openapi import OPENAPI_YAML

    LOGGER.debug('setting up routes endpoints')

    paths = {}

    paths['/routes'] = {
        'get': {
            'summary': 'Retrieve routes list',
            'description': 'Retrieve a list of routes',
            'tags': ['routes'],
            'operationId': 'getRoutes',
            'responses': {
                '200': {'$ref': '#/components/responses/200'},
                '404': {'$ref': f"{OPENAPI_YAML['oapif-1']}/responses/NotFound.yaml"},  # noqa
                'default': {'$ref': '#/components/responses/default'}
            }
        },
        'post': {
            'summary': 'Route calculation',
            'description': 'Route calculation',
            'tags': ['routes'],
            'operationId': 'executeRoute',
            'responses': {
                '200': {'$ref': '#/components/responses/200'},
                '500': {'$ref': f"{OPENAPI_YAML['oapif-1']}/responses/ServerError.yaml"},  # noqa
                'default': {'$ref': '#/components/responses/default'}
            },
            'requestBody': {
                'description': 'Mandatory calculate request JSON',
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'properties': {
                                'inputs': {
                                    'type': 'object',
                                    'description': 'Routing inputs',
                                    'properties': {
                                        'name': {
                                            'type': 'string',
                                            'description': 'route description',
                                        },
                                        'waypoints': {
                                            'type': 'object',
                                            'description': 'waypoints',
                                            'properties': {
                                                'value': {
                                                    '$ref': 'https://geojson.org/schema/MultiPoint.json'  # noqa
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return [{'name': 'routes'}], {'paths': paths}
