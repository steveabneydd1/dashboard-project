"""
Streamlit Dashboard for Mineral & Royalty Interest Evaluation
Interactive scenario analysis and sensitivity testing
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from core import DealInputs, Tract, MineralEvaluation
from appa113_volumes import APPA113_VOLUMES
import sys

# Map dependencies
try:
    import folium
    from streamlit_folium import st_folium
    HAS_MAP_DEPS = True
except ImportError as e:
    HAS_MAP_DEPS = False
    MAP_ERROR = str(e)

# Page configuration
st.set_page_config(
    page_title="Mineral Interest Evaluator",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⛽ Mineral & Royalty Interest Evaluator")
st.markdown("Interactive scenario analysis for Dale Operating Company mineral purchases")

# Load parcel library and TC areas for geospatial lookup
@st.cache_resource
def load_geospatial_data():
    try:
        from parcel_library import ParcelLibrary
        from geospatial_lookup import TypeCurveLookup
        
        parcel_lib = ParcelLibrary("utica_parcel_library.csv")
        tc_lookup = TypeCurveLookup(
            shp_path="/Users/steveabney/Downloads/Utica_TC_Areas/Utica_TC_Areas.shp",
            parcel_lib_path="utica_parcel_library.csv",
            tc_id_field='TC_ID',
            tc_name_field='TC_NAME'
        )
        return parcel_lib, tc_lookup
    except FileNotFoundError as e:
        st.error(f"❌ File not found: {e}")
        return None, None
    except Exception as e:
        st.error(f"❌ Geospatial data error: {type(e).__name__}: {e}")
        return None, None

# Load type curve library for all available curves
@st.cache_resource
def load_type_curve_library():
    try:
        from tc_library_parser import TypeCurveLibrary
        tc_lib = TypeCurveLibrary("TC.csv")
        return tc_lib
    except Exception as e:
        st.warning(f"⚠️ Type curve library not available: {e}")
        return None

parcel_lib, tc_lookup = load_geospatial_data()
tc_library = load_type_curve_library()

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'gas_price' not in st.session_state:
    st.session_state.gas_price = 3.68
if 'oil_price' not in st.session_state:
    st.session_state.oil_price = 61.0
if 'ngl_price' not in st.session_state:
    st.session_state.ngl_price = 20.13
if 'cap_gas' not in st.session_state:
    st.session_state.cap_gas = None
if 'floor_gas' not in st.session_state:
    st.session_state.floor_gas = None
if 'cap_oil' not in st.session_state:
    st.session_state.cap_oil = None
if 'floor_oil' not in st.session_state:
    st.session_state.floor_oil = None
if 'year4_flat' not in st.session_state:
    st.session_state.year4_flat = False
if 'parcel_lookup_result' not in st.session_state:
    st.session_state.parcel_lookup_result = None
if 'selected_tc_id' not in st.session_state:
    st.session_state.selected_tc_id = 'APPA_113'
if 'selected_tc_name' not in st.session_state:
    st.session_state.selected_tc_name = 'APPA_113'
if 'selected_tc_volumes' not in st.session_state:
    st.session_state.selected_tc_volumes = APPA113_VOLUMES

# Sidebar: Deal Setup
st.sidebar.header("📋 Deal Setup")

deal_name = st.sidebar.text_input("Deal Name", value="New Deal")
basin = st.sidebar.selectbox("Basin", ["Appalachia", "Permian", "Haynesville", "Oklahoma STACK/SCOOP"])
type_curve_id = st.sidebar.selectbox("Type Curve", ["APPA_113", "APPA_104", "Custom (enter volumes)"])

st.sidebar.header("🏔️ Mineral Interest")

# Tract inputs
num_tracts = st.sidebar.number_input("Number of Tracts", min_value=1, max_value=25, value=1)

tracts = []
for i in range(num_tracts):
    with st.sidebar.expander(f"Tract {i+1}", expanded=(i==0)):
        mineral_acres = st.number_input(f"Mineral Acres (Tract {i+1})", value=18.0, min_value=0.1)
        royalty_rate = st.number_input(f"Royalty Rate (Tract {i+1})", value=0.20, min_value=0.0, max_value=1.0, step=0.01)
        unit_acres = st.number_input(f"Drilling Unit Gross Acres (Tract {i+1})", value=234.2, min_value=1.0)
        unit_name = st.text_input(f"Unit Name (Tract {i+1})", value=f"Unit {i+1}")
        
        tract = Tract(
            mineral_acres=mineral_acres,
            royalty_rate=royalty_rate,
            drilling_unit_gross_acres=unit_acres,
            unit_name=unit_name
        )
        tracts.append(tract)

# Tabs for different input sections
tab_location, tab1, tab2, tab3, tab4, tab5 = st.tabs(["📍 Location", "Production", "Economics", "Costs & Taxes", "Timing", "Results"])

with tab_location:
    st.header("📍 Parcel Location & Type Curve Lookup")
    
    if parcel_lib and tc_lookup:
        # Search options
        search_method = st.radio("Search by:", ("Parcel ID", "Browse Available"))
        
        if search_method == "Parcel ID":
            col1, col2 = st.columns([3, 1])
            with col1:
                parcel_id = st.text_input("Enter Parcel ID (e.g., 53-00887.000)", placeholder="Parcel ID")
            with col2:
                search_btn = st.button("🔍 Lookup", key="lookup_parcel")
            
            if search_btn and parcel_id:
                result = tc_lookup.lookup_by_parcel_id(parcel_id)
                st.session_state.parcel_lookup_result = result
            
        else:  # Browse available
            st.subheader("Browse Utica Parcels")
            
            # Filter by TC area
            all_curves = tc_lookup.list_available_type_curves()
            tc_names = list(set([c['tc_name'] for c in all_curves]))
            tc_names.sort()
            
            selected_tc = st.selectbox("Filter by Type Curve Area", tc_names)
            
            # Get parcels in selected TC
            if selected_tc:
                try:
                    import pandas as pd
                    parcel_df = pd.read_csv("utica_parcel_library.csv")
                    filtered_df = parcel_df[parcel_df['TC_NAME'] == selected_tc].head(20)
                    
                    st.write(f"Sample parcels in {selected_tc} ({len(parcel_df[parcel_df['TC_NAME'] == selected_tc])} total):")
                    parcel_options = filtered_df['PARCEL_ID'].tolist()
                    
                    selected_parcel = st.selectbox("Select a parcel:", parcel_options, key="browse_select")
                    
                    if selected_parcel and st.button("📍 View Details", key="browse_lookup"):
                        result = tc_lookup.lookup_by_parcel_id(selected_parcel)
                        st.session_state.parcel_lookup_result = result
                
                except Exception as e:
                    st.error(f"Error browsing parcels: {e}")
        
        # Display lookup results
        if st.session_state.parcel_lookup_result:
            result = st.session_state.parcel_lookup_result
            
            if result['match']:
                # Save selected type curve to session state
                st.session_state.selected_tc_id = result['tc_id']
                st.session_state.selected_tc_name = result['tc_name']
                
                st.success(f"✅ Found: {result['parcel_id']}")
                
                # Display parcel info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Parcel ID", result['parcel_id'])
                with col2:
                    st.metric("Type Curve", result['tc_id'])
                with col3:
                    st.metric("Latitude", f"{result['lat']:.4f}")
                with col4:
                    st.metric("Longitude", f"{result['lon']:.4f}")
                
                st.info(f"**Type Curve Area:** {result['tc_name']}")
                
                # Interactive map
                st.subheader("📍 Map")
                
                if not HAS_MAP_DEPS:
                    st.error(f"❌ Map dependencies not available: {MAP_ERROR}")
                    st.info("Run this in terminal:\n```\npython3 -m pip install streamlit-folium folium\n```")
                else:
                    try:
                        with st.spinner("Loading map..."):
                            from shapefile_reader import ShapefileReader
                            
                            # Load TC areas shapefile using pyshp (no geopandas needed)
                            tc_reader = ShapefileReader("/Users/steveabney/Downloads/Utica_TC_Areas/Utica_TC_Areas.shp")
                            
                            # Create map centered on parcel
                            map_center = [result['lat'], result['lon']]
                            m = folium.Map(
                                location=map_center,
                                zoom_start=12,
                                tiles="OpenStreetMap"
                            )
                            
                            # Add parcel marker
                            folium.Marker(
                                location=map_center,
                                popup=f"<b>{result['parcel_id']}</b><br>{result['tc_name']}",
                                icon=folium.Icon(color="red", icon="info-sign"),
                                tooltip=result['parcel_id']
                            ).add_to(m)
                            
                            # Add TC area boundary (find matching TC area)
                            for record in tc_reader.get_all_records():
                                if record.attributes.get('TC_NAME') == result['tc_name']:
                                    # Convert to lat/lon for folium (swap x,y to lat,lon)
                                    coords = [(y, x) for x, y in record.points]
                                    folium.PolyLine(
                                        coords,
                                        color="blue",
                                        weight=2,
                                        opacity=0.6,
                                        popup=f"<b>{record.attributes.get('TC_NAME', 'Unknown')}</b>",
                                        tooltip=record.attributes.get('TC_NAME', 'Unknown')
                                    ).add_to(m)
                                    break  # Found the matching TC area
                            
                            # Display map
                            st_folium(m, width=700, height=500)
                    
                    except Exception as e:
                        st.error(f"❌ Map rendering error: {type(e).__name__}: {e}")
                        if st.checkbox("Show detailed error"):
                            import traceback
                            st.code(traceback.format_exc())
                
                # Auto-populate type curve in deal
                st.success("✅ Click the **Production** tab to see the auto-selected type curve!")
            
            else:
                st.error(f"❌ {result['error']}")
    
    else:
        st.error("❌ Parcel library not loaded. Ensure utica_parcel_library.csv exists.")

with tab1:
    st.header("📊 Production Profile")
    
    # Show selected type curve (from Location tab)
    selected_tc = st.session_state.get('selected_tc_name', 'APPA_113')
    st.info(f"**Type Curve Selected:** {selected_tc}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        gas_eur = st.number_input("Gas EUR (MMcf)", value=12060.0, min_value=100.0)
        oil_eur = st.number_input("Oil EUR (MBbls)", value=0.0, min_value=0.0)
        gas_shrink = st.slider("Gas Shrink Factor", min_value=0.0, max_value=1.0, value=0.85, step=0.05)
        ngl_yield = st.number_input("NGL Yield (Bbls/MMcf)", value=60.0, min_value=0.0)
    
    with col2:
        st.info(f"**Total NRI:** {sum(t.nri for t in tracts):.4f} ({sum(t.nri for t in tracts)*100:.2f}%)")
        st.write(f"**Gas EUR:** {gas_eur:,.0f} MMcf")
        st.write(f"**Oil EUR:** {oil_eur:,.0f} MBbls")
    
    # Type Curve Volume Plot
    st.subheader(f"📈 Monthly Type Curve Volumes ({selected_tc})")
    
    # Try to load volumes for the selected type curve
    gas_volumes = None
    tc_name_for_display = selected_tc
    
    if tc_library is not None:
        try:
            # Try to get volumes from the loaded library
            tc_id = st.session_state.get('selected_tc_id', 'APPA_113')
            gas_volumes = tc_library.get_volumes(tc_name_for_display)
            if gas_volumes:
                st.success(f"✅ Loaded type curve: {tc_name_for_display}")
        except Exception as e:
            st.warning(f"Could not load {tc_name_for_display}: {e}. Using APPA_113 fallback.")
            gas_volumes = None
    
    # Fallback to APPA_113 if custom TC not available
    if gas_volumes is None:
        gas_volumes = APPA113_VOLUMES[:-1]  # Remove last summary value (EUR = 600.0)
        tc_name_for_display = "APPA_113 (Fallback)"
    else:
        gas_volumes = gas_volumes[:-1] if isinstance(gas_volumes[-1], (int, float)) and gas_volumes[-1] > 100 else gas_volumes
    
    months = list(range(1, len(gas_volumes) + 1))
    
    if len(gas_volumes) > 0:
        # Create figure with gas/oil subplots
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot gas volumes
        ax.plot(months, gas_volumes, color='#1f77b4', linewidth=2.5, label=f'Gas ({tc_name_for_display})')
        ax.fill_between(months, gas_volumes, alpha=0.2, color='#1f77b4')
        
        # If there's an oil_eur input, show that as a separate line
        if oil_eur > 0:
            # Show oil as flat/declining profile for comparison
            oil_monthly = (oil_eur * 1000) / len(gas_volumes)  # Convert MBbls to Bbls, spread over months
            oil_profile = [oil_monthly * (1 - (i / len(gas_volumes)) * 0.5) for i in range(len(gas_volumes))]
            ax.plot(months, oil_profile, color='#ff7f0e', linewidth=2.5, label=f'Oil ({oil_eur:.0f} MBbls EUR)', linestyle='--')
            ax.fill_between(months, oil_profile, alpha=0.2, color='#ff7f0e')
        
        ax.set_xlabel('Month', fontsize=11, fontweight='bold')
        ax.set_ylabel('Production Volume', fontsize=11, fontweight='bold')
        ax.set_title(f'Type Curve Production Profile - {tc_name_for_display}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=10)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Peak Gas (MMcf/mo)", f"{max(gas_volumes):.1f}")
        with col2:
            st.metric("Avg Gas (MMcf/mo)", f"{sum(gas_volumes)/len(gas_volumes):.1f}")
        with col3:
            st.metric("Total Months", f"{len(gas_volumes)}")
        with col4:
            st.metric("Gas EUR (MMcf)", f"{sum(gas_volumes):.0f}")
    else:
        st.warning("⚠️ Type curve data not available")

with tab2:
    st.header("💰 Commodity Prices & Differentials")
    
    # Fetch CME prices
    st.subheader("📊 CME Market Prices")
    cme_section = st.container()
    with cme_section:
        col1, col2 = st.columns(2)
        with col1:
            fetch_cme = st.checkbox("Fetch live CME prices", value=False)
        with col2:
            if fetch_cme:
                st.info("ℹ️ Fetching from CME... (requires active connection)")
                try:
                    from cme_client import fetch_cme_prices
                    cme_prices = fetch_cme_prices()
                    st.success("✅ CME prices loaded")
                except Exception as e:
                    st.error(f"❌ CME fetch failed: {e}")
                    cme_prices = None
    
    # Price input section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Gas (Henry Hub)")
        gas_price = st.number_input("Price ($/MMBtu)", value=3.68, min_value=0.0, step=0.1)
        gas_diff = st.number_input("Differential ($/MMBtu)", value=-0.06, step=0.01)
        gas_diff_applied = st.checkbox("Apply gas diff", value=False)
        final_gas = (gas_price + gas_diff) if gas_diff_applied else gas_price
        st.metric("Final Gas Price", f"${final_gas:.2f}/MMBtu")
    
    with col2:
        st.subheader("Oil (WTI)")
        oil_price = st.number_input("Price ($/Bbl)", value=61.0, min_value=0.0, step=1.0)
        oil_diff = st.number_input("Differential ($/Bbl)", value=0.0, step=0.5)
        oil_diff_applied = st.checkbox("Apply oil diff", value=False)
        final_oil = (oil_price + oil_diff) if oil_diff_applied else oil_price
        st.metric("Final Oil Price", f"${final_oil:.2f}/Bbl")
    
    with col3:
        st.subheader("NGL")
        ngl_pct = st.slider("NGL (% of WTI)", min_value=0, max_value=100, value=33, step=5)
        ngl_price = final_oil * (ngl_pct / 100)
        st.metric("NGL Price", f"${ngl_price:.2f}/Bbl")
    
    # Cap/Floor controls
    st.subheader("⛓️ Price Caps & Floors")
    cap_floor_col1, cap_floor_col2, cap_floor_col3 = st.columns(3)
    
    with cap_floor_col1:
        st.write("**Gas ($/MMBtu)**")
        cap_gas = st.number_input("Cap", value=6.0, min_value=0.0, step=0.5)
        floor_gas = st.number_input("Floor", value=2.0, min_value=0.0, step=0.5)
    
    with cap_floor_col2:
        st.write("**Oil ($/Bbl)**")
        cap_oil = st.number_input("Cap", value=90.0, min_value=0.0, step=1.0)
        floor_oil = st.number_input("Floor", value=40.0, min_value=0.0, step=1.0)
    
    with cap_floor_col3:
        st.write("**Price Profile**")
        year4_flat = st.checkbox("Hold Year 4 avg flat perpetuity", value=False)
        apply_caps_floors = st.checkbox("Apply caps & floors", value=False)
    
    # Store in session state for use in calculation
    st.session_state.gas_price = final_gas
    st.session_state.oil_price = final_oil
    st.session_state.ngl_price = ngl_price
    st.session_state.cap_gas = cap_gas if apply_caps_floors else None
    st.session_state.floor_gas = floor_gas if apply_caps_floors else None
    st.session_state.cap_oil = cap_oil if apply_caps_floors else None
    st.session_state.floor_oil = floor_oil if apply_caps_floors else None
    st.session_state.year4_flat = year4_flat

with tab3:
    st.header("💸 Costs & Taxes")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("GP&T & Operating")
        gpt_cost = st.number_input("GP&T Cost ($/Mcf)", value=1.79, min_value=0.0, step=0.1)
        is_cost_bearing = st.checkbox("Cost-Bearing Lease (we pay GP&T)", value=False)
        
        st.subheader("Acquisition & Fees")
        acq_cost = st.number_input("Acquisition Cost ($M)", value=0.2375, min_value=0.0, step=0.01)
        ga_fees = st.number_input("G&A Fees ($M)", value=0.0047, min_value=0.0, step=0.001)
    
    with col2:
        st.subheader("Taxes (%)")
        sev_tax_gas = st.number_input("Gas Severance (%)", value=0.7, min_value=0.0, max_value=10.0, step=0.1)
        sev_tax_oil = st.number_input("Oil Severance (%)", value=0.2, min_value=0.0, max_value=10.0, step=0.1)
        ad_val_tax = st.number_input("Ad Valorem (%)", value=1.0, min_value=0.0, max_value=10.0, step=0.1)

with tab4:
    st.header("⏱️ Development Timing")
    col1, col2 = st.columns(2)
    
    with col1:
        undeveloped_delay = st.number_input("Undeveloped Delay (months)", value=36, min_value=0)
        undeveloped_timing = st.number_input("Undeveloped Timing (years)", value=1.0, min_value=0.25, step=0.25)
        spud_to_sales = st.number_input("Spud to Sales (months)", value=3, min_value=1)
    
    with col2:
        analysis_years = st.number_input("Analysis Period (years)", value=50, min_value=10, max_value=100)
        discount_rates = st.multiselect(
            "Discount Rates (%)",
            [0, 5, 7.5, 10, 12.5, 15, 17.5, 20, 25, 30],
            default=[10, 15, 20]
        )

with tab5:
    st.header("📈 Evaluation Results")
    
    # Build and run evaluation
    if st.button("🚀 Calculate IRR & NPV", key="calculate"):
        # Create type curve volumes
        if type_curve_id == "APPA_113":
            volumes = APPA113_VOLUMES[:-1]  # Remove last summary row
        else:
            volumes = []
        
        # Get prices from session state (with caps/floors applied if enabled)
        use_gas_price = st.session_state.get('gas_price', gas_price)
        use_oil_price = st.session_state.get('oil_price', oil_price)
        use_ngl_price = st.session_state.get('ngl_price', ngl_price)
        
        # Apply caps/floors if enabled
        cap_gas = st.session_state.get('cap_gas')
        floor_gas = st.session_state.get('floor_gas')
        cap_oil = st.session_state.get('cap_oil')
        floor_oil = st.session_state.get('floor_oil')
        
        if cap_gas is not None:
            use_gas_price = min(use_gas_price, cap_gas)
        if floor_gas is not None:
            use_gas_price = max(use_gas_price, floor_gas)
        if cap_oil is not None:
            use_oil_price = min(use_oil_price, cap_oil)
        if floor_oil is not None:
            use_oil_price = max(use_oil_price, floor_oil)
        
        use_ngl_price = use_oil_price * (ngl_pct / 100)
        
        # Create deal inputs
        deal = DealInputs(
            deal_name=deal_name,
            basin=basin,
            type_curve_id=type_curve_id,
            tracts=tracts,
            gross_locations=1.0,
            lateral_length_ft=10000,
            participation_wi=0.0,
            participation_nri=0.0,
            oil_eur_mbbl=oil_eur,
            gas_eur_mmcf=gas_eur,
            monthly_gross_gas_volumes=volumes,
            monthly_gross_oil_volumes=[],
            gas_shrink_factor=gas_shrink,
            ngl_yield_bbls_per_mmcf=ngl_yield,
            oil_price_per_bbl=use_oil_price,
            gas_price_per_mcf=use_gas_price,
            ngl_price_per_bbl=use_ngl_price,
            oil_differential_per_bbl=0.0,
            gas_differential_per_mcf=0.0,
            ngl_differential_pct_wti=ngl_pct / 100,
            gas_processing_per_mcf=gpt_cost,
            is_cost_bearing_lease=is_cost_bearing,
            acquisition_cost=acq_cost,
            upfront_ga_fees=ga_fees,
            severance_tax_oil_pct=sev_tax_oil / 100,
            severance_tax_gas_pct=sev_tax_gas / 100,
            ad_valorem_tax_pct=ad_val_tax / 100,
            undeveloped_delay_months=undeveloped_delay,
            undeveloped_timing_years=undeveloped_timing,
            spud_to_sales_months=spud_to_sales,
            analysis_years=analysis_years,
            discount_rates=[r / 100 for r in discount_rates],
            base_date=datetime(2026, 2, 28),
        )
        
        # Run evaluation
        eval = MineralEvaluation(deal)
        eval.evaluate()
        st.session_state.results = (eval, deal)
        
        # Show warning if year4_flat is enabled
        if st.session_state.get('year4_flat'):
            st.info("ℹ️ Year 4 flat-to-perpetuity logic enabled (feature in progress)")
        
        st.success("✅ Evaluation complete!")
    
    # Display results if available
    if st.session_state.results:
        eval, deal = st.session_state.results
        summary = eval.summary()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("IRR", f"{eval.irr:.1%}" if eval.irr else "N/A")
        with col2:
            st.metric("MoM", f"{eval.mom:.2f}x" if eval.mom else "N/A")
        with col3:
            st.metric("Payback", f"{eval.payback_period_months:.0f} mo" if eval.payback_period_months else "N/A")
        with col4:
            st.metric("PV-10%", f"${summary['npv_by_rate'].get(0.10, 0):.1f}M")
        
        # Financial summary
        st.subheader("Financial Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Investment", f"${summary['acquisition_cost'] + summary['total_capex']:.1f}M")
        with col2:
            st.metric("Total Revenue", f"${summary['total_revenue']:.1f}M")
        with col3:
            st.metric("Net Cash Flow", f"${summary['cumulative_cash_flow']:.1f}M")
        
        # NPV chart
        st.subheader("NPV by Discount Rate")
        npv_df = pd.DataFrame({
            'Discount Rate': [f"{r:.0%}" for r in sorted(summary['npv_by_rate'].keys())],
            'NPV ($M)': [summary['npv_by_rate'][r] for r in sorted(summary['npv_by_rate'].keys())]
        })
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(range(len(npv_df)), npv_df['NPV ($M)'], marker='o', linewidth=2)
        ax.set_xticks(range(len(npv_df)))
        ax.set_xticklabels(npv_df['Discount Rate'])
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax.set_xlabel('Discount Rate')
        ax.set_ylabel('NPV ($M)')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        
        # Cash flow detail
        st.subheader("Monthly Cash Flow (First 60 Months)")
        cf_df = pd.DataFrame({
            'Month': [cf.month for cf in eval.cash_flows[:60]],
            'Gas (MMcf)': [cf.net_gas_mcf for cf in eval.cash_flows[:60]],
            'Revenue ($k)': [cf.total_revenue * 1000 for cf in eval.cash_flows[:60]],
            'Taxes ($k)': [cf.total_tax * 1000 for cf in eval.cash_flows[:60]],
            'Net CF ($k)': [cf.net_cash_flow * 1000 for cf in eval.cash_flows[:60]],
        })
        st.dataframe(cf_df, use_container_width=True)
        
        # Export button
        csv = cf_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Cash Flows (CSV)",
            data=csv,
            file_name=f"{deal_name}_cashflows.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("💡 *Phase 2: Interactive Dashboard* | Built with [Streamlit](https://streamlit.io)")
