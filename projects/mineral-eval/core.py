"""
Mineral & Royalty Interest Evaluation Engine
Core financial modeling for oil & gas deals
Standard library only (no numpy/scipy dependencies)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math


@dataclass
class Tract:
    """A single tract of mineral acres in a drilling unit"""
    mineral_acres: float
    royalty_rate: float  # e.g., 0.20 for 20%
    drilling_unit_gross_acres: float
    unit_name: Optional[str] = None  # e.g., "Stephens County Unit 1"
    
    @property
    def nri(self) -> float:
        """Calculate NRI for this tract: (Acres × Royalty %) / Unit Size"""
        return (self.mineral_acres * self.royalty_rate) / self.drilling_unit_gross_acres


@dataclass
class DealInputs:
    """All inputs required for a deal evaluation"""
    
    # Metadata
    deal_name: str
    basin: str  # Appalachia, Permian, Haynesville, Oklahoma STACK/SCOOP
    type_curve_id: str
    
    # Mineral Interest Tracts (new structure)
    tracts: List[Tract] = field(default_factory=list)
    
    # Well & Land
    gross_locations: float = 1.0
    lateral_length_ft: float = 10000  # feet
    
    # Participation (optional additional interests beyond tract NRI)
    participation_wi: float = 0.0  # optional additional WI %
    participation_nri: float = 0.0  # optional additional NRI %
    
    # Production (EUR per well)
    oil_eur_mbbl: float = 0.0  # million barrels
    gas_eur_mmcf: float = 12060.0  # million cubic feet
    
    # Production Profile Options
    # Option 1: Use monthly volumes from type curve (preferred)
    monthly_gross_gas_volumes: List[float] = field(default_factory=list)  # MMcf per month
    monthly_gross_oil_volumes: List[float] = field(default_factory=list)  # MBbls per month
    
    # Option 2: Use initial rate + decline curve (if monthly_volumes not provided)
    initial_oil_rate_bbl_per_day: float = 0.0
    initial_gas_rate_mcf_per_day: float = 0.0  # Set to ~5000 for reasonable Appalachia rate
    
    decline_curve_type: str = "exponential"  # or "hyperbolic"
    initial_decline_rate: float = 0.5  # 50% first year decline
    hyperbolic_exponent: float = 0.5  # for hyperbolic decline
    terminal_decline_rate: float = 0.05  # 5% decline at terminal
    
    # Commercial Assumptions
    gas_shrink_factor: float = 0.85  # 85% shrink (15% lost to processing)
    ngl_yield_bbls_per_mmcf: float = 60.0  # barrels of NGL per MMcf
    
    # Commodity Prices
    # Note: When using type curves with monthly volumes in MMcf:
    #   - gas_price_per_mcf is interpreted as $/MMcf (not $/Mcf)
    #   - oil_price_per_bbl is $/Bbl (volumes in MBbls)
    oil_price_per_bbl: float = 61.0  # $/Bbl
    gas_price_per_mcf: float = 3.68  # $/MMcf (when using type curves)
    ngl_price_per_bbl: float = 0.0  # auto-calc: 33% of WTI
    
    # Price Differentials (same units as prices)
    oil_differential_per_bbl: float = 0.0  # $/Bbl
    gas_differential_per_mcf: float = -0.06  # $/MMcf (when using type curves)
    ngl_differential_pct_wti: float = 0.33  # 33% of WTI
    
    # Btu Adjustment
    btu_adjustment: float = 1.0
    
    # Operating Costs (per well)
    fixed_opex_per_month: float = 2500  # $/month
    variable_opex_oil_per_bbl: float = 0.0
    variable_opex_gas_per_mcf: float = 0.15
    variable_opex_water_per_bblw: float = 0.0
    
    # Gas Processing & Transportation
    gas_processing_per_mcf: float = 1.79  # GP&T cost
    is_cost_bearing_lease: bool = False  # if True, operator bears GP&T
    
    # Capex & Timing
    drilling_completion_capex: float = 7000  # $7k per foot of lateral
    spud_to_sales_months: int = 3
    development_delay_months: int = 0  # Delay from acquisition to first production (e.g., 39 for May 2029 start)
    
    # Development Timing
    undeveloped_delay_months: int = 36
    undeveloped_timing_years: int = 1
    duct_delay_months: int = 1
    permit_delay_months: int = 12
    development_pace_years: int = 4
    
    # Asset Type
    asset_type: str = "PUD"  # PUD, DUC, PDP, Permit
    on_off: bool = True
    
    # Production Risk
    production_risk: float = 1.0  # 100%
    
    # Cost Bearing
    # If True: We bear all capex and opex (single well basis)
    # If False: Operator bears costs, we get net revenue only (lease/royalty basis)
    cost_bearing: bool = False
    
    # Acquisition Cost
    # One-time upfront cost to acquire the interest (paid at base_date)
    acquisition_cost: float = 0.0
    
    # G&A and Other Fees
    # One-time upfront G&A/admin fees (paid at base_date)
    upfront_ga_fees: float = 0.0
    
    # Annual G&A (per year, deducted from cash flows)
    annual_ga: float = 0.0
    
    # Taxes
    severance_tax_oil_pct: float = 0.002  # 0.2%
    severance_tax_gas_pct: float = 0.007  # 0.7%
    severance_tax_ngl_pct: float = 0.0
    ad_valorem_tax_pct: float = 0.01  # 1.0%
    
    # Analysis Parameters
    analysis_years: int = 50
    discount_rates: List[float] = field(default_factory=lambda: [0.0, 0.05, 0.075, 0.10, 0.125, 0.15, 0.175, 0.20, 0.25, 0.30])
    base_date: datetime = field(default_factory=datetime.now)
    
    @property
    def total_nri(self) -> float:
        """Calculate total NRI across all tracts plus participation"""
        tract_nri = sum(tract.nri for tract in self.tracts)
        return tract_nri + self.participation_nri
    
    def __post_init__(self):
        """Calculate derived fields"""
        if self.ngl_price_per_bbl == 0.0:
            self.ngl_price_per_bbl = self.oil_price_per_bbl * self.ngl_differential_pct_wti


@dataclass
class AnnualCashFlow:
    """Cash flow for a single year"""
    year: int
    month: int
    gross_oil_bbl: float = 0.0
    gross_gas_mcf: float = 0.0
    gross_ngl_bbl: float = 0.0
    
    net_oil_bbl: float = 0.0
    net_gas_mcf: float = 0.0
    net_ngl_bbl: float = 0.0
    
    oil_revenue: float = 0.0
    gas_revenue: float = 0.0
    ngl_revenue: float = 0.0
    total_revenue: float = 0.0
    
    fixed_opex: float = 0.0
    variable_opex: float = 0.0
    total_opex: float = 0.0
    
    severance_tax: float = 0.0
    ad_valorem_tax: float = 0.0
    total_tax: float = 0.0
    
    gpt_cost: float = 0.0  # Gas processing & transportation
    
    capex: float = 0.0
    acquisition_cost: float = 0.0  # One-time upfront acquisition cost
    ga_fees: float = 0.0  # One-time upfront G&A fees
    annual_ga: float = 0.0  # Monthly portion of annual G&A
    
    net_cash_flow: float = 0.0


class ProductionDecline:
    """Production decline model"""
    
    @staticmethod
    def exponential_decline(q0, di, t):
        """Exponential decline: q(t) = q0 * exp(-di * t)"""
        return q0 * math.exp(-di * t)
    
    @staticmethod
    def hyperbolic_decline(q0, di, b, t):
        """Hyperbolic decline: q(t) = q0 * (1 + b*di*t)^(-1/b)"""
        exponent = -1 / b if b != 0 else -1
        return q0 * math.pow(1 + b * di * t, exponent)
    
    @staticmethod
    def harmonic_decline(q0, di, t):
        """Harmonic decline: q(t) = q0 / (1 + di*t)"""
        return q0 / (1 + di * t)
    
    @staticmethod
    def eur_to_initial_rate(eur_total, di, decline_type="exponential", well_life_years=50, b=0.5):
        """
        Convert EUR (cumulative) to initial daily production rate.
        Uses analytical formula for exponential decline, iterative for others.
        
        EUR = integral of q(t) dt from 0 to T
        For exponential: Q(T) = q0/di * (1 - exp(-di*T))
        So: q0 = EUR * di / (1 - exp(-di*T))
        """
        well_life = well_life_years  # years
        
        if decline_type == "exponential":
            # Analytical solution
            if di > 0:
                factor = 1 - math.exp(-di * well_life)
                if factor > 0:
                    q0 = eur_total * di / factor
                else:
                    q0 = eur_total / well_life / 365  # Fallback
            else:
                q0 = eur_total / well_life / 365
        else:
            # Iterative approach for hyperbolic/harmonic
            q0_guess = eur_total / (well_life * 365)
            
            for iteration in range(20):
                cumulative = 0.0
                for day in range(well_life * 365):
                    years = day / 365.0
                    if decline_type == "hyperbolic":
                        rate = ProductionDecline.hyperbolic_decline(q0_guess, di, b, years)
                    else:
                        rate = ProductionDecline.harmonic_decline(q0_guess, di, years)
                    cumulative += rate
                
                # Adjust q0 to match EUR
                if cumulative > 0:
                    ratio = eur_total / cumulative
                    q0_guess = q0_guess * ratio
                    # Stop if converged
                    if abs(ratio - 1.0) < 0.001:
                        break
            
            q0 = q0_guess
        
        return q0


class MineralEvaluation:
    """Core evaluation engine"""
    
    def __init__(self, inputs: DealInputs):
        self.inputs = inputs
        self.cash_flows: List[AnnualCashFlow] = []
        self.npv_by_rate: Dict[float, float] = {}
        self.irr: Optional[float] = None
        self.mom: Optional[float] = None
        self.payback_period_months: Optional[float] = None
        
    def evaluate(self):
        """Run full evaluation"""
        self.generate_cash_flows()
        self.calculate_npv_at_rates()
        self.calculate_irr()
        self.calculate_mom()
        self.calculate_payback()
        
    def generate_cash_flows(self):
        """Generate monthly/annual cash flows over analysis period"""
        self.cash_flows = []
        
        # Calculate total capex
        total_capex = self.inputs.drilling_completion_capex * self.inputs.lateral_length_ft / 1000
        cumulative_capex = 0.0
        
        for month in range(self.inputs.analysis_years * 12):
            current_date = self.inputs.base_date + timedelta(days=month * 30)
            
            # Acquisition cost and G&A fees at month 0
            if month == 0:
                acq_cost = self.inputs.acquisition_cost
                ga_fees = self.inputs.upfront_ga_fees
            else:
                acq_cost = 0.0
                ga_fees = 0.0
            
            # Annual G&A costs (amortized monthly)
            monthly_ga = self.inputs.annual_ga / 12.0
            
            # Capex period: spread over spud_to_sales_months starting at undeveloped_delay
            capex_start_month = self.inputs.undeveloped_delay_months
            capex_end_month = capex_start_month + self.inputs.spud_to_sales_months
            
            if total_capex > 0 and capex_start_month <= month < capex_end_month:
                if cumulative_capex < total_capex:
                    monthly_capex = min(total_capex / self.inputs.spud_to_sales_months, 
                                       total_capex - cumulative_capex)
                    cumulative_capex += monthly_capex
                else:
                    monthly_capex = 0.0
            else:
                monthly_capex = 0.0
            
            # Total upfront costs
            total_upfront_cost = acq_cost + (monthly_capex if self.inputs.cost_bearing else 0.0)
            
            # Calculate months since start of drilling (for ramp calculation)
            # Ramp starts at undeveloped_delay_months (month when first well spuds)
            months_since_undeveloped = month - self.inputs.undeveloped_delay_months
            
            if months_since_undeveloped < 0:
                # Before any drilling
                gross_gas_mcf = 0.0
                gross_oil_bbl = 0.0
            elif self.inputs.monthly_gross_gas_volumes:
                # Use type curve monthly volumes with production ramp
                ramp_duration_months = int(self.inputs.undeveloped_timing_years * 12)
                
                if months_since_undeveloped < ramp_duration_months:
                    # During ramp (months 0-11 relative to spud)
                    # Production = (month_index / ramp_duration) × peak_production
                    ramp_factor = (months_since_undeveloped + 1) / ramp_duration_months
                    
                    if len(self.inputs.monthly_gross_gas_volumes) > 0:
                        peak_gas = self.inputs.monthly_gross_gas_volumes[0]
                        gross_gas_mcf = peak_gas * ramp_factor
                    else:
                        gross_gas_mcf = 0.0
                    
                    gross_oil_bbl = 0.0
                else:
                    # After ramp: use type curve directly
                    # tc_month_index: which month of type curve to use
                    tc_month_index = int(months_since_undeveloped - ramp_duration_months)
                    
                    if tc_month_index < len(self.inputs.monthly_gross_gas_volumes):
                        gross_gas_mcf = self.inputs.monthly_gross_gas_volumes[tc_month_index]
                    else:
                        gross_gas_mcf = 0.0
                    
                    # Oil volumes
                    if self.inputs.monthly_gross_oil_volumes and tc_month_index < len(self.inputs.monthly_gross_oil_volumes):
                        gross_oil_bbl = self.inputs.monthly_gross_oil_volumes[tc_month_index]
                    else:
                        gross_oil_bbl = 0.0
            else:
                # No type curve provided, use decline curve model (not currently implemented for this case)
                gross_gas_mcf = 0.0
                gross_oil_bbl = 0.0
            
            # Apply production risk
            gross_gas_mcf *= self.inputs.production_risk
            gross_oil_bbl *= self.inputs.production_risk
            
            # NGL from shrunk gas
            shrunk_gas_mcf = gross_gas_mcf * self.inputs.gas_shrink_factor
            gross_ngl_bbl = shrunk_gas_mcf * self.inputs.ngl_yield_bbls_per_mmcf / 1_000_000
            
            # Net to interest (total NRI includes tracts + participation)
            net_gas_mcf = gross_gas_mcf * self.inputs.total_nri
            net_oil_bbl = gross_oil_bbl * self.inputs.total_nri
            net_ngl_bbl = gross_ngl_bbl * self.inputs.total_nri
            
            # Revenues
            gas_revenue = net_gas_mcf * (self.inputs.gas_price_per_mcf + self.inputs.gas_differential_per_mcf) * self.inputs.btu_adjustment
            oil_revenue = net_oil_bbl * (self.inputs.oil_price_per_bbl + self.inputs.oil_differential_per_bbl)
            ngl_revenue = net_ngl_bbl * self.inputs.ngl_price_per_bbl
            total_revenue = gas_revenue + oil_revenue + ngl_revenue
            
            # Operating Costs (if cost bearing)
            if self.inputs.cost_bearing:
                fixed_opex = self.inputs.fixed_opex_per_month if months_on_production > 0 else 0.0
                variable_opex = (
                    net_oil_bbl * self.inputs.variable_opex_oil_per_bbl +
                    net_gas_mcf * self.inputs.variable_opex_gas_per_mcf
                )
                total_opex = fixed_opex + variable_opex
            else:
                # Lease/royalty basis: operator bears costs
                fixed_opex = 0.0
                variable_opex = 0.0
                total_opex = 0.0
            
            # Gas Processing & Transportation
            # On lease basis: we may pay our share of GP&T depending on the lease terms
            # is_cost_bearing_lease=True: we pay GP&T (cost-bearing lease)
            # is_cost_bearing_lease=False: operator bears GP&T (cost-free lease)
            if self.inputs.is_cost_bearing_lease:
                # Cost-bearing lease: we pay our share of GP&T
                gpt_cost = shrunk_gas_mcf * self.inputs.gas_processing_per_mcf
            else:
                # Cost-free lease or working interest: operator bears/deducts GP&T
                gpt_cost = 0.0
            
            # Taxes (always apply, regardless of cost_bearing status)
            # Calculated on our net revenue share
            severance_tax = (
                net_oil_bbl * self.inputs.oil_price_per_bbl * self.inputs.severance_tax_oil_pct +
                net_gas_mcf * self.inputs.gas_price_per_mcf * self.inputs.severance_tax_gas_pct +
                net_ngl_bbl * self.inputs.ngl_price_per_bbl * self.inputs.severance_tax_ngl_pct
            )
            ad_valorem_tax = total_revenue * self.inputs.ad_valorem_tax_pct
            
            total_tax = severance_tax + ad_valorem_tax
            
            # Capex (if cost bearing)
            cf_capex = monthly_capex if self.inputs.cost_bearing else 0.0
            
            # Net cash flow = revenue - costs - acquisition - GA
            net_cash_flow = total_revenue - total_opex - gpt_cost - total_tax - cf_capex - acq_cost - ga_fees - monthly_ga
            
            cf = AnnualCashFlow(
                year=month // 12,
                month=month,
                gross_oil_bbl=gross_oil_bbl,
                gross_gas_mcf=gross_gas_mcf,
                gross_ngl_bbl=gross_ngl_bbl,
                net_oil_bbl=net_oil_bbl,
                net_gas_mcf=net_gas_mcf,
                net_ngl_bbl=net_ngl_bbl,
                oil_revenue=oil_revenue,
                gas_revenue=gas_revenue,
                ngl_revenue=ngl_revenue,
                total_revenue=total_revenue,
                fixed_opex=fixed_opex,
                variable_opex=variable_opex,
                total_opex=total_opex,
                severance_tax=severance_tax,
                ad_valorem_tax=ad_valorem_tax,
                total_tax=total_tax,
                gpt_cost=gpt_cost,
                capex=cf_capex,
                acquisition_cost=acq_cost,
                ga_fees=ga_fees,
                annual_ga=monthly_ga,
                net_cash_flow=net_cash_flow,
            )
            self.cash_flows.append(cf)
    
    def calculate_npv_at_rates(self):
        """Calculate NPV at each discount rate"""
        self.npv_by_rate = {}
        
        for rate in self.inputs.discount_rates:
            npv = 0.0
            for cf in self.cash_flows:
                months_discounted = cf.month
                discount_factor = (1 + rate) ** (-months_discounted / 12)
                npv += cf.net_cash_flow * discount_factor
            
            self.npv_by_rate[rate] = npv
    
    def calculate_irr(self):
        """Calculate IRR using bisection method"""
        def npv_func(rate):
            npv = 0.0
            for cf in self.cash_flows:
                months_discounted = cf.month
                discount_factor = (1 + rate) ** (-months_discounted / 12)
                npv += cf.net_cash_flow * discount_factor
            return npv
        
        try:
            # Find NPV at bounds
            low = 0.0
            high = 10.0  # Expand search to 1000%
            
            npv_low = npv_func(low)
            npv_high = npv_func(high)
            
            # Check if solution exists in range
            if npv_low * npv_high > 0:
                # Both same sign - no IRR in this range
                # Check if both positive (very high returns)
                if npv_low > 0:
                    # NPV is always positive, IRR is very high
                    # Try expanding range
                    for test_high in [50.0, 100.0, 500.0, 1000.0]:
                        if npv_func(test_high) < 0:
                            high = test_high
                            break
                    else:
                        # Still can't find crossing point
                        self.irr = None
                        return
                else:
                    self.irr = None
                    return
            
            # Bisection method
            tolerance = 1e-6
            for iteration in range(200):
                mid = (low + high) / 2
                npv_mid = npv_func(mid)
                
                if abs(npv_mid) < tolerance:
                    break
                
                if npv_mid < 0:
                    low = mid
                else:
                    high = mid
            
            self.irr = (low + high) / 2
        except:
            self.irr = None
    
    def calculate_mom(self):
        """Calculate Multiple on Money (MoM)"""
        total_inflow = sum(cf.net_cash_flow for cf in self.cash_flows if cf.net_cash_flow > 0)
        total_outflow = abs(sum(cf.net_cash_flow for cf in self.cash_flows if cf.net_cash_flow < 0))
        
        if total_outflow > 0:
            self.mom = total_inflow / total_outflow
        else:
            self.mom = None
    
    def calculate_payback(self):
        """Calculate payback period in months"""
        cumulative = 0.0
        for cf in self.cash_flows:
            cumulative += cf.net_cash_flow
            if cumulative >= 0:
                self.payback_period_months = cf.month
                return
        self.payback_period_months = None
    
    def summary(self) -> Dict:
        """Return summary results"""
        return {
            "deal_name": self.inputs.deal_name,
            "irr": self.irr,
            "mom": self.mom,
            "payback_months": self.payback_period_months,
            "npv_by_rate": self.npv_by_rate,
            "acquisition_cost": self.inputs.acquisition_cost,
            "total_capex": sum(cf.capex for cf in self.cash_flows),
            "total_revenue": sum(cf.total_revenue for cf in self.cash_flows),
            "total_opex": sum(cf.total_opex for cf in self.cash_flows),
            "total_tax": sum(cf.total_tax for cf in self.cash_flows),
            "cumulative_cash_flow": sum(cf.net_cash_flow for cf in self.cash_flows),
            "total_investment": self.inputs.acquisition_cost + sum(cf.capex for cf in self.cash_flows),
        }
