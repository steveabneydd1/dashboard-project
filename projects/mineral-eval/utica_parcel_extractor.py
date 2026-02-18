"""
Extract Utica Shale parcels from OH_Parcels.
Performs spatial join: OH_Parcels ∩ Utica_TC_Areas
Outputs parcel library CSV with centroids and TC info.
"""

import geopandas as gpd
from pathlib import Path
import csv


def extract_utica_parcels(
    parcel_shp: str,
    tc_areas_shp: str,
    output_csv: str = "utica_parcel_library.csv"
):
    """
    Extract parcels within Utica TC areas and save as searchable library.
    
    Args:
        parcel_shp: Path to OH_Parcels.shp
        tc_areas_shp: Path to Utica_TC_Areas.shp
        output_csv: Output CSV path
    
    Returns:
        GeoDataFrame with filtered parcels
    """
    print("📍 Extracting Utica Shale parcels...")
    
    # Load both shapefiles
    print("   Loading OH_Parcels (877K parcels)...")
    parcels = gpd.read_file(parcel_shp)
    
    print("   Loading Utica_TC_Areas (19 regions)...")
    tc_areas = gpd.read_file(tc_areas_shp)
    
    # Ensure same CRS
    parcels = parcels.to_crs(tc_areas.crs)
    
    # Spatial join: parcels within TC areas
    print("   Performing spatial join...")
    utica_parcels = gpd.sjoin(parcels, tc_areas, how='inner', predicate='within')
    
    print(f"   ✅ Found {len(utica_parcels)} parcels in Utica areas")
    
    # Calculate centroids
    print("   Computing centroids...")
    utica_parcels['centroid'] = utica_parcels.geometry.centroid
    utica_parcels['LATITUDE'] = utica_parcels['centroid'].y
    utica_parcels['LONGITUDE'] = utica_parcels['centroid'].x
    
    # Prepare output
    output_cols = [
        'PARCEL_ID',
        'LATITUDE',
        'LONGITUDE',
        'CALC_AC',
        'TC_ID',
        'TC_NAME'
    ]
    
    output_df = utica_parcels[output_cols].copy()
    output_df = output_df.drop_duplicates(subset=['PARCEL_ID'])
    
    # Save CSV
    output_df.to_csv(output_csv, index=False)
    print(f"\n✅ Parcel library saved: {output_csv}")
    print(f"   Records: {len(output_df)}")
    print(f"   Columns: {output_cols}")
    
    # Show distribution by TC area
    print(f"\n📊 Distribution by Type Curve Area:")
    tc_counts = output_df['TC_NAME'].value_counts()
    for tc_name, count in tc_counts.items():
        print(f"   {tc_name:<25} {count:>6} parcels")
    
    return output_df


if __name__ == "__main__":
    parcel_shp = "/Users/steveabney/Downloads/OH_Parcels/OH_Parcels.shp"
    tc_areas_shp = "/Users/steveabney/Downloads/Utica_TC_Areas/Utica_TC_Areas.shp"
    output_csv = "utica_parcel_library.csv"
    
    try:
        df = extract_utica_parcels(parcel_shp, tc_areas_shp, output_csv)
        print(f"\n🎯 Sample records:")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
