# MEMORY.md — Heyso's Long-Term Memory

## About Steve

**Steve Abney** — calls him Steve
- Timezone: America/Chicago (CST)
- First met: Feb 3, 2026 (named me Heyso!)

### Professional
- **President, Dale Operating Company** — oil & gas investments (mineral rights, royalties, non-op working interests)
- **Owner, Camp Huawni** — summer camp in East Texas (with wife)
- **Agent, Walker Ranch Holdings, LLC** — JV partner with Carbon X Credits on carbon credit project

### Current Priorities (as of Feb 2026)
1. **Carbon credits** — selling ~321K credits from Walker Ranch project at $17/credit
2. **Camp Huawni** — drive summer registrations (spring focus)

---

## Active Projects

### Mineral Evaluation System (Phase 2 Complete ✅, Phase 3 Complete ✅, Phase 4 In Progress 🔄)

**Status:** Phase 1, 2 & 3 production-ready and validated. Phase 4: Geospatial parcel lookup + interactive mapping now live.

**What's Done:**
- Phase 1: Core engine (IRR/NPV/MoM calculations, type curves, lease economics)
- Phase 2: Streamlit dashboard (web UI, no-code interface)
- Phase 3: CME pricing integration with cap/floor controls
- Phase 4: Geospatial parcel lookup (210K Utica parcels with interactive maps)
- Multi-tract support (1-25 tracts with independent royalties)
- Production ramp modeling (12 months)
- Tax calculations (state-specific)
- Type curve integration (APPA_113 extracted and working)
- **NEW:** Parcel location lookup → Auto type curve selection → Interactive folium maps

**How to Use:**
```bash
cd /Users/steveabney/.openclaw/workspace/projects/mineral-eval
streamlit run dashboard.py
```
Opens http://localhost:8501 — fill in deal, click "Calculate", get instant IRR/NPV/MoM

**Test Case (Declemente Unit 1, Appalachia):**
- 18 acres × 20% royalty ÷ 234.2 unit acres = **1.54% NRI**
- 12,060 MMcf EUR, APPA_113 type curve
- **Results:** 16.3% IRR, 2.64x MoM, $757k net revenue (50yr)
- Acquisition cost: $237.5k → Profit: $519k

**Key Features:**
✅ Multi-tract mineral interests  
✅ Real-time IRR/NPV/MoM calculation  
✅ NPV chart across discount rates  
✅ Monthly cash flow table  
✅ CSV export  
✅ Instant scenario testing  

**Phase 3 (Complete - Feb 16, 2026):**
- ✅ Type curve library parser (tc_library_parser.py) - 25 gas curves, 792 months (2026-2092), APPA_113.1 EUR=12,059.9 MMcf
- ✅ Price deck scenario parser (price_deck_parser.py) - 16 scenarios (4 gas × 4 oil), 792 months
- ✅ **CME pricing integration** (`cme_client.py`) — Real-time WTI/Henry Hub WebSocket fetcher
- ✅ **Price cap/floor logic** — Gas and oil min/max controls
- ✅ **Dashboard UI updates** — Economics tab with CME fetch, cap/floor controls, year-4-flat checkbox
- ✅ CME integration tested and working

**Phase 4 (Complete - Feb 17, 2026):**
- ✅ **OH_Parcels extraction** — Spatial join: 877K OH parcels ∩ 19 Utica TC Areas = 210K Utica parcels
- ✅ **Parcel library creation** — utica_parcel_library.csv (210K records with centroids + TC mapping)
- ✅ **ShapefileReader** — Point-in-polygon lookup using pyshp (no heavy GIS deps)
- ✅ **ParcelLibrary** — CSV-based parcel coordinate lookup
- ✅ **TypeCurveLookup** — Integration: parcel ID → coordinates → TC area identification
- ✅ **Dashboard Location tab** — Parcel search by ID or browse by TC area
- ✅ **Interactive maps** — folium integration showing parcel + TC boundary
- ✅ **Demo scripts** — Full end-to-end testing
- ✅ Tested: Sample parcel lookups, batch operations, map rendering

