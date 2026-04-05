"""
SNAP processing operators for Sentinel-1 GRD preprocessing
"""
from esa_snappy import GPF, HashMap
import config


def apply_orbit_file(product):
    """
    Apply precise orbit file.

    Args:
        product: SNAP Product object

    Returns:
        SNAP Product with orbit correction applied
    """
    print("    - Orbit correction")

    params = HashMap()
    params.put("orbitType", "Sentinel Precise (Auto Download)")
    params.put("continueOnFail", False)

    return GPF.createProduct("Apply-Orbit-File", params, product)


def thermal_noise_removal(product):
    """
    Remove thermal noise (GRD only).

    Args:
        product: SNAP Product object

    Returns:
        SNAP Product with thermal noise removed
    """
    print("    - Thermal noise removal")

    params = HashMap()
    params.put("removeThermalNoise", True)

    return GPF.createProduct("ThermalNoiseRemoval", params, product)


def calibration(product):
    """
    Radiometric calibration to Sigma0.

    Args:
        product: SNAP Product object

    Returns:
        SNAP Product with Sigma0 bands (VV and VH)
    """
    print("    - Calibration (Sigma0)")

    params = HashMap()
    params.put("outputSigmaBand", True)
    params.put("outputImageScaleInDb", False)

    return GPF.createProduct("Calibration", params, product)


def speckle_filter(product, filter_type="Lee Sigma"):
    """
    Apply speckle filtering to reduce noise while preserving edges.

    Args:
        product: SNAP Product object
        filter_type (str): Filter type - "Lee Sigma", "Refined Lee", or "Gamma Map"

    Returns:
        SNAP Product with speckle filtering applied
    """
    print(f"    - Speckle filtering ({filter_type})")

    params = HashMap()
    params.put("filter", filter_type)
    params.put("filterSizeX", 5)
    params.put("filterSizeY", 5)
    params.put("dampingFactor", 2)
    params.put("estimateENL", True)
    params.put("enl", 1.0)
    params.put("numLooksStr", "1")
    params.put("windowSize", "7x7")
    params.put("targetWindowSizeStr", "3x3")
    params.put("sigmaStr", "0.9")
    params.put("anSize", "50")

    return GPF.createProduct("Speckle-Filter", params, product)


def terrain_correction(product, target_crs=None):
    """
    Terrain correction with map projection to UTM 33N.

    Args:
        product: SNAP Product object
        target_crs (str): Target CRS (default from config)

    Returns:
        SNAP Product terrain corrected
    """
    print("    - Terrain correction")

    if target_crs is None:
        target_crs = config.TARGET_CRS

    params = HashMap()
    params.put("demName", config.DEM_NAME)
    params.put("imgResamplingMethod", "BILINEAR_INTERPOLATION")
    params.put("mapProjection", target_crs)
    params.put("pixelSpacingInMeter", config.PIXEL_SPACING)
    params.put("saveSelectedSourceBand", True)

    return GPF.createProduct("Terrain-Correction", params, product)


def subset_to_aoi(product, wkt):
    """
    Subset product to Area of Interest.

    Args:
        product: SNAP Product object
        wkt (str): WKT geometry string

    Returns:
        SNAP Product subset to AOI
    """
    print("    - Subset to AOI")

    params = HashMap()
    params.put("geoRegion", wkt)
    params.put("copyMetadata", True)

    return GPF.createProduct("Subset", params, product)


def process_grd(product, aoi_wkt):
    """
    Complete Sentinel-1 GRD processing pipeline.

    Pipeline:
    1. Orbit correction
    2. Thermal noise removal
    3. Calibration to Sigma0
    4. Speckle filtering (Lee Sigma)
    5. Terrain correction to UTM 33N
    6. Subset to AOI

    Args:
        product: SNAP Product object
        aoi_wkt (str): AOI in WKT format

    Returns:
        SNAP Product: Fully processed GRD product with VV and VH bands
    """
    print("  Processing GRD...")

    product = apply_orbit_file(product)
    product = thermal_noise_removal(product)
    product = calibration(product)
    product = speckle_filter(product)
    product = terrain_correction(product)
    product = subset_to_aoi(product, aoi_wkt)

    return product
