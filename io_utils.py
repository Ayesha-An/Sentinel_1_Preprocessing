"""
Input/Output utilities for Sentinel-1 preprocessing
"""
import json
import zipfile
from pathlib import Path
from esa_snappy import ProductIO
from shapely.geometry import shape


def load_aoi(aoi_file):
    """
    Load Area of Interest from GeoJSON file.

    Args:
        aoi_file (Path): Path to GeoJSON file

    Returns:
        str: WKT geometry string

    Raises:
        FileNotFoundError: If GeoJSON file doesn't exist
        ValueError: If GeoJSON structure is invalid
    """
    if not aoi_file.exists():
        raise FileNotFoundError(f"AOI file not found: {aoi_file}")

    print("Loading AOI...")

    with open(aoi_file) as f:
        aoi_data = json.load(f)

    if 'features' not in aoi_data or len(aoi_data['features']) == 0:
        raise ValueError("Invalid GeoJSON: no features found")

    geom = shape(aoi_data['features'][0]['geometry'])
    aoi_wkt = geom.wkt

    print(f"  WKT: {aoi_wkt[:60]}...\n")
    return aoi_wkt


def unzip_product(zip_path):
    """
    Extract Sentinel-1 ZIP file if not already extracted.

    Args:
        zip_path (Path): Path to ZIP file

    Returns:
        Path: Path to .SAFE folder

    Raises:
        FileNotFoundError: If ZIP file doesn't exist
    """
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    safe_path = zip_path.parent / zip_path.stem

    if not safe_path.exists():
        print("  Extracting...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(zip_path.parent)

    return safe_path


def read_product(safe_path):
    """
    Read Sentinel-1 product from .SAFE folder.

    Args:
        safe_path (Path): Path to .SAFE folder

    Returns:
        tuple: (product, product_type)

    Raises:
        FileNotFoundError: If manifest.safe not found
    """
    manifest = safe_path / "manifest.safe"

    if not manifest.exists():
        raise FileNotFoundError(f"manifest.safe not found in {safe_path}")

    product = ProductIO.readProduct(str(manifest))
    product_type = product.getProductType()

    return product, product_type


def save_geotiff(product, output_path, format_name="GeoTIFF-BigTIFF"):
    """
    Save product as GeoTIFF with VV and VH band descriptions.

    Ensures band metadata is properly stored in the GeoTIFF:
    - Band names (e.g., "Sigma0_VV", "Sigma0_VH")
    - Band descriptions

    Args:
        product: SNAP Product object
        output_path (str): Output file path (without extension)
        format_name (str): Output format name

    Raises:
        RuntimeError: If product has no bands
    """
    num_bands = product.getNumBands()

    if num_bands == 0:
        raise RuntimeError("Cannot save product with no bands")

    # Get bands and set descriptions for VV and VH
    print(f"    - Setting band metadata...")
    band_info = []

    for i, band in enumerate(product.getBands(), 1):
        band_name = band.getName()

        # Set description based on polarization
        if 'VV' in band_name.upper():
            description = f"VV polarization (Vertical transmit, Vertical receive)"
            band.setDescription(description)
            polarization = "VV"
        elif 'VH' in band_name.upper():
            description = f"VH polarization (Vertical transmit, Horizontal receive)"
            band.setDescription(description)
            polarization = "VH"
        else:
            description = band_name
            polarization = "Unknown"

        band_info.append(f"Band {i}: {band_name} ({polarization})")

    # Print band information
    print(f"    - Total bands: {num_bands}")
    for info in band_info:
        print(f"      {info}")

    print(f"    - Saving {format_name}...")
    ProductIO.writeProduct(product, output_path, format_name)

    print(f"  ✓ Saved: {Path(output_path).name}.tif")
    print(f"    Band metadata stored in GeoTIFF")


def find_sentinel1_files(input_dir):
    """
    Find all Sentinel-1 ZIP files in input directory.

    Args:
        input_dir (Path): Input directory

    Returns:
        list: List of Path objects to ZIP files
    """
    return sorted(input_dir.rglob("*.zip"))
