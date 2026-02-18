# 📊 Streamlit Dashboard - Phase 2

Interactive web interface for mineral interest evaluation.

## Quick Start

```bash
cd /Users/steveabney/.openclaw/workspace/projects/mineral-eval
streamlit run dashboard.py
```

This opens a web browser at `http://localhost:8501`

## Features

### 📋 Input Sections

1. **Deal Setup**
   - Deal name, basin, type curve selection
   - Multi-tract support (1-25 tracts)
   - Each tract: mineral acres, royalty rate, unit size

2. **Production**
   - Gas/oil EUR (MMcf/MBbls)
   - Shrink factor, NGL yield
   - Shows calculated total NRI

3. **Economics**
   - Gas, oil, NGL prices
   - Price differentials
   - Real-time price computation

4. **Costs & Taxes**
   - GP&T costs (deal-specific)
   - Cost-bearing lease toggle
   - Acquisition costs, G&A fees
   - Severance and ad valorem taxes (by %)

5. **Timing**
   - Development delays and ramp duration
   - Spud to sales timing
   - Analysis period (10-100 years)
   - Selectable discount rates

### 📈 Results

- **Key Metrics**: IRR, MoM, Payback, PV-10
- **Financial Summary**: Investment, Revenue, Net Cash Flow
- **NPV Chart**: Shows NPV across discount rates
- **Cash Flow Detail**: Monthly detail for first 60 months
- **Export**: Download cash flows to CSV

## Workflow

1. **Set up deal basics** (name, basin, tracts)
2. **Configure production** (EUR, shrink, NGL)
3. **Input prices & differentials**
4. **Set costs, taxes, fees**
5. **Specify timing assumptions**
6. **Click "Calculate IRR & NPV"**
7. **Review results, download CSV if needed**
8. **Adjust assumptions and re-run** (instant feedback)

## Next Steps

- [ ] Add sensitivity analysis charts (price/EUR/discount rate tornado)
- [ ] Support for custom type curves (manual entry)
- [ ] Scenario comparison (side-by-side deals)
- [ ] PDF export with charts
- [ ] Working interest sensitivity case (Phase 3)
- [ ] Land database integration
