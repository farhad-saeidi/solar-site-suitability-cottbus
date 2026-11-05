import geopandas as gpd
from config import PROCESSED

# --- Read scored parcels ---
parcels = gpd.read_file(PROCESSED / "parcels_scored.gpkg")
parcels["area_ha"] = parcels.area / 10000  # m2 -> ha

# --- 1. Compare two minimum sizes ---
for limit in [2, 5]:
    big = parcels[parcels["area_ha"] >= limit]
    print("Min", limit, "ha:", len(big), "parcels,", round(big["area_ha"].sum()), "ha")

# --- 2. Keep parcels of at least 2 ha (main scenario) ---
MIN_AREA = 2
suitable = parcels[parcels["area_ha"] >= MIN_AREA].copy()

# --- 3. Sensitivity analysis: top 10 parcels in both weighting scenarios ---
# Sort by score, and by area if two parcels have the same score
top_equal = suitable.sort_values(["score_equal", "area_ha"], ascending=False).head(10)
top_slope = suitable.sort_values(["score_slope", "area_ha"], ascending=False).head(10)
common = set(top_equal.index) & set(top_slope.index)
print("Same parcels in both top 10:", len(common), "of 10")

# --- Save ---
suitable.to_file(PROCESSED / "parcels_suitable.gpkg")
print("Saved!")