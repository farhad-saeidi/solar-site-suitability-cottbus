import io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import geopandas as gpd
from owslib.wms import WebMapService
from config import BBOX, PROCESSED, MAPS

# --- 1. Connect to the Solaratlas WMS (can be slow, so wait up to 120 s) ---
url = "https://energieportal-brandenburg.de/geoserver/solaratlas/ows"
wms = WebMapService(url, version="1.1.1", timeout=120)

# --- 2. Download the map image for our study area ---
layer = "solaratlas_potenzial_photovoltaik_freiflaechen"  # EEG 2023 areas
response = wms.getmap(
    layers=[layer],
    srs="EPSG:25833",
    bbox=BBOX,
    size=(1225, 950),  # 20 m per pixel
    format="image/png",
    transparent=True,
)
solaratlas = mpimg.imread(io.BytesIO(response.read()), format="png")

# --- 3. Read our suitable parcels ---
parcels = gpd.read_file(PROCESSED / "parcels_final.gpkg")

# --- 4.Plot: Solaratlas image + our parcel borders on top ---
xmin, ymin, xmax, ymax = BBOX
fig, ax = plt.subplots(figsize=(10, 8))
ax.imshow(solaratlas, extent=[xmin, xmax, ymin, ymax])
parcels.boundary.plot(ax=ax, color="black", linewidth=0.4)

ax.set_title("Our suitable parcels (black outline) vs. Solaratlas EEG areas (filled)")
ax.text(xmin, ymin - 1500,
        "Solaratlas: © Wirtschaftsförderung Land Brandenburg GmbH (WFBB), dl-de/by-2-0",
        fontsize=7)

plt.savefig(MAPS / "solaratlas_comparison.png", dpi=200, bbox_inches="tight")
plt.show()
print("Saved!")