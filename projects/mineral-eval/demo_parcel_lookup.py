#!/usr/bin/env python3
"""
Quick demo: Parcel lookup + type curve identification
Shows the full workflow: Parcel ID → Location → TC Area → Type Curve
"""

from parcel_library import ParcelLibrary
from geospatial_lookup import TypeCurveLookup
import pandas as pd

def demo():
    print("\n" + "="*70)
    print("⛽ UTICA SHALE PARCEL LOOKUP DEMO")
    print("="*70)
    
    # Initialize
    print("\n📚 Loading data...")
    parcel_lib = ParcelLibrary("utica_parcel_library.csv")
    tc_lookup = TypeCurveLookup(
        shp_path="/Users/steveabney/Downloads/Utica_TC_Areas/Utica_TC_Areas.shp",
        parcel_lib_path="utica_parcel_library.csv"
    )
    
    # Load the CSV for browsing
    parcel_df = pd.read_csv("utica_parcel_library.csv")
    
    print(f"✅ Loaded {len(parcel_df):,} Utica Shale parcels")
    print(f"✅ Loaded 19 type curve areas")
    
    # Demo 1: Lookup specific parcel
    print("\n" + "-"*70)
    print("DEMO 1: Lookup Specific Parcel ID")
    print("-"*70)
    
    test_parcel = "53-00887.000"
    print(f"\n🔍 Looking up parcel: {test_parcel}")
    
    result = tc_lookup.lookup_by_parcel_id(test_parcel)
    
    if result['match']:
        print(f"\n✅ MATCH FOUND")
        print(f"   Parcel ID:     {result['parcel_id']}")
        print(f"   Coordinates:   ({result['lat']:.4f}, {result['lon']:.4f})")
        print(f"   Type Curve ID: {result['tc_id']}")
        print(f"   Type Curve:    {result['tc_name']}")
        
        # Get additional parcel info
        parcel_info = parcel_df[parcel_df['PARCEL_ID'] == test_parcel].iloc[0]
        print(f"   Acreage:       {parcel_info['CALC_AC']:.2f} acres")
    else:
        print(f"\n❌ {result['error']}")
    
    # Demo 2: Browse by type curve area
    print("\n" + "-"*70)
    print("DEMO 2: Browse Parcels by Type Curve Area")
    print("-"*70)
    
    # Show distribution
    print("\n📊 Type Curve Distribution:")
    tc_counts = parcel_df['TC_NAME'].value_counts()
    for i, (tc_name, count) in enumerate(tc_counts.items(), 1):
        if i <= 5:
            print(f"   {i:2}. {tc_name:<30} {count:>6,} parcels")
    print(f"   ... {len(tc_counts) - 5} more areas")
    
    # Sample parcels from one area
    sample_tc = "Core Dry Gas East"
    sample_parcels = parcel_df[parcel_df['TC_NAME'] == sample_tc].head(5)
    
    print(f"\n📍 Sample parcels in '{sample_tc}':")
    for idx, row in sample_parcels.iterrows():
        print(f"   • {row['PARCEL_ID']:<20} ({row['LATITUDE']:.4f}, {row['LONGITUDE']:.4f}) {row['CALC_AC']:>8.2f} acres")
    
    # Demo 3: Multi-parcel lookup
    print("\n" + "-"*70)
    print("DEMO 3: Batch Lookup Multiple Parcels")
    print("-"*70)
    
    test_parcels = [
        "53-00887.000",
        "53-01138.021",
        "53-01138.012"
    ]
    
    print(f"\n🔄 Looking up {len(test_parcels)} parcels...\n")
    
    results_list = []
    for parcel in test_parcels:
        result = tc_lookup.lookup_by_parcel_id(parcel)
        if result['match']:
            results_list.append({
                'Parcel ID': result['parcel_id'],
                'Type Curve': result['tc_name'],
                'TC ID': result['tc_id'],
                'Latitude': f"{result['lat']:.4f}",
                'Longitude': f"{result['lon']:.4f}"
            })
    
    results_df = pd.DataFrame(results_list)
    print(results_df.to_string(index=False))
    
    # Demo 4: Statistics
    print("\n" + "-"*70)
    print("DEMO 4: Utica Shale Portfolio Statistics")
    print("-"*70)
    
    print(f"\n📊 Summary Statistics:")
    print(f"   Total Parcels:          {len(parcel_df):>10,}")
    print(f"   Total Acreage:          {parcel_df['CALC_AC'].sum():>10,.0f} acres")
    print(f"   Avg Parcel Size:        {parcel_df['CALC_AC'].mean():>10,.2f} acres")
    print(f"   Unique Type Curves:     {parcel_df['TC_NAME'].nunique():>10}")
    
    print(f"\n   Type Curve Breakdown:")
    for tc_name, count in tc_counts.items():
        pct = (count / len(parcel_df)) * 100
        print(f"      {tc_name:<30} {count:>6,} parcels ({pct:>5.1f}%)")
    
    # Demo 5: Export sample
    print("\n" + "-"*70)
    print("DEMO 5: Export to CSV")
    print("-"*70)
    
    export_df = parcel_df.head(10).copy()
    export_file = "sample_export.csv"
    export_df.to_csv(export_file, index=False)
    
    print(f"\n✅ Exported {len(export_df)} sample parcels to {export_file}")
    
    # Footer
    print("\n" + "="*70)
    print("✨ Demo Complete!")
    print("="*70)
    print("\n📝 Next Steps:")
    print("   1. Run: streamlit run dashboard.py")
    print("   2. Go to 📍 Location tab")
    print("   3. Enter parcel ID or browse by type curve")
    print("   4. View location on interactive map")
    print("   5. Type curve auto-applied in Production tab")
    print("\n")

if __name__ == "__main__":
    demo()
