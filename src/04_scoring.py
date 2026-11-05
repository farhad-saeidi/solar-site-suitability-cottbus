import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from config import RAW, PROCESSED

# --- Read data ---
candidates = gpd.read_file(PROCESSED / "candidates.gpkg")
roads = gpd.read_file(RAW / "osm_roads.gpkg")

# --- 0. Roads that construction trucks can use (no paths, tracks, footways) ---
truck_roads = ["motorway", "trunk", "primary", "secondary", "tertiary",
               "unclassified", "residential",
               "motorway_link", "trunk_link", "primary_link",
               "secondary_link", "tertiary_link"]
roads = roads[roads["fclass"].isin(truck_roads)]
roads_union = roads.union_all()

# --- 1. Merge touching candidates into parcels, split them at roads ---
merged = candidates.union_all()
merged = merged.difference(roads_union.buffer(5))  # cut a 10 m wide road strip
parcels = gpd.GeoDataFrame(geometry=[merged], crs=candidates.crs)
parcels = parcels.explode(index_parts=False).reset_index(drop=True)
print("Number of parcels:", len(parcels))

# --- 2. Mean slope and share of steep pixels of each parcel ---
slopes = []
steep_shares = []
with rasterio.open(PROCESSED / "slope.tif") as src:
    for geom in parcels.geometry:
        data, _ = mask(src, [geom], crop=True, all_touched=True, nodata=np.nan)
        values = data[~np.isnan(data)]
        slopes.append(values.mean())
        steep_shares.append((values > 10).mean())
parcels["slope_mean"] = slopes
parcels["steep_share"] = steep_shares

# --- 3. Hard exclusion: mean slope above 10 deg OR more than 25% steep pixels ---
too_steep = (parcels["slope_mean"] > 10) | (parcels["steep_share"] > 0.25)
print("Parcels excluded because of slope:", too_steep.sum())
parcels = parcels[~too_steep].copy()

# --- 4. Distance to the nearest road ---
parcels["road_dist"] = parcels.distance(roads_union)

# --- 5. Soft protection: LSG and BR (lower score, not excluded) ---
protected = gpd.read_file(RAW / "protected_areas.gpkg")
protected["type"] = protected["gml_id"].str.split("_").str[2]
soft = protected[protected["type"].isin(["LSG", "BR"])]
soft_union = soft.union_all()
parcels["lsg_share"] = parcels.intersection(soft_union).area / parcels.area
parcels["in_lsg_br"] = parcels["lsg_share"] > 0.5

# --- 6. Scores (0 to 3 points) ---
parcels["slope_score"] = pd.cut(parcels["slope_mean"],
                                bins=[-1, 3, 6, 10],
                                labels=[3, 2, 1]).astype(int)
parcels["road_score"] = pd.cut(parcels["road_dist"],
                               bins=[-1, 500, 1000, 2000, np.inf],
                               labels=[3, 2, 1, 0]).astype(int)
penalty = parcels["in_lsg_br"].astype(int)

# Two weighting scenarios
parcels["score_equal"] = 0.5 * parcels["slope_score"] + 0.5 * parcels["road_score"] - penalty
parcels["score_slope"] = 0.7 * parcels["slope_score"] + 0.3 * parcels["road_score"] - penalty

# --- Save and print a summary ---
parcels.to_file(PROCESSED / "parcels_scored.gpkg")
print("Parcels left:", len(parcels))
print("Parcels in LSG/BR:", parcels["in_lsg_br"].sum())
print("Median road distance:", round(parcels["road_dist"].median()), "m")
print("Saved!")