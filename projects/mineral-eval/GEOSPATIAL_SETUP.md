# Geospatial Parcel Lookup - Setup & Usage

## What's New (Feb 17, 2026)

✅ **Parcel Location Lookup** — Search 210K Utica Shale parcels by ID or browse by type curve area  
✅ **Auto Type Curve Selection** — Parcel location automatically determines which TC to apply  
✅ **Interactive Maps** — View parcel location + TC area boundaries with folium  
✅ **One-Click Setup** — Everything runs out of the box

## Files Added

- `utica_parcel_extractor.py` — Extracts Utica parcels from OH_Parcels shapefile (spatial join)
- `utica_parcel_library.csv` — 210K searchable parcel records (ID, lat/lon, TC area)
- `shapefile_reader.py` — Point-in-polygon lookup for shapefile data
- `parcel_library.py` — CSV-based parcel library with coordinate lookup
- `geospatial_lookup.py` — Integration layer (parcel ID → coordinates → TC area)

## Quick Start

### 1. Dashboard Launch

```bash
cd /Users/steveabney/.openclaw/workspace/projects/mineral-eval
streamlit run dashboard.py
```

Open browser → http://localhost:8501

### 2. Use Parcel Location Tab

**Option A: Search by Parcel ID**
- Enter parcel ID (e.g., "53-00887.000")
- Click "🔍 Lookup"
- See location + type curve auto-identified
- View interactive map

**Option B: Browse Available Parcels**
- Select a type curve area from dropdown
- Pick from 20 sample parcels
- Click "📍 View Details"
- See location + map

## Data Structure

### utica_parcel_library.csv

```
PARCEL_ID,LATITUDE,LONGITUDE,CALC_AC,TC_ID,TC_NAME
53-00887.000,39.8507,-80.8243,3.131476,UTICA_0013,Core Dry Gas East
53-01138.021,39.8519,-80.8253,19.235258,UTICA_0013,Core Dry Gas East
...
```

**210,309 records** organized by 19 type curve areas:
- North Oil, North Rich Condensate, North Condensate, etc.
- Core Oil, Core Rich Condensate, Core Condensate, etc.
- South Oil, South Rich Condensate, South Condensate, etc.

## How It Works

### Step 1: Parcel Library Loading
```python
parcel_lib = ParcelLibrary("utica_parcel_library.csv")
coords = parcel_lib.get_coordinates("53-00887.000")  # (39.8507, -80.8243)
```

### Step 2: Type Curve Lookup
```python
tc_lookup = TypeCurveLookup(
    shp_path="Utica_TC_Areas.shp",
    parcel_lib_path="utica_parcel_library.csv"
)
result = tc_lookup.lookup_by_parcel_id("53-00887.000")
# Returns: tc_id, tc_name, coordinates, match status
```

### Step 3: Display on Map
```python
import folium
m = folium.Map(location=[lat, lon], zoom_start=12)
folium.Marker([lat, lon], popup=parcel_id).add_to(m)
# + TC area boundary overlay
```

## TC Areas (19 Total)

| #  | TC ID | TC Name | Parcels |
|----|-------|---------|---------|
| 1 | UTICA_0001 | North Oil | 6,965 |
| 2 | UTICA_0002 | North Rich Condensate | 8,219 |
| 3 | UTICA_0003 | North Condensate | 14,025 |
| 4 | UTICA_0004 | North Lean Condensate | 7,614 |
| 5 | UTICA_0005 | North Wet Gas | 2,488 |
| 6 | UTICA_0006 | North Dry Gas | 19,970 |
| 7 | UTICA_0007 | Core Oil | 5,815 |
| 8 | UTICA_0008 | Core Rich Condensate | 4,481 |
| 9 | UTICA_0009 | Core Condensate | 5,737 |
| 10 | UTICA_0010 | Core Lean Condensate | 5,224 |
| 11 | UTICA_0011 | Core Wet Gas | 14,221 |
| 12 | UTICA_0012 | Core Dry Gas West | 12,188 |
| 13 | UTICA_0013 | Core Dry Gas East | 64,128 |
| 14 | UTICA_0014 | South Dry Gas | 10,882 |
| 15 | UTICA_0015 | South Oil | 15,081 |
| 16 | UTICA_0016 | South Rich Condensate | 5,369 |
| 17 | UTICA_0017 | South Condensate | 3,964 |
| 18 | UTICA_0018 | South Lean Condensate | 2,237 |
| 19 | UTICA_0019 | South Wet Gas | 1,701 |

**Total: 210,309 parcels**

## Dependencies

```bash
python3 -m pip install geopandas folium streamlit-folium pyshp
```

All already installed in your environment.

## Testing

Run the self-test:
```bash
python3 -c "from geospatial_lookup import TypeCurveLookup; ...(see code)"
```

Or run the full demo:
```bash
python3 geospatial_lookup.py
```

## What's Next

- [ ] Multi-parcel batch uploads
- [ ] Export parcel + TC info to reports
- [ ] Custom type curve area shapefiles
- [ ] Sensitivity analysis by TC area

## Architecture

```
Dashboard (Streamlit)
    ↓
Location Tab (Parcel Search)
    ↓
ParcelLibrary (CSV lookup)
    ↓ + GeospatialLookup (Integration)
    ↓
ShapefileReader (Point-in-polygon) ← Utica_TC_Areas.shp
    ↓
folium Map (Interactive visualization)
```

---

**Status:** ✅ Production Ready (Feb 17, 2026)
