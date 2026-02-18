"""
Price Deck Parser (Phase 3)
Parses price scenario CSV to extract gas and oil price forecasts (2026-2092).
Returns clean PriceScenario dataclasses for dashboard consumption.
"""

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Global cache for parsed price scenarios
_PRICE_CACHE: Optional[Dict[str, 'PriceScenario']] = None


@dataclass
class PriceScenario:
    """Price scenario with monthly gas and oil prices (2026-2092)."""
    name: str  # e.g., "Gas_3.0_Oil_60"
    gas_price_base: float  # Scenario gas price ($/MMBtu)
    oil_price_base: float  # Scenario oil price ($/bbl)
    monthly_dates: List[str]  # YYYY-MM-DD format
    monthly_gas_prices: List[float]  # $/MMBtu
    monthly_oil_prices: List[float]  # $/bbl
    
    def __repr__(self) -> str:
        return f"PriceScenario({self.name}, Gas=${self.gas_price_base:.1f}/MMBtu, Oil=${self.oil_price_base:.0f}/bbl, {len(self.monthly_dates)} months)"


def parse_price_deck(csv_path: str) -> Dict[str, PriceScenario]:
    """
    Parse price deck CSV and return dict of scenario names to PriceScenario objects.
    
    CSV Structure:
    - Row 4: Scenario price labels
      - Cols 6,7,8,9: Gas price scenarios (3.0, 3.25, 3.5, 4.0 $/MMBtu)
      - Cols 14,15,16,17: Oil price scenarios (60.0, 65.0, 70.0, 80.0 $/bbl)
    - Row 6+: Monthly data
      - Col 2: Year
      - Col 3: Date (YYYY-MM-DD format)
      - Col 5: NYMEX reference price
      - Cols 6-11: Gas price scenarios (including alternates)
      - Cols 13-19: Oil price scenarios (including alternates)
    - 798 rows total → 792 months of data (Feb 2026 - Jan 2092)
    
    Args:
        csv_path: Path to the price deck CSV file
        
    Returns:
        Dict mapping scenario names to PriceScenario objects
    """
    global _PRICE_CACHE
    
    # Return cached data if available
    if _PRICE_CACHE is not None:
        logger.info(f"Returning cached price scenarios with {len(_PRICE_CACHE)} scenarios")
        return _PRICE_CACHE
    
    logger.info(f"Parsing price deck from {csv_path}")
    scenarios = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        logger.debug(f"Read {len(rows)} rows from CSV")
        
        # Row 4 has the scenario price labels
        scenario_header_row = rows[4] if len(rows) > 4 else []
        
        # Identify gas price columns (3.0, 3.25, 3.5, 4.0, 5.0, 6.0)
        gas_cols = {}  # {col_idx: price}
        oil_cols = {}  # {col_idx: price}
        
        for col_idx, cell in enumerate(scenario_header_row):
            cell_str = (cell or "").strip()
            try:
                price = float(cell_str)
                if 2.0 <= price <= 6.0:
                    gas_cols[col_idx] = price
                elif 50.0 <= price <= 90.0:
                    oil_cols[col_idx] = price
            except ValueError:
                pass
        
        if not gas_cols or not oil_cols:
            logger.error(f"Could not find gas/oil price columns. Found {len(gas_cols)} gas, {len(oil_cols)} oil")
            return scenarios
        
        gas_prices = sorted(set(gas_cols.values()))
        oil_prices = sorted(set(oil_cols.values()))
        logger.info(f"Found {len(gas_cols)} gas columns ({gas_prices}) and {len(oil_cols)} oil columns ({oil_prices})")
        
        # Extract data rows (start at row 6)
        data_start_idx = 6
        dates = []
        gas_data_by_col = {col: [] for col in gas_cols}
        oil_data_by_col = {col: [] for col in oil_cols}
        
        for i in range(data_start_idx, len(rows)):
            row = rows[i]
            
            # Get date from column 3
            if len(row) <= 3:
                break
            
            date_str = (row[3] if len(row) > 3 else "").strip()
            if not date_str or len(date_str) < 10:
                break
            
            try:
                # Parse and validate date
                dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
                dates.append(dt.strftime('%Y-%m-%d'))
            except ValueError:
                break
            
            # Extract prices
            for col_idx in gas_cols:
                try:
                    price = float(row[col_idx]) if col_idx < len(row) and row[col_idx].strip() else 0.0
                    gas_data_by_col[col_idx].append(price)
                except (ValueError, IndexError):
                    gas_data_by_col[col_idx].append(0.0)
            
            for col_idx in oil_cols:
                try:
                    price = float(row[col_idx]) if col_idx < len(row) and row[col_idx].strip() else 0.0
                    oil_data_by_col[col_idx].append(price)
                except (ValueError, IndexError):
                    oil_data_by_col[col_idx].append(0.0)
        
        logger.info(f"Extracted {len(dates)} months of price data")
        
        # Create scenario combinations
        for gas_col, gas_price in sorted(gas_cols.items()):
            for oil_col, oil_price in sorted(oil_cols.items()):
                scenario_name = f"Gas_{gas_price:.1f}_Oil_{oil_price:.0f}"
                
                # Get monthly prices
                gas_prices_list = gas_data_by_col.get(gas_col, [])
                oil_prices_list = oil_data_by_col.get(oil_col, [])
                
                # Trim to same length as dates
                gas_prices_list = gas_prices_list[:len(dates)]
                oil_prices_list = oil_prices_list[:len(dates)]
                
                if gas_prices_list and oil_prices_list and len(gas_prices_list) == len(dates):
                    scenarios[scenario_name] = PriceScenario(
                        name=scenario_name,
                        gas_price_base=gas_price,
                        oil_price_base=oil_price,
                        monthly_dates=dates,
                        monthly_gas_prices=gas_prices_list,
                        monthly_oil_prices=oil_prices_list
                    )
        
        # Cache the results
        _PRICE_CACHE = scenarios
        logger.info(f"Successfully parsed {len(scenarios)} price scenarios with caching enabled")
        
    except Exception as e:
        logger.error(f"Error parsing price deck: {e}")
        raise
    
    return scenarios


