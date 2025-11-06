#!/usr/bin/env python3
"""Configuration for PDF table extraction - column coordinates and table bounds."""

# Column coordinates dictionary (x-coordinates in PDF points, ORIGINAL PAGE SPACE)
# These are the starting x-coordinates for each column boundary
COLUMN_COORDS = {
    "Nr. crt.": 30,
    "Cod LMI": 100,
    "Denumire": 200,
    "Localitate": 350,
    "Adresă": 475,
    "Datare": 665,
}

# Table bounding box as percentages (0.0 to 1.0)
# Used for page 0
TABLE_BBOX_PERCENT = {
    "left": 0.03,   # Adjusted to include first column (was 0.04, which cut into it)
    "top": 0.25,    # Used for page 0
    "right": 0.97,
    "bottom": 0.92,
}

# Top percentage for pages other than 0
# Page 0 uses TABLE_BBOX_PERCENT["top"], other pages use this value
OTHER_PAGES_TOP = 0.1

