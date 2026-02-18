"""
Parcel library loader - maps parcel IDs to coordinates (lat/lon).
Ready to accept CSV when available.
"""

import csv
from pathlib import Path
from typing import Dict, Optional, Tuple


class ParcelLibrary:
    """
    Load and query parcel library.
    Expected CSV format:
    PARCEL_ID, LATITUDE, LONGITUDE, [optional fields...]
    """
    
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.parcels = {}  # {parcel_id: {'lat': lat, 'lon': lon, ...}}
        self._load()
    
    def _load(self):
        """Load parcel library from CSV."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Parcel library not found: {self.csv_path}")
        
        with open(self.csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            if not reader.fieldnames:
                raise ValueError("CSV is empty or has no headers")
            
            # Look for parcel ID field (case-insensitive)
            parcel_id_field = None
            lat_field = None
            lon_field = None
            
            for field in reader.fieldnames:
                f_lower = field.lower().strip()
                if 'parcel' in f_lower and 'id' in f_lower:
                    parcel_id_field = field
                elif 'lat' in f_lower:
                    lat_field = field
                elif 'lon' in f_lower or 'lng' in f_lower:
                    lon_field = field
            
            if not parcel_id_field or not lat_field or not lon_field:
                raise ValueError(
                    f"CSV must have PARCEL_ID, LATITUDE, LONGITUDE fields\n"
                    f"Found: {reader.fieldnames}"
                )
            
            # Load records
            for row in reader:
                try:
                    parcel_id = row[parcel_id_field].strip()
                    lat = float(row[lat_field])
                    lon = float(row[lon_field])
                    
                    self.parcels[parcel_id] = {
                        'lat': lat,
                        'lon': lon,
                        **{k: v for k, v in row.items() if k not in [parcel_id_field, lat_field, lon_field]}
                    }
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping row due to parsing error: {e}")
    
    def lookup(self, parcel_id: str) -> Optional[Dict]:
        """
        Look up a parcel by ID.
        Returns dict with 'lat', 'lon', and any other fields from CSV.
        """
        return self.parcels.get(parcel_id.strip().upper())
    
    def get_coordinates(self, parcel_id: str) -> Optional[Tuple[float, float]]:
        """
        Get (lat, lon) for a parcel ID.
        Returns tuple or None if not found.
        """
        parcel = self.lookup(parcel_id)
        if parcel:
            return (parcel['lat'], parcel['lon'])
        return None
    
    def list_parcels(self):
        """Return list of all parcel IDs."""
        return sorted(self.parcels.keys())
    
    def __len__(self):
        """Return number of parcels."""
        return len(self.parcels)


def create_test_parcel_library(output_path: str):
    """
    Create a test parcel library CSV for demonstration.
    """
    test_data = [
        ['PARCEL_ID', 'LATITUDE', 'LONGITUDE', 'COUNTY', 'TOWNSHIP'],
        ['OHIO_P001', '40.5', '-82.5', 'Franklin', 'Columbus'],
        ['OHIO_P002', '40.6', '-82.4', 'Franklin', 'Columbus'],
        ['OHIO_P003', '40.7', '-82.3', 'Delaware', 'Delaware'],
        ['OHIO_P004', '40.4', '-82.6', 'Pickaway', 'Pickaway'],
    ]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    print(f"✅ Test parcel library created: {output_path}")


if __name__ == "__main__":
    # Create test library
    test_path = "test_parcel_library.csv"
    create_test_parcel_library(test_path)
    
    # Load and test
    try:
        lib = ParcelLibrary(test_path)
        print(f"✅ Loaded {len(lib)} parcels")
        
        # Test lookup
        coords = lib.get_coordinates('OHIO_P001')
        if coords:
            print(f"✅ OHIO_P001 coordinates: {coords}")
        
        # List all
        print("\nAll parcels:")
        for parcel_id in lib.list_parcels():
            lat, lon = lib.get_coordinates(parcel_id)
            print(f"  {parcel_id:<15} ({lat:.4f}, {lon:.4f})")
    
    except Exception as e:
        print(f"❌ Error: {e}")
