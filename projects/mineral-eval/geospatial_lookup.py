"""
Geospatial type curve lookup system.
Maps parcel ID -> coordinates -> shapefile polygon -> type curve.
"""

from pathlib import Path
from typing import Optional, Dict, List
from shapefile_reader import ShapefileReader
from parcel_library import ParcelLibrary


class TypeCurveLookup:
    """
    Lookup type curves for parcels using geospatial shapefiles.
    """
    
    def __init__(
        self,
        shp_path: str,
        parcel_lib_path: str,
        tc_id_field: str = 'TC_ID',
        tc_name_field: str = 'TC_NAME'
    ):
        """
        Initialize lookup system.
        
        Args:
            shp_path: Path to shapefile (.shp)
            parcel_lib_path: Path to parcel library CSV
            tc_id_field: Name of type curve ID field in shapefile
            tc_name_field: Name of type curve name field in shapefile
        """
        self.shp_path = shp_path
        self.parcel_lib_path = parcel_lib_path
        self.tc_id_field = tc_id_field
        self.tc_name_field = tc_name_field
        
        self.shapefile = None
        self.parcel_lib = None
        self._load()
    
    def _load(self):
        """Load shapefile and parcel library."""
        try:
            self.shapefile = ShapefileReader(self.shp_path)
            print(f"✅ Loaded shapefile: {self.shp_path}")
        except Exception as e:
            print(f"⚠️  Shapefile load error: {e}")
        
        try:
            self.parcel_lib = ParcelLibrary(self.parcel_lib_path)
            print(f"✅ Loaded parcel library: {self.parcel_lib_path} ({len(self.parcel_lib)} parcels)")
        except FileNotFoundError:
            print(f"⚠️  Parcel library not found: {self.parcel_lib_path}")
            print("   Ready to load when CSV is available")
        except Exception as e:
            print(f"⚠️  Parcel library load error: {e}")
    
    def lookup_by_parcel_id(self, parcel_id: str) -> Optional[Dict]:
        """
        Lookup type curve for a parcel ID.
        
        Returns dict with:
            - parcel_id: Input parcel ID
            - lat, lon: Coordinates from parcel library
            - tc_id: Type curve ID (from shapefile)
            - tc_name: Type curve name (from shapefile)
            - match: Whether a match was found
        """
        result = {
            'parcel_id': parcel_id,
            'lat': None,
            'lon': None,
            'tc_id': None,
            'tc_name': None,
            'match': False,
            'error': None,
        }
        
        # Check parcel library
        if not self.parcel_lib:
            result['error'] = "Parcel library not loaded"
            return result
        
        coords = self.parcel_lib.get_coordinates(parcel_id)
        if not coords:
            result['error'] = f"Parcel ID not found: {parcel_id}"
            return result
        
        lat, lon = coords
        result['lat'] = lat
        result['lon'] = lon
        
        # Check shapefile
        if not self.shapefile:
            result['error'] = "Shapefile not loaded"
            return result
        
        attrs = self.shapefile.lookup_point(lon, lat)
        if not attrs:
            result['error'] = f"Coordinates outside all polygons: ({lat}, {lon})"
            return result
        
        result['tc_id'] = attrs.get(self.tc_id_field, 'Unknown')
        result['tc_name'] = attrs.get(self.tc_name_field, 'Unknown')
        result['match'] = True
        
        return result
    
    def lookup_by_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Lookup type curve for given coordinates.
        
        Returns dict with tc_id, tc_name, match status.
        """
        result = {
            'lat': lat,
            'lon': lon,
            'tc_id': None,
            'tc_name': None,
            'match': False,
            'error': None,
        }
        
        if not self.shapefile:
            result['error'] = "Shapefile not loaded"
            return result
        
        attrs = self.shapefile.lookup_point(lon, lat)
        if not attrs:
            result['error'] = f"Coordinates outside all polygons"
            return result
        
        result['tc_id'] = attrs.get(self.tc_id_field, 'Unknown')
        result['tc_name'] = attrs.get(self.tc_name_field, 'Unknown')
        result['match'] = True
        
        return result
    
    def list_available_type_curves(self) -> List[Dict]:
        """List all available type curves from shapefile."""
        if not self.shapefile:
            return []
        return self.shapefile.list_type_curves(self.tc_id_field, self.tc_name_field)
    
    def list_available_parcels(self) -> List[str]:
        """List all available parcel IDs from parcel library."""
        if not self.parcel_lib:
            return []
        return self.parcel_lib.list_parcels()


def demo():
    """Demo the lookup system."""
    print("\n" + "="*80)
    print("GEOSPATIAL TYPE CURVE LOOKUP DEMO")
    print("="*80)
    
    # Initialize
    lookup = TypeCurveLookup(
        shp_path="/Users/steveabney/Downloads/Utica_TC_Areas/Utica_TC_Areas.shp",
        parcel_lib_path="test_parcel_library.csv",  # Will use test data
        tc_id_field='TC_ID',
        tc_name_field='TC_NAME'
    )
    
    # Test 1: List type curves
    print("\n📋 Available Type Curves:")
    for curve in lookup.list_available_type_curves():
        print(f"  {curve['tc_id']:<15} {curve['tc_name']}")
    
    # Test 2: Lookup by parcel ID (if test library exists)
    print("\n🔍 Lookup by Parcel ID:")
    test_parcel = 'OHIO_P001'
    result = lookup.lookup_by_parcel_id(test_parcel)
    if result['match']:
        print(f"  ✅ {test_parcel}")
        print(f"     Coordinates: ({result['lat']:.4f}, {result['lon']:.4f})")
        print(f"     Type Curve: {result['tc_id']} - {result['tc_name']}")
    else:
        print(f"  ℹ️  {result['error']}")
    
    # Test 3: Lookup by coordinates
    print("\n🗺️  Lookup by Coordinates:")
    test_lon, test_lat = -82.5, 40.5
    result = lookup.lookup_by_coordinates(test_lat, test_lon)
    if result['match']:
        print(f"  ✅ ({test_lat}, {test_lon})")
        print(f"     Type Curve: {result['tc_id']} - {result['tc_name']}")
    else:
        print(f"  ℹ️  {result['error']}")


if __name__ == "__main__":
    demo()
