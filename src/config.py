"""Central settings for the solar site suitability project."""
from pathlib import Path

#  Project paths 
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
MAPS = ROOT / "outputs" / "maps"
TABLES = ROOT / "outputs" / "tables"

#  Coordinate reference system (ETRS89 / UTM zone 33N, metres) 
CRS = "EPSG:25833"

#  Study area: Cottbus & Cottbuser Ostsee (xmin, ymin, xmax, ymax) 
BBOX = (446000, 5725500, 470500, 5744500)