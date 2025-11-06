#!/usr/bin/env python3
"""Script to extract table rows from PDF using explicit column boundaries."""

import sys
from pathlib import Path
import pdfplumber
from pdf_config import COLUMN_COORDS, TABLE_BBOX_PERCENT, OTHER_PAGES_TOP


def is_child_row(row: list) -> bool:
    """Check if a row is a child row (has empty first column)."""
    return row and not row[0].strip()


def merge_child_into_parent(parent_row: list, child_row: list) -> None:
    """Merge a child row into its parent row with space separators."""
    for col_idx in range(len(child_row)):
        if col_idx < len(parent_row):
            if child_row[col_idx].strip():
                parent_row[col_idx] = parent_row[col_idx] + " " + child_row[col_idx].strip()
        else:
            parent_row.append(child_row[col_idx].strip())


def merge_rows_on_page(rows: list) -> list:
    """Merge child rows into parent rows within a single page."""
    merged_rows = []
    for row in rows:
        if is_child_row(row):
            if merged_rows:
                merge_child_into_parent(merged_rows[-1], row)
        else:
            merged_rows.append(row)
    return merged_rows


def calculate_crop(page_width: float, page_height: float, table_bbox_percent: dict, 
                   other_pages_top: float = 0.1) -> dict:
    """Calculate crop coordinates for table extraction."""
    return {
        'left': page_width * table_bbox_percent.get("left", 0.0),
        'right': page_width * table_bbox_percent.get("right", 1.0),
        'bottom': page_height * table_bbox_percent.get("bottom", 1.0),
        'first': page_height * table_bbox_percent.get("top", 0.0),
        'top': page_height * other_pages_top,
    }


def extract_table(pdf_path: str, column_coords: dict, table_bbox_percent: dict,
                  page_num: int = None, other_pages_top: float = 0.1):
    """Extract table rows and split into columns based on column boundaries."""
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return None
    
    with pdfplumber.open(pdf_file) as pdf:
        # Determine which pages to process
        if page_num is None:
            pages_to_process = range(len(pdf.pages))
        else:
            if page_num >= len(pdf.pages):
                return None
            pages_to_process = [page_num]
        
        all_rows = []
        last_row_from_previous_page = None
        
        first_page = pdf.pages[pages_to_process[0]]
        crop = calculate_crop(first_page.width, first_page.height, table_bbox_percent, other_pages_top)
        
        for current_page_num in pages_to_process:
            page = pdf.pages[current_page_num]
            page_width = page.width
            page_height = page.height
        
            crop_top = crop['first'] if current_page_num == 0 else crop['top']
            page = page.crop((crop['left'], crop_top, crop['right'], crop['bottom']))
            
            sorted_columns = sorted(column_coords.items(), key=lambda x: x[1])
            column_boundaries = []
            for col_name, x_original in sorted_columns:
                x_cropped = x_original - crop['left']
                column_boundaries.append(x_cropped)
            
            cropped_width = crop['right'] - crop['left']
            column_boundaries.append(cropped_width)
            column_boundaries = sorted(list(set(column_boundaries)))
            
            words = page.extract_words()
            
            # Group words by y-position to form lines
            rows_dict = {}
            for word in words:
                y_rounded = round(word['top'] / 2) * 2
                if y_rounded not in rows_dict:
                    rows_dict[y_rounded] = []
                rows_dict[y_rounded].append(word)
            
            # Assign words to columns based on x-coordinates
            result_rows = []
            for y_pos in sorted(rows_dict.keys()):
                row_words = sorted(rows_dict[y_pos], key=lambda w: w['x0'])
                
                row_columns = [""] * (len(column_boundaries) - 1)
                for word in row_words:
                    word_x = word['x0']
                    for col_idx in range(len(column_boundaries) - 1):
                        left_bound = column_boundaries[col_idx]
                        right_bound = column_boundaries[col_idx + 1]
                        # Last column includes right boundary
                        if col_idx == len(column_boundaries) - 2:
                            if left_bound <= word_x <= right_bound:
                                if row_columns[col_idx]:
                                    row_columns[col_idx] += " "
                                row_columns[col_idx] += word['text']
                                break
                        else:
                            if left_bound <= word_x < right_bound:
                                if row_columns[col_idx]:
                                    row_columns[col_idx] += " "
                                row_columns[col_idx] += word['text']
                                break
                
                if any(col.strip() for col in row_columns):
                    result_rows.append([col.strip() for col in row_columns])
            
            # Remove header row (first row on each page)
            result_rows = result_rows[1:]
            
            # Handle cross-page row continuation (parent row on previous page, child row on this page)
            if last_row_from_previous_page is not None and result_rows:
                first_row = result_rows[0]
                if is_child_row(first_row):
                    merge_child_into_parent(last_row_from_previous_page, first_row)
                    all_rows[-1] = last_row_from_previous_page
                    result_rows = result_rows[1:]
            
            merged_rows = merge_rows_on_page(result_rows)
            
            all_rows.extend(merged_rows)
            
            if merged_rows:
                last_row_from_previous_page = merged_rows[-1]
            else:
                last_row_from_previous_page = None
        
        return all_rows


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "pdfs" / "Bucuresti.pdf"
    
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)
    
    rows = extract_table(
        str(pdf_path),
        column_coords=COLUMN_COORDS,
        table_bbox_percent=TABLE_BBOX_PERCENT,
        page_num=None,  # None = process all pages
        other_pages_top=OTHER_PAGES_TOP,
    )
    
    if rows:
        print("\n" + "=" * 80)
        print("All rows (with columns):")
        for i, row in enumerate(rows, 1):
            print(f"{i:3}: {row}")
