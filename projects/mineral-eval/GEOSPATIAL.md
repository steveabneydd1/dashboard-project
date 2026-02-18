# Geospatial Type Curve Lookup

Automatically select the correct type curve based on parcel location using shapefiles and parcel coordinates.

## How It Works

1. **User enters Parcel ID** in the dashboard
2. **Parcel library lookup** → Extracts latitude/longitude from parcel database
3. **Shapefile point-in-polygon** → Finds which type curve area contains those coordinates
4. **Auto-populate type curve** → Sets the correct type curve (e.g., "Core Wet Gas")

## System Components

### 1. Shapefile Reader (`shapefile_reader.py`)
- Reads ESRI shapefiles (.shp + .dbf + .shx files)
- Extracts polygon boundaries and attributes
- Implements point-in-polygon algorithm (ray casting)
- Returns type curve ID and name for any coordinate

**Features:**
- Pure Python (uses `pyshp` library, not heavy GIS like Shapely/GDAL)
- WGS84 compatible (tested with Utica_TC_Areas)
- Supports arbitrary attribute fields

### 2. Parcel Library (`parcel_library.py`)
- Loads parcel database from CSV
- Expected columns: PARCEL_ID, LATITUDE, LONGITUDE
- Case-insensitive field detection
- Fast lookup by parcel ID

**CSV Format:**
```
PARCEL_ID,LATITUDE,LONGITUDE,COUNTY,TOWNSHIP
OHIO_P001,40.5123,-82.4567,Franklin,Columbus
OHIO_P002,40.5456,-82.3890,Franklin,New Albany
...
```

### 3. Geospatial Lookup (`geospatial_lookup.py`)
- Orchestrates the lookup workflow
- Maps: Parcel ID → Coordinates → Type Curve
- Error handling and validation
- Supports both parcel ID and manual coordinate lookups

## Setup

### Step 1: Install Dependencies
```bash
pip install pyshp
```

### Step 2: Prepare Your Data

**Shapefiles:**
- Place your .shp, .dbf, .shx files in a directory
- Ensure WGS84 coordinate system (EPSG:4326)
- Add `TC_ID` and `TC_NAME` fields to the DBF

**Parcel Library:**
- Create CSV with columns: PARCEL_ID, LATITUDE, LONGITUDE
- Example: `ohio_parcels.csv`

### Step 3: Initialize in Dashboard

```python
from geospatial_lookup import TypeCurveLookup

lookup = TypeCurveLookup(
    shp_path="path/to/Utica_TC_Areas/Utica_TC_Areas.shp",
    parcel_lib_path="path/to/ohio_parcels.csv",
    tc_id_field='TC_ID',
    tc_name_field='TC_NAME'
)
```

## Usage

### Lookup by Parcel ID
```python
result = lookup.lookup_by_parcel_id('OHIO_P001')
if result['match']:
    print(f"Type Curve: {result['tc_name']}")
```

### Lookup by Coordinates
```python
result = lookup.lookup_by_coordinates(lat=40.5, lon=-82.5)
if result['match']:
    print(f"Type Curve: {result['tc_name']}")
```

## Current Status

✅ **Shapefile Reader** — Working with Utica_TC_Areas (19 polygons loaded)
✅ **Point-in-Polygon** — Ray casting algorithm implemented
⏳ **Parcel Library** — Waiting for your CSV file
⏳ **Dashboard Integration** — Ready to wire up once parcel library arrives

## Files

- `shapefile_reader.py` — ESRI shapefile parser + point-in-polygon
- `parcel_library.py` — Parcel CSV loader and lookup
- `geospatial_lookup.py` — Unified lookup interface
- `GEOSPATIAL.md` — This documentation

## Testing

Test the system before dashboard integration:

```bash
# Test shapefile reader
python3 shapefile_reader.py

# Test geospatial lookup (with test parcel library)
python3 geospatial_lookup.py
```

## Next Steps

1. **Provide parcel library CSV** with columns: PARCEL_ID, LATITUDE, LONGITUDE
2. **Dashboard integration** — Add parcel ID input field
3. **Auto-populate type curve** based on geospatial lookup
4. **Support multiple basins** (Appalachia, Permian, Haynesville, etc.)

## Troubleshooting

**"pyshp not installed"**
```bash
pip install pyshp
```

**"Parcel library not found"**
- Ensure CSV file path is correct
- Check file exists and is readable

**"Coordinates outside all polygons"**
- Verify coordinates are within shapefile extent
- Check coordinate system (must be WGS84 / EPSG:4326)
- Use a known point within the area to test

**Point not matching expected polygon**
- May be on polygon boundary (ray casting has edge cases)
- Verify coordinates are inside expected polygon using external tool
- Check for polygon orientation issues

---

For more on point-in-polygon algorithms: https://en.wikipedia.org/wiki/Point_in_polygon
For ESRI shapefile spec: https://www.esri.com/content/dam/esrisites/sitecore/Home/Microsites/Product-Pages/shapefilz.pdf
