# Phase 3 Status - Type Curve Library & Price Scenario Integration

## ✅ Complete

### Parsers Built & Tested
1. **tc_library_parser.py**
   - Parses type curve library CSV (file_10)
   - Extracts 25 gas type curves from columns 32+ (skips oil curves in cols 6-31)
   - 792 months of data per curve (2026-2092)
   - Metadata: EUR, Lateral Length, Bench designation
   - Caching enabled for performance
   - ✅ Verified: APPA_113.1 shows EUR=12,059.9 MMcf
   
2. **price_deck_parser.py**
   - Parses price deck CSV (file_12)
   - Extracts 16 price scenarios (4 gas prices × 4 oil prices)
   - 792 months of monthly price forecasts (2026-2092)
   - Gas prices: $3.0, $3.25, $3.5, $4.0/MMBtu
   - Oil prices: $60, $65, $70, $80/bbl
   - Caching enabled for performance
   - ✅ Verified: All 792 months extracted correctly

### CSV Structure Understood
- **Type curves**: Oil curves (cols 6-31, EUR=0) separate from gas curves (cols 32+)
- **Prices**: Scenario labels in row 4, data starts row 6, uses actual date (col 3) for validation
- **Month encoding**: Sequential counter (1-12 for 2026, 12-30 for 2027, etc.) in col 3
  - Use actual date in col 4 for validation instead

## ⏳ Next Steps for Dashboard Integration

### 1. Extend Dashboard Inputs (tab1 or new tab)
- Add type curve selector dropdown (populated from tc_library_parser)
- Display selected curve metadata (EUR, lateral length, bench)
- Replace hardcoded APPA_113 with selected curve's monthly volumes

### 2. Add Price Scenario Selector
- New dropdown for price scenarios (from price_deck_parser)
- Show scenario details (base gas/oil prices, date range)
- Allow user to select specific scenario for valuation

### 3. Update Economic Calculation
- When type curve selected: Use curve's monthly_volumes instead of APPA_113_VOLUMES
- When price scenario selected: Use scenario's monthly_gas_prices and monthly_oil_prices
- Calculate IRR/NPV/MoM with selected type curve + price scenario

### 4. Validation & Testing
- Test APPA_113.1 (gas) with original Declemente Unit 1 case
  - Should match Excel model: 16.3% IRR, 2.636x MoM
  - Note: Use APPA_113.1, NOT APPA_113 (which is the oil curve)
- Test 2-3 different type curves
- Test multiple price scenarios on same deal
- Scenario comparison (side-by-side results)

### 5. Future Enhancements (Phase 3B)
- Sensitivity analysis: IRR/MoM across all type curves and price scenarios
- Tornado charts (tornado sensitivity analysis)
- Scenario comparison dashboard
- CSV export with scenario comparison results

## Implementation Notes

### Parser Integration Pattern
```python
# In dashboard.py:
from tc_library_parser import parse_tc_library, get_curve
from price_deck_parser import parse_price_deck, get_scenario

# Load parsers on app init
tc_lib_path = "/path/to/file_10.csv"
price_deck_path = "/path/to/file_12.csv"

curves = parse_tc_library(tc_lib_path)  # Returns {name: TypeCurveData}
scenarios = parse_price_deck(price_deck_path)  # Returns {name: PriceScenario}

# In sidebar/form:
selected_curve = st.selectbox("Type Curve", list(curves.keys()))
curve_data = curves[selected_curve]

selected_scenario = st.selectbox("Price Scenario", list(scenarios.keys()))
scenario_data = scenarios[selected_scenario]

# Use in calculation:
inputs.monthly_gross_gas_volumes = curve_data.monthly_volumes
inputs.monthly_gas_prices = scenario_data.monthly_gas_prices
inputs.monthly_oil_prices = scenario_data.monthly_oil_prices
```

### File Structure
```
mineral-eval/
├── core.py                      # Core engine (no changes needed)
├── dashboard.py                 # EXTEND with curve/scenario selectors
├── appa113_volumes.py          # Keep for backward compatibility
├── tc_library_parser.py        # ✅ NEW - Parse type curves
├── price_deck_parser.py        # ✅ NEW - Parse price scenarios
├── test_declemente.py          # Can be updated to use new parsers
├── README.md                    # Update with new features
└── PHASE3_STATUS.md            # This file
```

## Testing Checklist

- [ ] tc_library_parser correctly loads and caches 25 curves
- [ ] APPA_113.1 EUR matches expected (12,059.9 MMcf)
- [ ] price_deck_parser loads all 16 scenarios
- [ ] Dashboard displays type curve dropdown
- [ ] Dashboard displays price scenario dropdown
- [ ] Selected curve metadata shown in UI
- [ ] Selected scenario details shown in UI
- [ ] Dashboard uses selected curve's volumes in calculation
- [ ] Dashboard uses selected scenario's prices in calculation
- [ ] Declemente Unit 1 with APPA_113.1 + base scenario matches Excel (16.3% IRR)
- [ ] Multi-scenario comparison works
- [ ] CSV export includes selected curve and scenario names

## Questions for Steve

1. **Oil curves (APPA_113 at col 6)**: Should these be included in the future? Currently only parsing gas curves (cols 32+).
2. **Default selections**: Which type curve and price scenario should be defaults when dashboard loads?
3. **Scenario naming**: Current format is "Gas_3.0_Oil_60" - prefer this or different naming?
4. **Prices**: Should we offer more/different gas/oil price scenarios in future?
5. **Sensitivity analysis**: High priority for Phase 3B?
