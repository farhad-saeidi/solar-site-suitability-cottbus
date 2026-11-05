import geopandas as gpd
from shapely.geometry import box
from config import BBOX, CRS, RAW

# Study area as a polygon
area = gpd.GeoSeries([box(*BBOX)], crs=CRS)

# OSM layers we need
layers = {
    "landuse": "gis_osm_landuse_a_free_1.shp",
    "water": "gis_osm_water_a_free_1.shp",
    "roads": "gis_osm_roads_free_1.shp",
}

for name, filename in layers.items():
    # Read only features inside the study area (faster)
    gdf = gpd.read_file(RAW / "osm" / filename, bbox=area)

    # Change CRS from WGS84 (degrees) to EPSG:25833 (metres)
    gdf = gdf.to_crs(CRS)

    # Cut exactly at the bbox border
    gdf = gpd.clip(gdf, area)

    gdf.to_file(RAW / f"osm_{name}.gpkg")
    print(name, ":", len(gdf), "features saved")