def get_scenario(scenario_name: str, csv_path: Optional[str] = None) -> Optional[PriceScenario]:
    """
    Get a specific price scenario by name.
    
    Args:
        scenario_name: Name of the scenario (e.g., "Gas_3.0_Oil_60")
        csv_path: Path to CSV (required on first call)
        
    Returns:
        PriceScenario object or None if not found
    """
    global _PRICE_CACHE
    
    if _PRICE_CACHE is None:
        if csv_path is None:
            raise ValueError("csv_path required on first call")
        parse_price_deck(csv_path)
    
    return _PRICE_CACHE.get(scenario_name)


def list_scenarios(csv_path: Optional[str] = None) -> List[str]:
    """List all available scenario names."""
    if _PRICE_CACHE is None and csv_path:
        parse_price_deck(csv_path)
    return sorted(list(_PRICE_CACHE.keys())) if _PRICE_CACHE else []


def get_gas_prices(csv_path: Optional[str] = None) -> List[float]:
    """Get unique gas prices across all scenarios."""
    if _PRICE_CACHE is None and csv_path:
        parse_price_deck(csv_path)
    if _PRICE_CACHE:
        return sorted(list(set([s.gas_price_base for s in _PRICE_CACHE.values()])))
    return []


def get_oil_prices(csv_path: Optional[str] = None) -> List[float]:
    """Get unique oil prices across all scenarios."""
    if _PRICE_CACHE is None and csv_path:
        parse_price_deck(csv_path)
    if _PRICE_CACHE:
        return sorted(list(set([s.oil_price_base for s in _PRICE_CACHE.values()])))
    return []


def clear_cache():
    """Clear the price scenario cache."""
    global _PRICE_CACHE
    _PRICE_CACHE = None
    logger.debug("Price scenario cache cleared")


if __name__ == "__main__":
    # Test parsing
    logging.basicConfig(level=logging.INFO)
    
    test_csv = "/Users/steveabney/.openclaw/media/inbound/file_12---9197eca9-585e-46c3-9104-e0a12fe50ade.csv"
    
    scenarios = parse_price_deck(test_csv)
    
    print(f"\n✓ Parsed {len(scenarios)} price scenarios")
    print(f"\nGas prices: {get_gas_prices()}")
    print(f"Oil prices: {get_oil_prices()}")
    
    print(f"\nSample scenarios:")
    for name in sorted(scenarios.keys())[:3]:
        scenario = scenarios[name]
        print(f"\n  {scenario.name}")
        print(f"    Base: Gas=${scenario.gas_price_base:.1f}/MMBtu, Oil=${scenario.oil_price_base:.0f}/bbl")
        print(f"    Months: {len(scenario.monthly_dates)}")
        if scenario.monthly_dates:
            print(f"    Date range: {scenario.monthly_dates[0]} to {scenario.monthly_dates[-1]}")
            print(f"    First month prices: Gas=${scenario.monthly_gas_prices[0]:.2f}, Oil=${scenario.monthly_oil_prices[0]:.2f}")
