#!/usr/bin/env python3
"""
Break apart an Excel workbook into CSV files (one per sheet).
Uses only standard library (zipfile + xml).
Usage: python3 excel_to_csv.py <path_to_excel_file> [output_dir]
"""

import sys
import csv
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict

def excel_to_csv(excel_path, output_dir=None):
    """Convert all sheets in an Excel file to CSV files using standard lib only."""
    
    excel_file = Path(excel_path)
    if not excel_file.exists():
        print(f"Error: File not found: {excel_path}")
        return False
    
    if output_dir is None:
        output_dir = excel_file.parent / f"{excel_file.stem}_csv"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    try:
        # .xlsx is a zip file
        with zipfile.ZipFile(excel_path, 'r') as zip_ref:
            # Read workbook.xml to get sheet names
            workbook_xml = zip_ref.read('xl/workbook.xml')
            wb_root = ET.fromstring(workbook_xml)
            
            # Extract sheet names
            ns = {'': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            sheets = []
            for sheet in wb_root.findall('.//{}sheet', ns):
                sheet_id = sheet.get('sheetId')
                name = sheet.get('name')
                rid = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                sheets.append((name, rid, sheet_id))
            
            # Read relationships to map rIds to file paths
            rels_xml = zip_ref.read('xl/_rels/workbook.xml.rels')
            rels_root = ET.fromstring(rels_xml)
            rid_to_file = {}
            for rel in rels_root.findall('.//'):
                rid = rel.get('Id')
                target = rel.get('Target')
                if rid and target:
                    rid_to_file[rid] = target
            
            print(f"Found {len(sheets)} sheets:")
            for name, rid, _ in sheets:
                print(f"  - {name}")
            print()
            
            # Process each sheet
            for sheet_name, rid, sheet_id in sheets:
                print(f"Converting '{sheet_name}'...", end=" ")
                
                # Get the worksheet file
                sheet_file = rid_to_file.get(rid)
                if not sheet_file:
                    print("(skipped - no file mapping)")
                    continue
                
                sheet_path = f"xl/{sheet_file}"
                if sheet_path not in zip_ref.namelist():
                    print("(skipped - file not found)")
                    continue
                
                # Read worksheet XML
                sheet_xml = zip_ref.read(sheet_path)
                sheet_root = ET.fromstring(sheet_xml)
                
                # Extract cell values
                ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
                rows_data = []
                
                for row in sheet_root.findall(f'{{{ns}}}sheetData/{{{ns}}}row'):
                    row_num = int(row.get('r'))
                    row_data = {}
                    
                    for cell in row.findall(f'{{{ns}}}c'):
                        cell_ref = cell.get('r')  # e.g., "A1"
                        cell_type = cell.get('t', 'n')  # type: s=string, n=number, b=boolean, etc
                        
                        # Extract column letter from cell ref (A, B, C, ...)
                        col_letter = ''.join(c for c in cell_ref if c.isalpha())
                        col_num = sum((ord(c) - ord('A') + 1) * (26 ** (len(col_letter) - i - 1)) 
                                     for i, c in enumerate(col_letter))
                        
                        # Get cell value
                        value = None
                        v_elem = cell.find(f'{{{ns}}}v')
                        if v_elem is not None and v_elem.text:
                            if cell_type == 's':
                                # String - need to look up in shared strings
                                value = v_elem.text
                            else:
                                value = v_elem.text
                        
                        row_data[col_num] = value
                    
                    rows_data.append((row_num, row_data))
                
                # Convert to CSV format
                if rows_data:
                    # Sort by row number
                    rows_data.sort(key=lambda x: x[0])
                    
                    # Find max column
                    max_col = max(max(row[1].keys()) if row[1] else 0 for row in rows_data)
                    
                    # Sanitize sheet name for filename
                    safe_name = "".join(c for c in sheet_name if c.isalnum() or c in " -_").rstrip()
                    output_file = output_dir / f"{safe_name}.csv"
                    
                    # Write CSV
                    with open(output_file, 'w', newline='') as f:
                        writer = csv.writer(f)
                        for row_num, row_data in rows_data:
                            row_values = [row_data.get(col, '') for col in range(1, max_col + 1)]
                            writer.writerow(row_values)
                    
                    print(f"✓ ({len(rows_data)} rows, {max_col} cols) → {output_file.name}")
                else:
                    print("(empty sheet)")
        
        print(f"\nDone! CSVs saved to: {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 excel_to_csv.py <excel_file> [output_dir]")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = excel_to_csv(excel_file, output_dir)
    sys.exit(0 if success else 1)
