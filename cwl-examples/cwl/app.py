import os
import click
import pystac
import rasterio
import rasterio.mask
from skimage.filters import threshold_otsu
from pyproj import Transformer
from shapely import box
from loguru import logger
import shutil
import rio_stac
import numpy as np

np.seterr(divide="ignore", invalid="ignore")


def crop(asset: pystac.Asset, bbox, epsg):
    """_summary_

    Args:
        asset (_type_): _description_
        bbox (_type_): _description_
        epsg (_type_): _description_

    Returns:
        _type_: _description_
    """
    with rasterio.open(asset.get_absolute_href()) as src:
        transformer = Transformer.from_crs(epsg, src.crs, always_xy=True)

        minx, miny = transformer.transform(bbox[0], bbox[1])
        maxx, maxy = transformer.transform(bbox[2], bbox[3])

        transformed_bbox = box(minx, miny, maxx, maxy)

        logger.info(f"Crop {asset.get_absolute_href()}")

        out_image, out_transform = rasterio.mask.mask(
            src, [transformed_bbox], crop=True
        )
        out_meta = src.meta.copy()

        out_meta.update(
            {
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
            }
        )

        return out_image.astype(np.float32), out_meta


def threshold(data):
    """Returns the Otsu threshold of a numpy array"""
    return data > threshold_otsu(data[np.isfinite(data)])


def normalized_difference(array1, array2):
    """Returns the normalized difference of two numpy arrays"""
    return (array1 - array2) / (array1 + array2)


def aoi2box(aoi):
    """Converts an area of interest expressed as a bounding box to a list of floats"""
    return [float(c) for c in aoi.split(",")]


def get_asset(item, common_name):
    """Returns the asset of a STAC Item defined with its common band name"""
    for _, asset in item.get_assets().items():
        if "data" not in asset.to_dict()["roles"]:
            continue

        eo_asset = pystac.extensions.eo.AssetEOExtension(asset)
        if not eo_asset.bands:
            continue
        for b in eo_asset.bands:
            if (
                "common_name" in b.properties.keys()
                and b.properties["common_name"] == common_name
            ):
                return asset


@click.command(
    short_help="Water bodies detection",
    help="Detects water bodies using the Normalized Difference Water Index (NDWI) and Otsu thresholding.",
)
@click.option(
    "--input-item",
    "item_url",
    help="STAC Item URL or staged STAC catalog",
    required=True,
)
@click.option(
    "--aoi",
    "aoi",
    help="Area of interest expressed as a bounding box",
    required=True,
)
@click.option(
    "--epsg",
    "epsg",
    help="EPSG code",
    required=True,
)
@click.option(
    "--band",
    "bands",
    help="Common band name",
    required=True,
    multiple=True,
)
def main(item_url, aoi, bands, epsg):
    if os.path.isdir(item_url):
        catalog = pystac.read_file(os.path.join(item_url, "catalog.json"))
        item = next(catalog.get_items())
    else:
        item = pystac.read_file(item_url)

    logger.info(f"Read {item.id} from {item.get_self_href()}")

    cropped_assets = {}

    for band in bands:
        asset = get_asset(item, band)
        logger.info(f"Read asset {band} from {asset.get_absolute_href()}")

        if not asset:
            msg = f"Common band name {band} not found in the assets"
            logger.error(msg)
            raise ValueError(msg)

        bbox = aoi2box(aoi)

        out_image, out_meta = crop(asset, bbox, epsg)

        cropped_assets[band] = out_image[0]

    nd = normalized_difference(cropped_assets[bands[0]], cropped_assets[bands[1]])

    water_bodies = threshold(nd)

    out_meta.update(
        {
            "dtype": "uint8",
            "driver": "COG",
            "tiled": True,
            "compress": "lzw",
            "blockxsize": 256,
            "blockysize": 256,
        }
    )

    water_body = "otsu.tif"

    with rasterio.open(water_body, "w", **out_meta) as dst_dataset:
        logger.info("Write otsu.tif")
        dst_dataset.write(water_bodies, indexes=1)

    logger.info("Creating a STAC Catalog")
    cat = pystac.Catalog(id="catalog", description="water-bodies")

    if os.path.isdir(item_url):
        catalog = pystac.read_file(os.path.join(item_url, "catalog.json"))
        item = next(catalog.get_items())
    else:
        item = pystac.read_file(item_url)

    os.makedirs(item.id, exist_ok=True)
    shutil.copy(water_body, item.id)

    out_item = rio_stac.stac.create_stac_item(
        source=water_body,
        input_datetime=item.datetime,
        id=item.id,
        asset_roles=["data", "visual"],
        asset_href=os.path.basename(water_body),
        asset_name="data",
        with_proj=True,
        with_raster=False,
    )

    cat.add_items([out_item])

    cat.normalize_and_save(
        root_href="./", catalog_type=pystac.CatalogType.SELF_CONTAINED
    )

    logger.info("Done!")


if __name__ == "__main__":
    main()
