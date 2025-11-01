#!/usr/bin/env python3
"""Script to read PDF and display each line to console."""

import sys
from pathlib import Path
import pdfplumber




def normalize_row_with_header(row, expected_header):
    """Merge cells in a row to match expected header structure.
    
    Attempts to combine split cells to form the expected column names.
    """
    if not expected_header:
        return row
    
    row_text = ' '.join(str(cell).strip() for cell in row if cell).lower()
    normalized = []
    row_idx = 0
    
    for expected_col in expected_header:
        expected_lower = expected_col.lower()
        expected_len = len(expected_lower)
        
        # Try to find this column by matching cells
        matched_cells = []
        current_text = ""
        
        # Start from where we left off
        for i in range(row_idx, len(row)):
            cell = str(row[i]).strip() if row[i] else ""
            if not cell:
                continue
            
            current_text += cell
            matched_cells.append(i)
            
            # Check if we've matched the expected column
            if expected_lower in current_text.lower() or current_text.lower() in expected_lower:
                normalized.append(current_text.strip())
                row_idx = i + 1
                break
            
            # If current text is longer than expected, we might have overshot
            if len(current_text) > expected_len * 1.5:
                # Try to see if we can extract the expected column
                if expected_lower in current_text.lower():
                    normalized.append(expected_col)  # Use expected name
                    row_idx = i + 1
                    break
        
        # If we didn't find a match, try to extract from remaining cells
        if len(normalized) <= len([n for n in normalized if n]):
            remaining = ' '.join(str(row[j]).strip() for j in range(row_idx, len(row)) if row[j])
            if expected_lower in remaining.lower():
                # Extract just this part
                normalized.append(expected_col)
                # Advance row_idx somehow - this is approximate
                row_idx += 1
            else:
                normalized.append("")
    
    # If we have fewer columns than expected, pad
    while len(normalized) < len(expected_header):
        normalized.append("")
    
    return normalized[:len(expected_header)]


