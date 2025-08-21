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

import sys

import osmnx as ox
from osmnx import convert, projection
from wayfarer import loader


def download_osm(lat, long, distance_in_metres, name):
    """
    Download roads from OSM centered around Riga, Latvia
    This only needs to be run once.
    """

    location_point = (lat, long)
    # get roads within a distance of distance_in_metres m from this point
    bbox = ox.utils_geo.bbox_from_point(
        location_point, dist=distance_in_metres)

    G = ox.graph_from_bbox(bbox=bbox)

    # save as a graph
    ox.save_graphml(G, filepath=f'{name}/network.graphml')

    # also save the data as a GeoPackage for review (not required for routing)
    ox.save_graph_geopackage(G, filepath=f'{name}/network.gpkg')


def create_wayfarer_graph():

    # load the OSMnx graph from the previously saved file
    G = ox.load_graphml(f'{name}/network.graphml')

    # get data frames from the graph
    _, gdf_edges = convert.graph_to_gdfs(convert.to_undirected(G))

    # project to Web Mercator from EPSG:4326 so we can work with
    # planar distance calculations
    gdf_edges = projection.project_gdf(gdf_edges, to_crs="EPSG:3857")

    # get a dictionary of all edges in the network
    d = gdf_edges.to_dict("records")

    # loop through the edges and add a unique key
    recs = []

    for fid, props in enumerate(d):
        # we can't use osmid as the key as sometimes it is not always unique
        # and sometimes a list
        # instead use the enumerator which will match the FID in the GeoPackage
        props.update({"key": fid})
        # we reprojected the geometry to Web Mercator, so we also need to
        # update the length field
        props["length"] = props["geometry"].length
        recs.append(props)

    # create the wayfarer network
    net = loader.load_network_from_records(
        recs,
        key_field="key",
        length_field="length",
        from_field="from",
        to_field="to",
    )

    # save the network
    loader.save_network_to_file(net, f'{name}/network.pickle')


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(f'Usage: {sys.argv[0]} <lat> <long> <distance_in_metres> <name>')
        sys.exit(1)

    lat, long, distance_in_metres, name = sys.argv[1:]
    print('Downloading from OSM')
    download_osm(float(lat), float(long), int(distance_in_metres), name)
    print('Creating network graph')
    create_wayfarer_graph()
    print("Done!")
