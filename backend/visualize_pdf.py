#!/usr/bin/env python3
"""Script to visualize PDF column boundaries - helps find correct coordinates."""

import sys
from pathlib import Path
import pdfplumber
from PIL import Image, ImageDraw, ImageFont
from pdf_config import COLUMN_COORDS, TABLE_BBOX_PERCENT, OTHER_PAGES_TOP


def visualize_column_lines(pdf_path: str, column_coords: dict = None, table_bbox_percent: dict = None, 
                           page_num: int = 0, output_path: str = None, other_pages_top: float = 0.1,
                           cropped_coords: list = None):
    """Draw vertical lines on PDF page at column boundary coordinates.
    
    This function helps you find the correct x-coordinates for each column.
    Can visualize either original page space coordinates or already-converted cropped coordinates.
    
    Args:
        pdf_path: Path to PDF file
        column_coords: Dict mapping column names to x-coordinates (in PDF points, ORIGINAL PAGE SPACE)
                      Example: {"Nr. crt.": 50, "Cod LMI": 100, "Denumire": 200}
                      These coordinates are relative to the full page, not the cropped area
                      If cropped_coords is provided, this is ignored
        table_bbox_percent: Dict with percentages for table bounding box (for visualization only)
                           {"left": 0.0, "top": 0.1, "right": 1.0, "bottom": 0.9}
                           If None, uses full page
                           For pages other than 0, the 'top' value is overridden by other_pages_top
        page_num: Page number (0-indexed)
        output_path: Path to save image. If None, saves next to PDF.
        other_pages_top: Top percentage to use for pages other than 0 (default 0.1)
        cropped_coords: List of x-coordinates already in cropped page space.
                       If provided, these are used directly (no conversion needed).
                       Useful for visualizing the actual coordinates used during extraction.
                       Example: [0, 46.3, 161.3, 308.3, 441.3, 631.3, 783.1]
    
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
        crop_right = original_width
        if table_bbox_percent:
            # Use different top value for pages other than 0
            bbox_to_use = table_bbox_percent.copy()
            if page_num != 0:
                bbox_to_use["top"] = other_pages_top
            
            left = original_width * bbox_to_use.get("left", 0.0)
            top = original_height * bbox_to_use.get("top", 0.0)
            right = original_width * bbox_to_use.get("right", 1.0)
            bottom = original_height * bbox_to_use.get("bottom", 1.0)
            page = page.crop((left, top, right, bottom))
            print(f"Visualization cropped to: left={left:.1f}, top={top:.1f}, right={right:.1f}, bottom={bottom:.1f}")
            if page_num != 0:
                print(f"  (Using other_pages_top={other_pages_top} for page {page_num})")
            crop_left = left
            crop_right = right
        
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
        
        # Determine which coordinates to use
        if cropped_coords is not None:
            # Use provided cropped coordinates directly
            x_coords_to_draw = sorted(cropped_coords)
            labels = [f"Boundary {i+1}" for i in range(len(x_coords_to_draw))]
            print(f"Using provided cropped coordinates: {x_coords_to_draw}")
        else:
            # Use original page space coordinates and convert
            if column_coords is None:
                print("Error: Either column_coords or cropped_coords must be provided")
                return None
            sorted_columns = sorted(column_coords.items(), key=lambda x: x[1])
            x_coords_to_draw = []
            labels = []
            for col_name, x_coord in sorted_columns:
                x_cropped = x_coord - crop_left
                if x_cropped >= 0 and x_cropped <= (crop_right - crop_left):
                    x_coords_to_draw.append(x_cropped)
                    labels.append(f"{col_name} ({x_coord:.0f})")
        
        # Draw vertical lines for each column boundary
        for i, x_coord in enumerate(x_coords_to_draw):
            # Convert from cropped page space to image pixels
            scale = pil_image.width / page.width
            adjusted_x = x_coord * scale
            
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
            text = f"{labels[i]} ({x_coord:.1f})"
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
        print(f"Column boundaries (cropped space):")
        for i, x_coord in enumerate(x_coords_to_draw):
            print(f"  {labels[i]}: x = {x_coord:.1f} points")
        
        return output_path


def main():
    # Hardcoded PDF path
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "pdfs" / "Alba.pdf"
    
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)
    
    # Visualize column boundaries
    # Option 1: See on FULL PAGE (no crop) - use original column_coords
    visualize_column_lines(
        str(pdf_path),
        column_coords=COLUMN_COORDS,
        table_bbox_percent=None,  # No crop - see full page
        page_num=0,
        other_pages_top=OTHER_PAGES_TOP,
    )
    
    # Option 2: See on CROPPED AREA - use cropped_coords (what extraction actually uses)
    # visualize_column_lines(
    #     str(pdf_path),
    #     cropped_coords=[0, 46.318400000000004, 161.3184, 308.3184, 441.3184, 631.3184, 783.0971999999999],
    #     table_bbox_percent=TABLE_BBOX_PERCENT,
    #     page_num=0,
    #     other_pages_top=OTHER_PAGES_TOP,
    # )


if __name__ == "__main__":
    main()