def extract_rows(pdf_path: str, table_settings=None, header_text=None, 
                 skip_rows=0, crop_bbox=None, table_bbox=None, expected_header=None):
    """Extract table rows from first page. Each row is a list.
    
    Args:
        pdf_path: Path to PDF file
        table_settings: Dict of table extraction settings for pdfplumber
        header_text: Expected header text to help identify table location
        skip_rows: Number of rows to skip from the beginning
        crop_bbox: Bounding box to crop page (legacy, use table_bbox instead)
        table_bbox: Exact bounding box of table area: dict {left, top, right, bottom} or tuple (x0, top, x1, bottom)
                    This crops to exactly where the table is, excluding headers and rotated text
        expected_header: List of expected column names, e.g., ['Nr. crt.', 'Cod LMI', 'Denumire', ...]
                         Used to merge incorrectly split header cells and align columns
    """
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            if len(pdf.pages) == 0:
                print("Error: PDF has no pages")
                sys.exit(1)
            
            first_page = pdf.pages[0]
            
            # Use table_bbox if provided, otherwise fall back to crop_bbox
            bbox_to_use = table_bbox if table_bbox is not None else crop_bbox
            
            # Crop page to table area if bbox provided
            if bbox_to_use:
                if isinstance(bbox_to_use, dict):
                    # Convert dict to tuple: (x0, top, x1, bottom)
                    x0 = bbox_to_use.get('left', 0) if bbox_to_use.get('left') is not None else 0
                    top = bbox_to_use.get('top', 0) if bbox_to_use.get('top') is not None else 0
                    x1 = bbox_to_use.get('right') if bbox_to_use.get('right') is not None else first_page.width
                    bottom = bbox_to_use.get('bottom') if bbox_to_use.get('bottom') is not None else first_page.height
                    first_page = first_page.crop((x0, top, x1, bottom))
                    print(f"Cropped to table area: left={x0:.1f}, top={top:.1f}, right={x1:.1f}, bottom={bottom:.1f}")
                else:
                    # Assume tuple (x0, top, x1, bottom)
                    first_page = first_page.crop(bbox_to_use)
                    print(f"Cropped to table area with bbox: {bbox_to_use}")
            
            # Try different table extraction strategies
            strategies = [
                table_settings,  # Custom settings if provided
                {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
                {"vertical_strategy": "text", "horizontal_strategy": "text"},
                {"vertical_strategy": "explicit", "horizontal_strategy": "explicit"},
                None,  # Default settings
            ]
            
            tables = None
            for i, strategy in enumerate(strategies):
                if strategy is None and i != len(strategies) - 1:
                    continue
                try:
                    if strategy:
                        tables = first_page.extract_tables(strategy)
                    else:
                        tables = first_page.extract_tables()
                    if tables:
                        print(f"Found {len(tables)} table(s) using strategy {i+1}")
                        break
                except Exception as e:
                    continue
            
            if not tables:
                print("No tables found. Trying structured text extraction...")
                # Fallback: extract text and try to parse it
                text = first_page.extract_text()
                if text:
                    lines = text.split('\n')
                    print(f"Found {len(lines)} text lines")
                    print("\nFirst 20 lines:")
                    for i, line in enumerate(lines[:20], 1):
                        print(f"{i:3}: {line}")
                return
            
            # Get the first table
            table = tables[0]
            
            print(f"Table has {len(table)} rows (before filtering)")
            
            # Skip initial rows if specified
            if skip_rows > 0:
                print(f"Skipping first {skip_rows} row(s)")
                table = table[skip_rows:]
            
            # Find header row
            header_row_idx = None
            if expected_header:
                # Look for row that contains parts of expected header
                for i, row in enumerate(table):
                    row_text = ' '.join(str(cell).strip() for cell in row if cell).lower()
                    # Check if any expected header column is in this row
                    for col in expected_header:
                        if col.lower() in row_text:
                            header_row_idx = i
                            print(f"Found header row {i} (contains '{col}')")
                            break
                    if header_row_idx is not None:
                        break
            elif header_text:
                for i, row in enumerate(table):
                    row_text = ' '.join(str(cell) for cell in row if cell)
                    if header_text.lower() in row_text.lower():
                        header_row_idx = i
                        print(f"Found header at row {i}: {row}")
                        break
            
            # Normalize header row if expected_header provided
            if expected_header and header_row_idx is not None:
                raw_header = table[header_row_idx]
                normalized_header = normalize_row_with_header(raw_header, expected_header)
                print(f"Raw header: {raw_header}")
                print(f"Normalized header: {normalized_header}")
                print("=" * 80)
                start_idx = header_row_idx + 1
            else:
                start_idx = header_row_idx + 1 if header_row_idx is not None else 0
            
            # Filter out empty rows (rows with all empty cells)
            filtered_table = []
            row_numbers = []  # Keep track of original row indices
            
            for orig_row_idx, row in enumerate(table[start_idx:], start=start_idx):
                if any(cell and str(cell).strip() for cell in row):
                    # Try to normalize row if we have expected_header
                    if expected_header:
                        # Better approach: group cells based on position and content
                        # Look for patterns that indicate column boundaries
                        expected_cols = len(expected_header)
                        merged_row = [""] * expected_cols
                        
                        # Strategy: if row has too many cells, try to intelligently merge
                        # Look for cells that start with numbers (col 0), LMI codes (col 1), etc.
                        non_empty_cells = [(i, str(cell).strip()) for i, cell in enumerate(row) if cell and str(cell).strip()]
                        
                        if len(non_empty_cells) <= expected_cols:
                            # Not too many cells, just use them directly
                            for idx, (orig_idx, cell) in enumerate(non_empty_cells):
                                if idx < expected_cols:
                                    merged_row[idx] = cell
                        else:
                            # Too many cells - try to merge intelligently
                            # First cell should be number (Nr. crt.)
                            if non_empty_cells:
                                merged_row[0] = non_empty_cells[0][1]
                            
                            # Second cell should start with letters (Cod LMI)
                            lmi_idx = 1
                            for i, (_, cell) in enumerate(non_empty_cells[1:], 1):
                                # Look for pattern like "AB-I-s-A-00001"
                                if any(part in cell for part in ["-I-", "-m-", "-s-", "-A-", "-B-"]) or len(cell) > 8:
                                    merged_row[1] = cell
                                    lmi_idx = i + 1
                                    break
                            
                            # Remaining cells - merge until we have expected column count
                            remaining = non_empty_cells[lmi_idx:]
                            if remaining:
                                # Distribute remaining cells across remaining columns
                                cells_per_col = max(1, len(remaining) // (expected_cols - 2))
                                col_idx = 2
                                for i, (_, cell) in enumerate(remaining):
                                    if col_idx < expected_cols:
                                        if not merged_row[col_idx]:
                                            merged_row[col_idx] = cell
                                        else:
                                            merged_row[col_idx] += " " + cell
                                        # Move to next column after cells_per_col cells
                                        if (i + 1) % cells_per_col == 0:
                                            col_idx += 1
                        
                        filtered_table.append(merged_row)
                        row_numbers.append(orig_row_idx)
                    else:
                        filtered_table.append(row)
                        row_numbers.append(orig_row_idx)
            
            print(f"\nShowing {len(filtered_table)} data rows")
            print("=" * 80)
            
            # Each row is a list - print each row with original row number
            for i, (orig_row_num, row) in enumerate(zip(row_numbers, filtered_table)):
                print(f"Row {orig_row_num}: {row}")
    
    except Exception as e:
        print(f"Error reading PDF: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    pdf_path = None
    header_text = None
    
    # Simple argument parsing
    args = sys.argv[1:]
    if args:
        pdf_path = args[0]
        if len(args) > 1:
            header_text = args[1]
    
    if not pdf_path:
        script_dir = Path(__file__).parent
        pdf_path = script_dir / "pdfs" / "Alba.pdf"
    
    # You can customize table_settings here
    # Example: {"vertical_strategy": "lines", "horizontal_strategy": "lines"}
    table_settings = None
    
    # Table bounding box: exact coordinates of the table area
    # Format: {left, top, right, bottom} in points (PDF coordinates)
    # You can get these values by inspecting the PDF or trial and error
    # Set to None if you want to extract from full page
    table_bbox = {
        "left": 0,      # Left edge of table (adjust as needed)
        "top": 0,     # Top edge of table (below headers/title)
        "right": 800,   # Right edge of table (before rotated text)
        "bottom": 550   # Bottom edge of table (adjust as needed)
    }
    # Or use None to disable
    # table_bbox = None
    
    # Legacy crop_bbox (deprecated, use table_bbox instead)
    crop_bbox = None
    
    # Skip first N rows (e.g., title/header rows that mess up column count)
    skip_rows = 0  # Skip first 3 rows
    
    # Expected header: provide the correct column names to merge split cells
    # This helps when PDF splits cells incorrectly (e.g., "Denum" + "ire" = "Denumire")
    expected_header = [
        "Nr. crt.",
        "Cod LMI",
        "Denumire",
        "Localitate",
        "Adresă",
        "Datare"
    ]
    # Set to None if you don't want header normalization
    # expected_header = None
    
    extract_rows(
        str(pdf_path), 
        table_settings=table_settings, 
        header_text=header_text,
        skip_rows=skip_rows,
        crop_bbox=crop_bbox,
        table_bbox=table_bbox,
        expected_header=expected_header
    )
