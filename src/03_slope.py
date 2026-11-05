import numpy as np
import rasterio
from config import PROCESSED

# Read the DEM
with rasterio.open(PROCESSED / "dem_cottbus.tif") as src:
    dem = src.read(1)
    profile = src.profile
    pixel_size = src.res[0]  # 30 m

# Height change per metre in y and x direction
dy, dx = np.gradient(dem, pixel_size)

# Slope in degrees
slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))

# Short summary
print("Min slope:", round(slope.min(), 1), "deg")
print("Max slope:", round(slope.max(), 1), "deg")
print("Mean slope:", round(slope.mean(), 1), "deg")

# Save as GeoTIFF (same grid as the DEM)
with rasterio.open(PROCESSED / "slope.tif", "w", **profile) as dst:
    dst.write(slope.astype("float32"), 1)

print("Saved!")