import io
import geopandas as gpd
from owslib.wfs import WebFeatureService
from config import BBOX, CRS, RAW

# Connect to the WFS of LfU Brandenburg
url = "https://inspire.brandenburg.de/services/ps_schutzg_wfs"
wfs = WebFeatureService(url, version="2.0.0")

# Download protected sites inside our study area
response = wfs.getfeature(
    typename="ps:ProtectedSite",
    bbox=BBOX,
    srsname="urn:ogc:def:crs:EPSG::25833",
)

# Read the data into a GeoDataFrame
gdf = gpd.read_file(io.BytesIO(response.read()))
if gdf.crs is None:
    gdf = gdf.set_crs(CRS)

# Show a short summary
print("Number of areas:", len(gdf))
print(gdf["gml_id"].head(10))

# Save the result
gdf.to_file(RAW / "protected_areas.gpkg")
print("Saved!")