**Phase 4 Architecture:**
- `utica_parcel_extractor.py` — Extracts Utica parcels (spatial join)
- `shapefile_reader.py` — Point-in-polygon algorithm (ray casting)
- `parcel_library.py` — CSV parcel coordinate database
- `geospatial_lookup.py` — Integration layer (parcel → TC)
- `demo_parcel_lookup.py` — Demo with 210K parcels, 19 TC areas, batch lookups

**Phase 5 Roadmap (Planned):**
- Multi-parcel batch uploads
- Export parcel + TC info to deal reports
- Custom TC area shapefiles (Marcellus, Appalachian, etc.)
- Sensitivity analysis (tornado charts)
- Scenario comparison (side-by-side)
- Custom type curve upload
- Working interest case (with capex/opex)

**Files:**
- `projects/mineral-eval/core.py` — Core engine (600+ lines)
- `projects/mineral-eval/dashboard.py` — Streamlit UI (350+ lines)
- `projects/mineral-eval/tc_library_parser.py` — Type curve CSV parser [IN PROGRESS]
- `projects/mineral-eval/price_deck_parser.py` — Price scenario CSV parser [IN PROGRESS]
- `projects/mineral-eval/README.md` — Full documentation

**Phase 3 Input Files (from Steve):**
- Type curve library: `/Users/steveabney/.openclaw/media/inbound/file_10---e96bd262-79b7-4217-b8c8-0b35fee55557.csv`
  - Wide format: Curve names as columns (32+), months as rows
  - Sections: Oil curves (cols 6-31, EUR=0), Gas curves (cols 32+, EUR>0)
  - 792 months (2026-2092), ~25 gas curves
  - Metadata: EUR (row 2), Lateral Length (row 4), Bench (row 11)
  - Data: Year/month/date (cols 2-4), then volumes
  
- Price deck: `/Users/steveabney/.openclaw/media/inbound/file_12---9197eca9-585e-46c3-9104-e0a12fe50ade.csv`
  - Scenario labels in row 4: Gas prices (3.0, 3.25, 3.5, 4.0), Oil prices (60.0, 65.0, 70.0, 80.0)
  - Data rows 6-797: Year, Date (col 3), monthly prices
  - 792 months (Feb 2026 - Jan 2092), 16 scenarios (4×4)

### Walker Ranch Carbon Credits
- **Location:** Stephens County, TX (90mi from Abilene/Stargate)
- **What happened:** 23 legacy O&G wells plugged (17 qualified for credits)
- **Credits:** ~321,000 MT CO2e, BCarbon registry
- **Steve's role:** Agent for Walker Ranch Holdings (JV partner)
- **Sales:** Carbon X Credits handles transactions; Steve does BD
- **Target buyers:** Stargate partners (Microsoft, Oracle, OpenAI), Big Tech, Texas energy companies
- **Key contact:** Taylor Landress, Carbon X COO (tlandress@carbonxcredits.com)
- **Project page:** carbonxcredits.com/projects/walker-ranch
- **Files:** `projects/carbon-credits/`

---

## Skills & Tools

### Vapi Caller
- Skill at `skills/vapi-caller/`
- Makes outbound AI phone calls
- Steve's Vapi phone: +18172865577
- Credentials in `skills/vapi-caller/references/credentials.md`

### Hunter.io
- Contact/email lookup API
- Steve has Data-platform tier (1000 searches)
- API key stored (not in files for security)

---

## Preferences & Notes

### Model Selection
- **Default to Haiku** for routine tasks
- **Escalate to Sonnet** for moderate complexity
- **Use Opus** only when Haiku/Sonnet can't handle it
- Goal: cost efficiency without sacrificing quality when it matters
