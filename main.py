"""
Sentinel-1 SAR Preprocessing Pipeline - Main Script
====================================================
Processes Sentinel-1 GRD and SLC products with automatic type detection.

This script orchestrates the preprocessing workflow by using modular components:
- config.py: Configuration and constants
- io_utils.py: Input/output operations
- processors.py: SNAP processing operators

Author: Ayesha Anwar
"""
from pathlib import Path

# Import custom modules
import config
import io_utils
import processors


def process_sentinel1_file(zip_path, aoi_wkt, output_dir):
    """
    Process a single Sentinel-1 file.

    Args:
        zip_path (Path): Path to Sentinel-1 ZIP file
        aoi_wkt (str): AOI in WKT format
        output_dir (Path): Output directory

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{zip_path.name}")

    try:
        # Extract ZIP
        safe_path = io_utils.unzip_product(zip_path)

        # Read product
        product, product_type = io_utils.read_product(safe_path)
        print(f"  Type: {product_type}")

        # Process based on product type
        if "GRD" in product_type:
            product = processors.process_grd(product, aoi_wkt)
        elif "SLC" in product_type:
            product = processors.process_slc(product, aoi_wkt)
        else:
            raise ValueError(f"Unknown product type: {product_type}")

        # Save result
        output_name = safe_path.stem.replace(".SAFE", "")
        output_path = str(output_dir / output_name)
        io_utils.save_geotiff(product, output_path, config.OUTPUT_FORMAT)

        # Clean up
        product.dispose()

        return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False


def main():
    """
    Main execution function.

    Orchestrates the complete preprocessing workflow:
    1. Load AOI from GeoJSON
    2. Find all Sentinel-1 ZIP files
    3. Process each file (GRD or SLC)
    4. Save results as GeoTIFF
    5. Display summary statistics
    """
    print("=" * 70)
    print("SENTINEL-1 SAR PREPROCESSING PIPELINE")
    print("=" * 70)
    print(f"Input directory: {config.INPUT_DIR}")
    print(f"Output directory: {config.OUTPUT_DIR}")
    print(f"Target CRS: {config.TARGET_CRS}")
    print("=" * 70)

    # Load AOI
    try:
        aoi_wkt = io_utils.load_aoi(config.AOI_FILE)
    except Exception as e:
        print(f"\nERROR: Failed to load AOI - {e}")
        return

    # Find all Sentinel-1 ZIP files
    zip_files = io_utils.find_sentinel1_files(config.INPUT_DIR)

    if not zip_files:
        print("\nNo ZIP files found in input directory")
        print(f"Expected location: {config.INPUT_DIR}/**/*.zip")
        return

    print(f"Found {len(zip_files)} file(s) to process")

    # Process each file
    processed = 0
    failed = 0

    for zip_path in zip_files:
        if process_sentinel1_file(zip_path, aoi_wkt, config.OUTPUT_DIR):
            processed += 1
        else:
            failed += 1

    # Display summary
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Successfully processed: {processed}")
    print(f"Failed: {failed}")
    print(f"Output directory: {config.OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
