# =================================================================
#
# Authors: Antonio Cerciello <anto.nio.cerciello@gmail.com>
#          Francesco Bartoli <xbartolone@gmail.com>
#          Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2022 Antonio Cerciello
# Copyright (c) 2025 Francesco Bartoli
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

from dataclasses import dataclass
from enum import Enum
from typing import Optional

TILEMATRIXSET_HREF_BASEURL = 'https://raw.githubusercontent.com/opengeospatial/2D-Tile-Matrix-Set/master/registry/json'  # noqa


class TilesMetadataFormat(str, Enum):
    # Tile Set Metadata
    JSON = "JSON"
    JSONLD = "JSONLD"
    # TileJSON 3.0
    TILEJSON = "TILEJSON"
    # HTML (default)
    HTML = "HTML"


@dataclass
class TileMatrixSetType:
    id: str
    crs: str
    uri: str
    href: Optional[str] = None
    path: Optional[str] = None


class DefaultTileMatrixSets(Enum):
    WORLDCRS84QUAD = TileMatrixSetType(
        id='WorldCRS84Quad',
        crs='http://www.opengis.net/def/crs/OGC/1.3/CRS84',
        uri='http://www.opengis.net/def/tilematrixset/OGC/1.0/WorldCRS84Quad',
        href=f'{TILEMATRIXSET_HREF_BASEURL}/WorldCRS84Quad.json'
    )
    WEBMERCATORQUAD = TileMatrixSetType(
        id='WebMercatorQuad',
        crs='http://www.opengis.net/def/crs/EPSG/0/3857',
        uri='http://www.opengis.net/def/tilematrixset/OGC/1.0/WebMercatorQuad',
        href=f'{TILEMATRIXSET_HREF_BASEURL}/WebMercatorQuad.json'
    )
