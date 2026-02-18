"""
Type Curve Library Parser (Phase 3) - Updated
Parses type curve library CSV to extract GAS curve definitions, EUR, lateral length, and monthly volumes.
Properly handles separate oil and gas sections in the CSV.

Structure:
- Columns 6-31: Oil type curves (SKIP)
- Columns 32+: Gas type curves (PARSE)
- Row 2: EUR values
- Row 4: Lateral length values
- Row 11: Bench designations
- Row 14+: Monthly data with dates in column 4
"""

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Global cache for parsed type curve library
_TC_CACHE: Optional[Dict[str, 'TypeCurveData']] = None


@dataclass
class TypeCurveData:
    """Type curve definition with EUR, lateral length, bench, and monthly production volumes."""
    name: str
    eur_mmcf: float  # Gas EUR in MMcf
    lateral_length_ft: float
    bench: str  # e.g., "Point Pleasant", "Marcellus"
    monthly_volumes: List[float]  # Gas volumes in MMcf
    product_type: str = "gas"  # "gas" or "oil"
    
    def __repr__(self) -> str:
        return f"TypeCurve({self.name}, EUR={self.eur_mmcf:.1f} MMcf, {len(self.monthly_volumes)} months, bench={self.bench})"


def parse_tc_library(csv_path: str) -> Dict[str, TypeCurveData]:
    """
    Parse type curve library CSV and return dict of curve names to TypeCurveData.
    
    Only parses GAS curves (columns 32+), skipping oil curves (columns 6-31).
    
    The CSV has a wide format with:
    - Curve names in header row (row 0)
    - EUR values in row 2
    - Lateral length in row 4
    - Bench in row 11
    - Monthly volumes starting from row 14
    - Column 4 contains actual dates (YYYY-MM-DD) for validation
    
    Args:
        csv_path: Path to the type curve CSV file
        
    Returns:
        Dict mapping curve names to TypeCurveData objects
    """
    global _TC_CACHE
    
    # Return cached data if available
    if _TC_CACHE is not None:
        logger.info(f"Returning cached type curve library with {len(_TC_CACHE)} gas curves")
        return _TC_CACHE
    
    logger.info(f"Parsing type curve library from {csv_path}")
    curves = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        logger.debug(f"Read {len(rows)} rows from CSV")
        
        # Extract curve names from row 0
        # Gas curves start at column 32 (skip oil curves in columns 6-31)
        header_row = rows[0] if rows else []
        gas_curve_cols = {}  # {col_idx: curve_name}
        
        for col_idx in range(32, len(header_row)):  # Start at column 32 for gas curves
            cell = (header_row[col_idx] or "").strip()
            if 'APPA_' in cell or 'M_' in cell:
                gas_curve_cols[col_idx] = cell
        
        if not gas_curve_cols:
            logger.error("Could not find gas curve names in columns 32+")
            return curves
        
        curve_names = [gas_curve_cols[idx] for idx in sorted(gas_curve_cols.keys())]
        logger.info(f"Found {len(curve_names)} gas curves: {curve_names[:10]}...")
        
        # Row 2: EUR values
        eur_values = {name: 0.0 for name in curve_names}
        if len(rows) > 2:
            eur_row = rows[2]
            for col_idx, curve_name in gas_curve_cols.items():
                if col_idx < len(eur_row) and eur_row[col_idx].strip():
                    try:
                        eur_values[curve_name] = float(eur_row[col_idx])
                    except ValueError:
                        eur_values[curve_name] = 0.0
            logger.debug(f"Extracted EUR for {len([v for v in eur_values.values() if v > 0])} gas curves")
        
        # Row 4: Lateral length
        lateral_lengths = {name: 10000.0 for name in curve_names}
        if len(rows) > 4:
            lateral_row = rows[4]
            for col_idx, curve_name in gas_curve_cols.items():
                if col_idx < len(lateral_row) and lateral_row[col_idx].strip():
                    try:
                        lateral_lengths[curve_name] = float(lateral_row[col_idx])
                    except ValueError:
                        lateral_lengths[curve_name] = 10000.0
            logger.debug(f"Extracted lateral length")
        
        # Row 11: Bench designations
        benches = {name: "Unknown" for name in curve_names}
        if len(rows) > 11:
            bench_row = rows[11]
            for col_idx, curve_name in gas_curve_cols.items():
                if col_idx < len(bench_row) and bench_row[col_idx].strip():
                    benches[curve_name] = bench_row[col_idx].strip()
            logger.debug(f"Extracted bench for {len([v for v in benches.values() if v != 'Unknown'])} curves")
        
        # Extract monthly volumes (rows 14+)
        # Use column 4 (actual date) to validate and count months
        monthly_volumes = {name: [] for name in curve_names}
        data_start_idx = 14  # Monthly data starts at row 14
        months_parsed = 0
        
        logger.debug(f"Parsing monthly data from row {data_start_idx} onwards...")
        
        for i in range(data_start_idx, len(rows)):
            row = rows[i]
            
            # Validate using column 4 (actual date)
            if len(row) <= 4:
                continue
            
            date_str = row[4].strip() if row[4] else ""
            
            # Try to parse the date to validate it's a data row
            try:
                if date_str and '2026' in date_str or '2027' in date_str or '2028' in date_str:
                    # Valid date row, extract volumes
                    for col_idx, curve_name in gas_curve_cols.items():
                        if col_idx < len(row) and row[col_idx].strip():
                            try:
                                vol = float(row[col_idx])
                                monthly_volumes[curve_name].append(vol)
                            except ValueError:
                                monthly_volumes[curve_name].append(0.0)
                        else:
                            monthly_volumes[curve_name].append(0.0)
                    months_parsed += 1
                else:
                    # Stop if we hit a non-data row
                    if months_parsed > 0:
                        break
            except (ValueError, IndexError):
                if months_parsed > 0:
                    break
                continue
        
        logger.info(f"Parsed {months_parsed} months of production data")
        
        # Build TypeCurveData objects
        for curve_name in curve_names:
            curves[curve_name] = TypeCurveData(
                name=curve_name,
                eur_mmcf=eur_values.get(curve_name, 0.0),
                lateral_length_ft=lateral_lengths.get(curve_name, 10000.0),
                bench=benches.get(curve_name, "Unknown"),
                monthly_volumes=monthly_volumes.get(curve_name, []),
                product_type="gas"
            )
        
        # Cache the results
        _TC_CACHE = curves
        avg_months = len(list(curves.values())[0].monthly_volumes) if curves else 0
        logger.info(f"Successfully parsed {len(curves)} GAS type curves with ~{avg_months} months per curve")
        
    except Exception as e:
        logger.error(f"Error parsing type curve library: {e}")
        raise
    
    return curves


