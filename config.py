"""
Configuration file for Sentinel-1 GRD preprocessing
"""
from pathlib import Path

# Directory paths
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
AOI_FILE = INPUT_DIR / "aoi" / "aoi_geog.geojson"

# GRD Processing parameters
TARGET_CRS = "EPSG:32633" 
DEM_NAME = "SRTM 3Sec"
PIXEL_SPACING = 10.0  

# Output format
OUTPUT_FORMAT = "GeoTIFF-BigTIFF"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)
