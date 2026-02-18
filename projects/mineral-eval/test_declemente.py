"""
Test the Declemente well example
Validation against Model Output.csv and Model Main Input.csv
"""

from core import DealInputs, Tract, MineralEvaluation
from appa113_volumes import APPA113_VOLUMES
from datetime import datetime

# Use all 600 months from type curve (last row was summary, remove it)
appa113_monthly_volumes = APPA113_VOLUMES[:-1]

# Declemente Unit 1 - dry gas well
# 18 mineral acres × 20% royalty ÷ 234.2 unit gross acres = 1.537% NRI
declemente = DealInputs(
    deal_name="Declemente Unit 1",
    basin="Appalachia",
    type_curve_id="APPA_113",
    
    # Mineral Interest (tracts)
    tracts=[
        Tract(
            mineral_acres=18.0,
            royalty_rate=0.20,
            drilling_unit_gross_acres=234.2,
            unit_name="Stephens County Unit 1"
        )
    ],
    
    # Well & Land
    gross_locations=1.0,
    lateral_length_ft=10000,
    
    # Participation (none in this deal)
    participation_wi=0.0,
    participation_nri=0.0,
    
    # Production
    oil_eur_mbbl=0.0,  # dry gas
    gas_eur_mmcf=12060.0,
    
    # Type curve monthly volumes (in MMcf, gross production)
    monthly_gross_gas_volumes=appa113_monthly_volumes,
    monthly_gross_oil_volumes=[],  # No oil production
    
    # Commercial
    gas_shrink_factor=0.85,
    ngl_yield_bbls_per_mmcf=60.0,
    oil_price_per_bbl=61.0,
    gas_price_per_mcf=3.68,
    ngl_differential_pct_wti=0.33,
    gas_differential_per_mcf=-0.06,
    
    # Opex
    fixed_opex_per_month=2500,
    variable_opex_gas_per_mcf=0.15,
    gas_processing_per_mcf=1.79,
    is_cost_bearing_lease=False,
    
    # Capex & Timing
    drilling_completion_capex=7000,  # $/ft lateral
    spud_to_sales_months=3,  # 3 months from TIL (Turn In Line) to revenue receipt
    
    # Development timing (from Development Assumptions in FIN tab)
    undeveloped_delay_months=36,  # Wait 36 months before drilling starts
    undeveloped_timing_years=1.0,  # Drill 1 well over 1 year (12 months)
    duct_delay_months=1,
    permit_delay_months=12,
    development_pace_years=4,
    
    # Taxes
    severance_tax_oil_pct=0.002,
    severance_tax_gas_pct=0.007,
    ad_valorem_tax_pct=0.01,
    
    # Acquisition Cost and Fees (in millions)
    acquisition_cost=0.2375,  # $237.5k upfront to acquire the 1.5% NRI interest
    upfront_ga_fees=0.0047,  # $4.7k upfront G&A/admin fees
    
    # Base date
    base_date=datetime(2026, 2, 28),
)

# Run evaluation
print("=" * 80)
print(f"Evaluating: {declemente.deal_name}")
print(f"Tracts: {[(t.mineral_acres, t.royalty_rate, t.unit_name) for t in declemente.tracts]}")
print(f"Total NRI: {declemente.total_nri:.4f} ({declemente.total_nri*100:.2f}%)")
print("=" * 80)

eval = MineralEvaluation(declemente)
eval.evaluate()

# Debug NPV at various rates
print("\nNPV at different rates (for debugging):")
for rate in [0.0, 0.1, 0.163, 0.2, 0.3]:
    npv = 0.0
    for cf in eval.cash_flows:
        discount_factor = (1 + rate) ** (-cf.month / 12)
        npv += cf.net_cash_flow * discount_factor
    rate_label = f"IRR" if rate == 0.163 else f"{rate:.1%}"
    print(f"  NPV @ {rate_label}: ${npv:,.0f}")

# Debug: Show production and cash flows for first 10 months
print("\nFirst 10 months of cash flows (starting at month 40 = May 2029):")
print(f"{'Month':<6} {'Gas (MMcf)':<15} {'Revenue':<15} {'Opex':<15} {'Net CF':<15}")
print("-" * 70)
for cf in eval.cash_flows[40:50]:
    if cf.net_gas_mcf > 0 or cf.net_cash_flow != 0:
        print(f"{cf.month:<6} {cf.net_gas_mcf:>13,.0f}  ${cf.total_revenue:>12,.0f}  ${cf.total_opex:>12,.0f}  ${cf.net_cash_flow:>12,.0f}")

# Print results
summary = eval.summary()
print("\n" + "=" * 80)
print("EVALUATION RESULTS:")
print("=" * 80)
if summary['irr']:
    print(f"IRR: {summary['irr']:.2%}")
else:
    print(f"IRR: N/A")
if summary['mom']:
    print(f"MoM: {summary['mom']:.2f}x")
else:
    print("MoM: N/A")
if summary['payback_months']:
    print(f"Payback: {summary['payback_months']:.0f} months ({summary['payback_months']/12:.1f} years)")
else:
    print("Payback: N/A")

print(f"\nTotal Investment: ${summary['acquisition_cost'] + summary['total_capex']:,.0f}")
print(f"  Acquisition Cost: ${summary['acquisition_cost']:,.0f}")
print(f"  Development Capex: ${summary['total_capex']:,.0f}")
print(f"Total Revenue (undiscounted): ${summary['total_revenue']:,.0f}")
print(f"Total Opex (undiscounted): ${summary['total_opex']:,.0f}")
print(f"Total Tax (undiscounted): ${summary['total_tax']:,.0f}")
print(f"Cumulative Cash Flow: ${summary['cumulative_cash_flow']:,.0f}")

print("\n" + "=" * 80)
print("NPV at Different Discount Rates:")
print("=" * 80)
for rate in sorted(summary['npv_by_rate'].keys()):
    npv = summary['npv_by_rate'][rate]
    rate_pct = f"{rate:.1%}".rjust(6)
    npv_str = f"${npv:,.0f}".rjust(15)
    print(f"PV-{rate_pct}: {npv_str}")

print("\n" + "=" * 80)
print("Expected from Model Output.csv:")
print("=" * 80)
print(f"Single Well IRR: 52.9%")
print(f"Single Well MoM: 2.32x")
print(f"Single Well PV-10: $5.0M")
print(f"Lease IRR (Blowdown): 16.3% / 2.64x")
print(f"Lease IRR (Exit): 17.8% / 2.16x")
