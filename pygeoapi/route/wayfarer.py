# =================================================================
#
# Authors: Seth Girvin <sethg@geographika.co.uk>
#          Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2025 Seth Girvin
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

import json
import logging
import sys
from typing import Any

import networkx
import pyproj
import shapely
from shapely import Geometry
from shapely.geometry import mapping, Point, shape
from shapely.ops import transform
from wayfarer import linearref, loader, routing, splitter, to_edge

from pygeoapi.route.base import BaseRouter

LOGGER = logging.getLogger(__name__)


def get_closest_edge(network: networkx.MultiGraph, point: Geometry) -> tuple:
    """
    Get closest edge of a point

    :param network: Wayfarer Generated Multigraph
    :param point: Shapely `Geometry` (`Point`)

    :returns: `tuple` of node id and distance measure
    """

    closest_line = None
    min_dist = float('inf')

    for edge in network.edges(data=True, keys=True):
        edge = to_edge(edge)
        geom = shape(edge.attributes['geometry'])
        dist = point.distance(geom)
        if dist < min_dist:
            min_dist = dist
            closest_line = geom
            fid = edge.key

    LOGGER.debug('Finding snapped point on the line')
    snap_point, _ = linearref.get_nearest_vertex(point, closest_line)

    LOGGER.debug('Getting the measure along the line')
    distance_along = linearref.get_measure_on_line(closest_line, snap_point)

    return (fid, distance_along)


def transform_point(crs_in: str, crs_out: str, geometry: Geometry) -> Geometry:
    """
    Transform coordinates of a Shapely geometry from one CRS to another

    :param crs_in: `str` of source CRS
    :param crs_out: `str` of destination CRS
    :param geometry: Shapely `Geometry` object

    :returns: Shapely `Geometry` object of transformed geometry
    """

    LOGGER.debug('Transforming Geometry')
    LOGGER.debug(f'Geometry type: {type(geometry)}')

    transformer = pyproj.Transformer.from_crs(
        crs_in, crs_out, always_xy=True).transform

    return transform(transformer, geometry)


def get_node(network: networkx.MultiGraph, edge, start_or_end: str) -> Any:
    """
    Function to calculate a node

    :param network: Wayfarer Generated Multigraph
    :param fid: `int` of node id
    :param measure: `float` of measure

    :returns: node
    """

    if start_or_end == 'start':
        idx = 0
    elif start_or_end == 'end':
        idx = 1

    split_edges = splitter.split_network_edge(network, edge[0], [edge[1]])
    node = split_edges[idx].start_node

    return node


def path2geojson(path) -> dict:
    """
    Function to serialize a GeoJSON FeatureCollection from a path

    :param path: PATH TODO
    :returns: `dict` of resulting path as GeoJSON
    """

    LOGGER.debug('Building GeoJSON')

    geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    for edge in path:
        LOGGER.debug('Transforming edge Geometry')
        geometry = transform_point(
            'EPSG:3857', 'EPSG:4326', edge.attributes['geometry'])

        feature = {
            'type': 'Feature',
            'geometry': mapping(geometry),
            'properties': {
                'id': edge.key
            }
        }
        geojson['features'].append(feature)

    return geojson


def calculate_route(network: networkx.MultiGraph, startx: float, starty: float,
                    endx: float, endy: float) -> dict:
    """
    Function to calculate a route

    :param network: Wayfarer Generated Multigraph
    :param startx: `float` of starting x coordinate
    :param starty: `float` of starting y coordinate
    :param endx: `float` of end x coordinate
    :param endy: `float` of end y coordinate

    :returns: `dict` of GeoJSON response
    """

    LOGGER.debug('Transforming point')
    start_point = transform_point('EPSG:4326', 'EPSG:3857',
                                  Point(startx, starty))
    end_point = transform_point('EPSG:4326', 'EPSG:3857',
                                Point(endx, endy))

    LOGGER.debug('Get start and end edges')
    start_edge = get_closest_edge(network, start_point)
    end_edge = get_closest_edge(network, end_point)

    LOGGER.debug('Get start and end nodes')
    start_node = get_node(network, start_edge, 'start')
    end_node = get_node(network, end_edge, 'end')

    LOGGER.debug('Get path')
    path = routing.solve_shortest_path(network, start_node=start_node,
                                       end_node=end_node)

    LOGGER.debug('Transform to GeoJSON')
    return path2geojson(path)


class WayfarerRouter(BaseRouter):
    def __init__(self, provider_def):
        """
        Initialize object

        :param route_def: route definition

        :returns: pygeoapi.route.wayfarer.WayfarerRouter
        """

        super().__init__(provider_def)

    def calculate_route(self, data):
        coords = shapely.from_geojson(
            json.dumps(data['inputs']['waypoints']['value']))

        network = loader.load_network_from_file(self.data)

        result = calculate_route(network, coords.geoms[0].x, coords.geoms[0].y,
                                 coords.geoms[1].x, coords.geoms[1].y)

        return 'application/geo+json', result


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <startx,starty> <endx,endy>')

    start_point = [float(c) for c in sys.argv[1].split(',')]
    end_point = [float(c) for c in sys.argv[2].split(',')]

    # load the network
    network = loader.load_network_from_file('./data/riga.pickle')

    # calculate the route!
    route_geojson = calculate_route(network, *start_point, *end_point)

    print(json.dumps(route_geojson))