def get_curve(curve_name: str, csv_path: Optional[str] = None) -> Optional[TypeCurveData]:
    """
    Get a specific curve by name. Parses CSV if not already cached.
    
    Args:
        curve_name: Name of the curve (e.g., "APPA_113.1")
        csv_path: Path to CSV (required on first call)
        
    Returns:
        TypeCurveData object or None if not found
    """
    global _TC_CACHE
    
    if _TC_CACHE is None:
        if csv_path is None:
            raise ValueError("csv_path required on first call")
        parse_tc_library(csv_path)
    
    return _TC_CACHE.get(curve_name)


def clear_cache():
    """Clear the type curve cache (for testing or reloading)."""
    global _TC_CACHE
    _TC_CACHE = None
    logger.debug("Type curve cache cleared")


if __name__ == "__main__":
    # Test parsing
    logging.basicConfig(level=logging.INFO)
    
    test_csv = "/Users/steveabney/.openclaw/media/inbound/file_10---e96bd262-79b7-4217-b8c8-0b35fee55557.csv"
    
    curves = parse_tc_library(test_csv)
    
    print(f"\n✓ Parsed {len(curves)} GAS curves (skipped oil curves)")
    print(f"\nSample GAS curves:")
    
    # Show APPA_113.1 as primary example (gas version of APPA_113)
    if "APPA_113.1" in curves:
        tc = curves["APPA_113.1"]
        print(f"\n  {tc.name} (GAS - Main curve)")
        print(f"    EUR: {tc.eur_mmcf:.2f} MMcf")
        print(f"    Lateral: {tc.lateral_length_ft:.0f} ft")
        print(f"    Bench: {tc.bench}")
        print(f"    Months: {len(tc.monthly_volumes)}")
        if tc.monthly_volumes:
            print(f"    First 3 months: {[f'{v:.2f}' for v in tc.monthly_volumes[:3]]}")
    
    # Show other gas curves
    for name in sorted(curves.keys())[1:4]:
        tc = curves[name]
        print(f"\n  {tc.name}")
        print(f"    EUR: {tc.eur_mmcf:.2f} MMcf")
        print(f"    Lateral: {tc.lateral_length_ft:.0f} ft")
        print(f"    Bench: {tc.bench}")
        print(f"    Months: {len(tc.monthly_volumes)}")
        if tc.monthly_volumes:
            print(f"    First 3 months: {[f'{v:.2f}' for v in tc.monthly_volumes[:3]]}")
