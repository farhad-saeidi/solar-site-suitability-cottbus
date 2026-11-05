import geopandas as gpd
from config import PROCESSED, TABLES

# --- Read suitable parcels (>= 2 ha) ---
parcels = gpd.read_file(PROCESSED / "parcels_suitable.gpkg")

# --- Scenario: 1.0 to 1.5 ha of land per MWp ---
HA_PER_MWP_DENSE = 1.0  # dense layout -> more MWp
HA_PER_MWP_WIDE = 1.5   # wide layout  -> less MWp

parcels["mwp_min"] = parcels["area_ha"] / HA_PER_MWP_WIDE
parcels["mwp_max"] = parcels["area_ha"] / HA_PER_MWP_DENSE

# --- Totals for the whole study area ---
print("Suitable area:", round(parcels["area_ha"].sum()), "ha")
print("Capacity:", round(parcels["mwp_min"].sum()), "-",
      round(parcels["mwp_max"].sum()), "MWp")

# --- Top 10 parcels as a table ---
top10 = parcels.sort_values(["score_equal", "area_ha"], ascending=False).head(10)
columns = ["area_ha", "slope_mean", "road_dist", "in_lsg_br",
           "score_equal", "score_slope", "mwp_min", "mwp_max"]
table = top10[columns].round(1)
table.to_csv(TABLES / "top10_parcels.csv", index_label="parcel_id")
print(table)

# --- Save ---
parcels.to_file(PROCESSED / "parcels_final.gpkg")
print("Saved!")