import pandas as pd
import geopandas as gpd
from config import BBOX, CRS, RAW, PROCESSED, ROOT

# --- Read data ---
landuse = gpd.read_file(RAW / "osm_landuse.gpkg")
water = gpd.read_file(RAW / "osm_water.gpkg")
protected = gpd.read_file(RAW / "protected_areas.gpkg")
mining = gpd.read_file(ROOT / "data" / "manual" / "active_mining_ExportFeatures.shp").to_crs(CRS)

# --- 1. Candidate land: only open land types ---
good_types = ["farmland", "meadow", "grass", "scrub", "heath"]
candidates = landuse[landuse["fclass"].isin(good_types)].copy()

# --- 2. Exclusion areas ---
# All other land use types (forest, residential, industrial, ...)
bad_landuse = landuse[~landuse["fclass"].isin(good_types)]

# Protected area type is inside gml_id, e.g. "ProtectedSite_DE4252-301_FFH_225"
protected["type"] = protected["gml_id"].str.split("_").str[2]
print(protected["type"].value_counts())

# Strictly protected areas are fully excluded (LSG/BR only get a lower score later)
strict = protected[protected["type"].isin(["FFH", "NSG", "SPA"])]

# Put all exclusion shapes together and merge them into one shape
exclusion = pd.concat([bad_landuse.geometry, water.geometry,
                       strict.geometry, mining.geometry])
exclusion = exclusion.make_valid().union_all()

# --- 3. Remove exclusion areas from candidates ---
candidates["geometry"] = candidates.difference(exclusion)
candidates = candidates[~candidates.is_empty]

# --- Save and print a summary ---
candidates.to_file(PROCESSED / "candidates.gpkg")

# Cut the exclusion layer to the study area (only for nicer maps)
exclusion_gdf = gpd.GeoDataFrame(geometry=[exclusion], crs=CRS).clip(BBOX)
exclusion_gdf.to_file(PROCESSED / "exclusion.gpkg")

print("Candidate polygons:", len(candidates))
print("Candidate area:", round(candidates.area.sum() / 10000), "ha")