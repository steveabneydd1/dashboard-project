"""
Shapefile reader for point-in-polygon type curve lookup.
Uses pyshp (pure Python, no heavy GIS dependencies like shapely/fiona).
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import shapefile
except ImportError:
    raise ImportError("pyshp not installed. Run: pip install pyshp")


class ShapeRecord:
    """Represents a single shapefile record (polygon + attributes)."""
    
    def __init__(self, record_num: int, points: List[Tuple[float, float]], attributes: Dict):
        self.record_num = record_num
        self.points = points  # List of (lon, lat) tuples
        self.attributes = attributes
    
    def point_in_polygon(self, lon: float, lat: float) -> bool:
        """
        Ray casting algorithm to check if a point is inside the polygon.
        Uses a horizontal ray from the point to the right.
        """
        if not self.points or len(self.points) < 3:
            return False
        
        count = 0
        n = len(self.points)
        
        for i in range(n):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % n]
            
            # Check if ray crosses edge
            if ((p1[1] <= lat < p2[1]) or (p2[1] <= lat < p1[1])):
                # Calculate x coordinate of intersection
                x_intersect = (p2[0] - p1[0]) * (lat - p1[1]) / (p2[1] - p1[1]) + p1[0]
                if lon < x_intersect:
                    count += 1
        
        # Odd number of intersections = inside
        return count % 2 == 1


class ShapefileReader:
    """
    Read ESRI shapefiles (.shp + .dbf) and perform point-in-polygon lookups.
    Uses pyshp for reliable parsing.
    """
    
    def __init__(self, shp_path: str):
        self.shp_path = Path(shp_path)
        self.records = []
        self._load()
    
    def _load(self):
        """Load and parse the shapefile using pyshp."""
        if not self.shp_path.exists():
            raise FileNotFoundError(f"Shapefile not found: {self.shp_path}")
        
        # pyshp auto-finds .dbf and .shx files based on .shp name
        shp_str = str(self.shp_path.with_suffix(''))
        
        try:
            reader = shapefile.Reader(shp_str)
        except Exception as e:
            raise RuntimeError(f"Failed to read shapefile: {e}")
        
        # Check shape type
        if reader.shapeType != shapefile.POLYGON:
            raise ValueError(f"Expected POLYGON shapefile, got type {reader.shapeType}")
        
        # Extract field names
        field_names = [field[0] for field in reader.fields[1:]]  # Skip first (record ID)
        
        # Process each record
        for i, rec in enumerate(reader.shapeRecords()):
            shape = rec.shape
            record = rec.record
            
            # Extract polygon points (first ring = outer boundary)
            if shape.parts:
                start_idx = shape.parts[0]
                end_idx = shape.parts[1] if len(shape.parts) > 1 else len(shape.points)
                polygon_points = [(x, y) for x, y in shape.points[start_idx:end_idx]]
            else:
                polygon_points = [(x, y) for x, y in shape.points]
            
            # Build attributes dict
            attrs = {}
            for j, field_name in enumerate(field_names):
                if j < len(record):
                    attrs[field_name] = record[j]
            
            # Create record
            if len(polygon_points) >= 3:
                shape_rec = ShapeRecord(i + 1, polygon_points, attrs)
                self.records.append(shape_rec)
        
        print(f"✅ Loaded {len(self.records)} polygons from shapefile")
    
    def lookup_point(self, lon: float, lat: float) -> Optional[Dict]:
        """
        Find which polygon contains the given point.
        Returns the attributes dict of the containing polygon, or None.
        """
        for record in self.records:
            if record.point_in_polygon(lon, lat):
                return record.attributes
        return None
    
    def get_all_records(self) -> List[ShapeRecord]:
        """Return all records."""
        return self.records
    
    def list_type_curves(self, tc_id_field: str = 'TC_ID', tc_name_field: str = 'TC_NAME') -> List[Dict]:
        """Return list of type curves with ID and name."""
        curves = []
        for record in self.records:
            curves.append({
                'tc_id': record.attributes.get(tc_id_field, 'N/A'),
                'tc_name': record.attributes.get(tc_name_field, 'N/A'),
            })
        return curves


if __name__ == "__main__":
    # Test
    try:
        reader = ShapefileReader("/Users/steveabney/Downloads/Utica_TC_Areas/Utica_TC_Areas.shp")
        
        print(f"\n✅ Loaded {len(reader.records)} type curve areas")
        print("\nAvailable type curves:")
        for curve in reader.list_type_curves():
            print(f"  {curve['tc_id']:<15} {curve['tc_name']}")
        
        # Test point lookup (Ohio, near center)
        print("\n--- Testing point lookup ---")
        test_lon, test_lat = -82.5, 40.5
        result = reader.lookup_point(test_lon, test_lat)
        if result:
            print(f"✅ Point ({test_lon}, {test_lat}) is in: {result.get('TC_NAME', 'Unknown')}")
        else:
            print(f"❌ Point ({test_lon}, {test_lat}) is outside all polygons")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
