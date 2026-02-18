# Phase 3: Type Curve & Price Deck Parsers

## Overview
Built two production-ready parser modules for the mineral evaluation system's Phase 3 integration.

## Modules Created

### 1. **tc_library_parser.py** (9.6 KB)
Type Curve Library Parser - Extracts GAS type curve definitions from CSV.

**Key Features:**
- Parses type curve library CSV with 25 GAS curve definitions
- **Skips oil curves (columns 6-31)**, only parses gas curves (columns 32+)
- Uses actual date column (column 4) for validation instead of month counter
- Extracts curve metadata:
  - Name (e.g., APPA_113.1, APPA_104.24, APPA_104.25, etc.)
  - EUR in MMcf (Estimated Ultimate Recovery)
    - APPA_113.1 gas: 12,059.9 MMcf (vs oil version APPA_113: 0)
    - APPA_104.24+ gas: 3,279.9 MMcf each
  - Lateral length in feet (typically 10,000 ft)
  - Bench designation (e.g., Point Pleasant, Marcellus, WCA, WCB, LS)
  - 35 months of monthly production volumes in MMcf (2026-2028)
- Global caching to avoid re-reading CSV
- Clean dataclass-based API

**CSV Structure Handled:**
```
Columns 0-5:    Metadata columns (Year, Month counter, Date)
Columns 6-31:   Oil curves (SKIPPED)
Columns 32+:    Gas curves (PARSED)
Row 2:          EUR values
Row 4:          Lateral length values
Row 11:         Bench designations
Row 14+:        Monthly production data with dates in column 4
```

**Main Interface:**
```python
from tc_library_parser import parse_tc_library, TypeCurveData, get_curve, clear_cache

# Parse entire library (gas curves only)
curves = parse_tc_library("/path/to/type_curves.csv")
# Returns: Dict[str, TypeCurveData] with 25 gas curves

# Get specific gas curve
curve = get_curve("APPA_113.1", csv_path="/path/to/type_curves.csv")
# curve.name, curve.eur_mmcf, curve.lateral_length_ft, curve.bench, curve.monthly_volumes
```

**Data Structures:**
```python
@dataclass
class TypeCurveData:
    name: str                          # e.g., "APPA_113.1" (gas)
    eur_mmcf: float                   # e.g., 12059.9 MMcf
    lateral_length_ft: float          # e.g., 10000.0 ft
    bench: str                        # e.g., "Point Pleasant"
    monthly_volumes: List[float]      # 35 months of volumes (2026-2028)
    product_type: str = "gas"
```

**Test Results:**
- ✓ Parses 25 GAS type curves (skips 25 oil curves in columns 6-31)
- ✓ Extracts correct EUR values:
  - APPA_113.1 gas: 12,059.9 MMcf
  - APPA_104.24-47 gas: 3,279.9 MMcf each
- ✓ Extracts bench for all curves (Point Pleasant, Marcellus, etc.)
- ✓ Parses 35 months of production data per curve (uses date column 4)
- ✓ Year 1 (12 months) production for APPA_113.1: 4,149.9 MMcf
- ✓ Caching works correctly (returns cached dict on subsequent calls)

---

### 2. **price_deck_parser.py** (10.2 KB)
Price Deck Parser - Extracts price scenarios from CSV.

**Key Features:**
- Parses price deck CSV with multiple commodity scenarios
- Extracts gas price scenarios: $3.0, $4.0, $5.0, $6.0 per MMBtu
- Extracts oil price scenarios: $60, $65, $70, $80 per bbl
- Creates 16 scenario combinations (4 gas × 4 oil)
- Monthly dates and prices for each scenario
- Global caching to avoid re-reading CSV
- Clean dataclass-based API

**Main Interface:**
```python
from price_deck_parser import parse_price_deck, PriceScenario, get_scenario, clear_cache

# Parse all scenarios
scenarios = parse_price_deck("/path/to/price_deck.csv")
# Returns: Dict[str, PriceScenario]

# Get specific scenario
scenario = get_scenario("Gas_3.0_Oil_60", csv_path="/path/to/price_deck.csv")
# scenario.name, scenario.gas_price, scenario.oil_price
# scenario.monthly_dates, scenario.monthly_gas_prices, scenario.monthly_oil_prices
```

**Data Structures:**
```python
@dataclass
class PriceScenario:
    name: str                         # e.g., "Gas_3.0_Oil_60"
    gas_price: float                  # e.g., 3.0 $/MMBtu
    oil_price: float                  # e.g., 60.0 $/bbl
    monthly_dates: List[str]          # YYYY-MM-DD format
    monthly_gas_prices: List[float]   # $/MMBtu per month
    monthly_oil_prices: List[float]   # $/bbl per month
```

**Test Results:**
- ✓ Parses 4 gas price scenarios (3.0, 4.0, 5.0, 6.0 $/MMBtu)
- ✓ Parses 4 oil price scenarios (60, 65, 70, 80 $/bbl)
- ✓ Creates 16 scenario combinations
- ✓ Extracts monthly dates and prices for each scenario
- ✓ Caching works correctly

---

## Usage Examples

### Type Curves
```python
from tc_library_parser import parse_tc_library

tc_csv = "/Users/steveabney/.openclaw/media/inbound/file_10---e96bd262-79b7-4217-b8c8-0b35fee55557.csv"
curves = parse_tc_library(tc_csv)

# Iterate over curves
for curve_name, curve_data in curves.items():
    print(f"{curve_name}: EUR={curve_data.eur_mmcf:.1f}, Bench={curve_data.bench}")
    print(f"  Production: {len(curve_data.monthly_volumes)} months")
    print(f"  Year 1 avg: {sum(curve_data.monthly_volumes[:12]) / 12:.1f} MMcf/month")
```

### Price Scenarios
```python
from price_deck_parser import parse_price_deck

price_csv = "/Users/steveabney/.openclaw/media/inbound/file_12---9197eca9-585e-46c3-9104-e0a12fe50ade.csv"
scenarios = parse_price_deck(price_csv)

# Access specific scenario
scenario = scenarios["Gas_3.0_Oil_60"]
for date, gas_price, oil_price in zip(scenario.monthly_dates, 
                                       scenario.monthly_gas_prices,
                                       scenario.monthly_oil_prices):
    print(f"{date}: Gas=${gas_price:.2f}, Oil=${oil_price:.2f}")
```

---

## File Locations
- **tc_library_parser.py**: `/Users/steveabney/.openclaw/workspace/projects/mineral-eval/tc_library_parser.py`
- **price_deck_parser.py**: `/Users/steveabney/.openclaw/workspace/projects/mineral-eval/price_deck_parser.py`

## Standards Compliance
- ✓ Standard library only (csv, logging, dataclasses, datetime)
- ✓ No external dependencies (pandas/numpy not required)
- ✓ Clean dataclass-based return types
- ✓ Proper error handling and logging
- ✓ Global caching for performance
- ✓ Module-level functions and helper utilities
- ✓ Comprehensive docstrings
- ✓ Test functions included (run as __main__)

## Integration Notes
Both modules are ready for consumption by the dashboard and other Phase 3 components:
- Import functions directly
- Parse CSV files once, cache results
- Access parsed data through clean dataclass interfaces
- Logging can be configured at the application level

---

**Created:** 2026-02-15  
**Status:** Production Ready ✓
