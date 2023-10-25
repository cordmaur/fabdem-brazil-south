"""Utils"""
import rasterio as rio
from shapely.geometry import Polygon, mapping, shape
import geopandas as gpd
import shapely
from typing import Optional


def get_bbox_and_footprint(dataset):
    """
    This function gets an Rasterio or RioXarray dataset and extracts the bounding box and corresponding footprint
    The Footprint is a Polygon with the dataset boundaries.
    """
    # create the bounding box it will depend if it comes from rasterio or rioxarray
    bounds = dataset.bounds

    if isinstance(bounds, rio.coords.BoundingBox):  # type: ignore
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
    else:
        bbox = [float(f) for f in bounds()]

    # create the footprint
    footprint = Polygon(
        [[bbox[0], bbox[1]], [bbox[0], bbox[3]], [bbox[2], bbox[3]], [bbox[2], bbox[1]]]
    )

    return bbox, mapping(footprint)


def catalog_to_dataframe(catalog):
    """
    Create a Geopandas Dataframe with the footprints of the items in the catalog
    """
    # first, let's get catalog items
    items = list(catalog.get_all_items())

    # create a GeoDataFrame with the items to perform the intersection
    crs = "epsg:" + str(items[0].assets["DEM"].extra_fields["proj:epsg"])
    gdf = gpd.GeoDataFrame(
        index=[item.id for item in items],
        geometry=[shape(item.geometry) for item in items],
        crs=crs,
    )  # type: ignore

    return gdf


def search_catalog(catalog, geometry: Optional[shapely.Geometry] = None):
    """
    Search the catalog for items intersecting the given geometry. The intersection uses the asset footprint
    that is stored in the `item.geometry`.
    If no geometry is given, all items in the catalog are returned.
    """

    gdf = catalog_to_dataframe(catalog)

    gdf_items = gdf[gdf.intersects(geometry)]

    return [catalog.get_item(idx) for idx in gdf_items.index]  # type: ignore
