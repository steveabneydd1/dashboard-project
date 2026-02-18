#!/usr/bin/env python3
"""
Extract type curves from TC.csv and organize by curve ID
"""

import csv
from typing import Dict, List

def extract_type_curves(csv_path: str) -> Dict[str, Dict]:
    """
    Parse TC.csv and extract monthly production volumes for each type curve.
    
    Returns dict like:
    {
        'APPA_113': {
            'gas': [277.7, 386.4, 421.7, ...],  # MMcf per month
            'oil': [0, 0, 0, ...],  # MBbls per month
            'eur_gas': 12060,
            'eur_oil': 0,
        },
        ...
    }
    """
    
    curves = {}
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Find header rows with column metadata
    # Row 0-8: Various header info
    # Row 9: Year, Month, Date, then units for each curve
    
    # Find the "TC Area" row to identify which columns have which curves
    tc_area_row = None
    for i, row in enumerate(rows):
        if row and row[4] == "TC Area":
            tc_area_row = i
            break
    
    if tc_area_row is None:
        print("Could not find 'TC Area' row")
        return {}
    
    # Extract curve IDs from TC Area row
    curve_ids = []
    for j, cell in enumerate(rows[tc_area_row][6:], start=6):
        if cell and cell not in ['', 'x']:
            if cell not in curve_ids:
                curve_ids.append(cell)
    
    print(f"Found curves: {curve_ids[:10]}...")
    
    # Find data start row (after headers)
    # Data starts around row 11 with Year, Month, Date
    data_start = None
    for i in range(10, min(20, len(rows))):
        if rows[i] and rows[i][0] and rows[i][0].strip() == "Year":
            # This might be a header, skip
            continue
        if rows[i] and rows[i][0].isdigit():
            data_start = i
            break
    
    if data_start is None:
        # Find first year by looking for "2026" in first column
        for i in range(10, len(rows)):
            try:
                year_val = rows[i][0].strip()
                if year_val == '2026':
                    data_start = i
                    break
            except:
                continue
    
    if data_start is None:
        data_start = 11  # Default fallback
    
    print(f"Data starts at row {data_start}")
    
    # Now parse column positions from header row (tc_area_row)
    # We need to find which column index has each curve
    
    # Simpler approach: find columns by looking for curve IDs in header
    header_row = rows[tc_area_row]
    
    curve_columns = {}  # curve_id -> column_index
    for col_idx, cell in enumerate(header_row):
        if cell and cell in curve_ids:
            curve_columns[cell] = col_idx
    
    print(f"\nCurve columns: {curve_columns}")
    
    # Extract data for each curve
    for curve_id in curve_columns:
        col_idx = curve_columns[curve_id]
        gas_volumes = []
        oil_volumes = []
        
        # Collect volumes from all data rows
        for row_idx in range(data_start, len(rows)):
            row = rows[row_idx]
            if len(row) > col_idx and row[col_idx]:
                try:
                    volume = float(row[col_idx])
                    gas_volumes.append(volume)
                except:
                    pass
        
        # For now, assume all are gas curves (dry gas)
        # We can refine this later
        if gas_volumes:
            curves[curve_id] = {
                'gas_monthly': gas_volumes,
                'oil_monthly': [0.0] * len(gas_volumes),
                'eur_gas': sum(gas_volumes),
                'eur_oil': 0.0,
            }
            print(f"{curve_id}: {len(gas_volumes)} months, EUR={sum(gas_volumes):.1f} MMcf")
    
    return curves


if __name__ == '__main__':
    curves = extract_type_curves('/Users/steveabney/Downloads/TC.csv')
    
    # Show APPA_113 specifically
    if 'APPA_113' in curves:
        curve = curves['APPA_113']
        print(f"\nAPPA_113 Gas Production (first 20 months):")
        for month, volume in enumerate(curve['gas_monthly'][:20], 1):
            print(f"  Month {month}: {volume:.1f} MMcf")
