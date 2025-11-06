#!/usr/bin/env python3
"""Script to read PDF and visualize column boundaries."""

import sys
from pathlib import Path
import pdfplumber

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Error: PIL/Pillow required. Install with: pip install Pillow")
    sys.exit(1)


def visualize_column_lines(pdf_path: str, column_coords: dict, table_bbox_percent: dict = None, 
                           page_num: int = 0, output_path: str = None):
    """Draw vertical lines on PDF page at column boundary coordinates.
    
    This function helps you find the correct x-coordinates for each column.
    Column coordinates are in ORIGINAL PAGE SPACE (before any cropping).
    
    Args:
        pdf_path: Path to PDF file
        column_coords: Dict mapping column names to x-coordinates (in PDF points, ORIGINAL PAGE SPACE)
                      Example: {"Nr. crt.": 50, "Cod LMI": 100, "Denumire": 200}
                      These coordinates are relative to the full page, not the cropped area
        table_bbox_percent: Dict with percentages for table bounding box (for visualization only)
                           {"left": 0.0, "top": 0.1, "right": 1.0, "bottom": 0.9}
                           If None, uses full page
        page_num: Page number (0-indexed)
        output_path: Path to save image. If None, saves next to PDF.
    
    Returns:
        Path to saved image
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return None
    
    with pdfplumber.open(pdf_file) as pdf:
        if page_num >= len(pdf.pages):
            print(f"Error: Page {page_num} not found. PDF has {len(pdf.pages)} page(s)")
            return None
        
        page = pdf.pages[page_num]
        
        # Store original page dimensions (column_coords are in original page space)
        original_width = page.width
        original_height = page.height
        
        # Print page dimensions (ORIGINAL PAGE SPACE - this is what column_coords use)
        print(f"Page {page_num + 1} dimensions: {original_width:.1f} x {original_height:.1f} points")
        print(f"  (1 point = 1/72 inch, so {original_width/72:.2f} x {original_height/72:.2f} inches)")
        print(f"  Column coordinates are in this original page space")
        
        # Convert percentage bbox to absolute coordinates (for visualization crop only)
        crop_left = 0
        if table_bbox_percent:
            left = original_width * table_bbox_percent.get("left", 0.0)
            top = original_height * table_bbox_percent.get("top", 0.0)
            right = original_width * table_bbox_percent.get("right", 1.0)
            bottom = original_height * table_bbox_percent.get("bottom", 1.0)
            page = page.crop((left, top, right, bottom))
            print(f"Visualization cropped to: left={left:.1f}, top={top:.1f}, right={right:.1f}, bottom={bottom:.1f}")
            crop_left = left
        
        # Convert page to image
        im = page.to_image(resolution=150)
        pil_image = im.original
        draw = ImageDraw.Draw(pil_image)
        
        # Colors for different columns
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 165, 0),  # Orange
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
        ]
        
        # Sort columns by x-coordinate
        sorted_columns = sorted(column_coords.items(), key=lambda x: x[1])
        
        # Draw vertical lines for each column boundary
        for i, (col_name, x_coord) in enumerate(sorted_columns):
            # Convert x-coordinate from original page space to cropped image space
            scale = pil_image.width / page.width
            adjusted_x = (x_coord - crop_left) * scale
            
            # Choose color (cycle through if more columns than colors)
            color = colors[i % len(colors)]
            
            # Draw vertical line
            draw.line([(adjusted_x, 0), (adjusted_x, pil_image.height)], fill=color, width=3)
            
            # Draw label
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
            except:
                font = ImageFont.load_default()
            
            # Draw text with background for readability
            text = f"{col_name} ({x_coord:.0f})"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Draw background rectangle
            padding = 4
            draw.rectangle(
                [(adjusted_x + 5, 10 + i * 25), 
                 (adjusted_x + 5 + text_width + padding * 2, 10 + i * 25 + text_height + padding * 2)],
                fill=(255, 255, 255, 200)
            )
            draw.text((adjusted_x + 5 + padding, 10 + i * 25 + padding), text, fill=color, font=font)
        
        # Save image
        if output_path is None:
            output_path = pdf_file.parent / f"{pdf_file.stem}_page{page_num+1}_columns.png"
        else:
            output_path = Path(output_path)
        
        pil_image.save(output_path)
        print(f"\nVisualization saved to: {output_path}")
        print(f"Column boundaries:")
        for col_name, x_coord in sorted_columns:
            print(f"  {col_name}: x = {x_coord:.1f} points")
        
        return output_path


if __name__ == "__main__":
    # Hardcoded PDF path
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "pdfs" / "Alba.pdf"
    
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)
    
    # Column coordinates dictionary (x-coordinates in PDF points)
    # These are the starting x-coordinates for each column
    column_coords = {
        "Nr. crt.": 30,
        "Cod LMI": 80,
        "Denumire": 195,
        "Localitate": 342,
        "Adresă": 475,
        "Datare": 665,
    }
    
    # Table bounding box as percentages (0.0 to 1.0)
    # None means use full page
    table_bbox_percent = {
        "left": 0.04,    # 0% from left edge
        "top": 0.25,    # 15% from top (skip header/title)
        "right": 0.97,   # 90% from left
        "bottom": 0.9,  # 80% from top (leave some margin at bottom)
    }
    # Or set to None to use full page:
    # table_bbox_percent = None
    
    # Visualize
    visualize_column_lines(
        str(pdf_path),
        column_coords=column_coords,
        table_bbox_percent=table_bbox_percent,
        page_num=0,
    )
