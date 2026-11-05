import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from config import BBOX, CRS, RAW, PROCESSED

# Input and output files
src_file = RAW / "Copernicus_DSM_COG_10_N51_00_E014_00_DEM.tif"
out_file = PROCESSED / "dem_cottbus.tif"

# Target grid: our bbox with 30 m pixels
res = 30
xmin, ymin, xmax, ymax = BBOX
width = int((xmax - xmin) / res)
height = int((ymax - ymin) / res)
transform = from_origin(xmin, ymax, res, res)

# Empty array for the new DEM
dem = np.zeros((height, width), dtype="float32")

# Reproject from EPSG:4326 to EPSG:25833 and cut to bbox
with rasterio.open(src_file) as src:
    reproject(
        source=rasterio.band(src, 1),
        destination=dem,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=CRS,
        resampling=Resampling.bilinear,
    )

# Short check
print("Size:", dem.shape)
print("Min height:", dem.min(), "m")
print("Max height:", dem.max(), "m")

# Save as GeoTIFF
with rasterio.open(
    out_file, "w", driver="GTiff",
    height=height, width=width, count=1,
    dtype="float32", crs=CRS, transform=transform,
) as dst:
    dst.write(dem, 1)

print("Saved!")