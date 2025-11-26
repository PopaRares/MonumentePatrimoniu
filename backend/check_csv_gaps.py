#!/usr/bin/env python3
"""Check CSV files for missing row numbers in the first column."""

import csv
from pathlib import Path


def check_csv_gaps(csv_path: Path):
    """Check a CSV file for missing numbers in the first column."""
    numbers = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # Skip header row
            next(reader, None)
            
            for row in reader:
                if row and len(row) > 0:
                    try:
                        num = int(row[0].strip())
                        numbers.append(num)
                    except (ValueError, IndexError):
                        # Skip non-numeric or empty first column
                        continue
        
        if not numbers:
            print(f"{csv_path.name}: No valid numbers found")
            return
        
        max_num = max(numbers)
        expected = set(range(1, max_num + 1))
        actual = set(numbers)
        missing = sorted(expected - actual)
        
        if missing:
            print(f"{csv_path.name}: Missing numbers: {missing}")
        else:
            print(f"{csv_path.name}: ✓ All numbers present (1-{max_num})")
            
    except Exception as e:
        print(f"{csv_path.name}: Error reading file - {e}")


def main():
    script_dir = Path(__file__).parent
    csvs_dir = script_dir / "csvs"
    
    if not csvs_dir.exists():
        print(f"Error: CSV directory not found: {csvs_dir}")
        return
    
    csv_files = sorted(csvs_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {csvs_dir}")
        return
    
    print(f"Checking {len(csv_files)} CSV files...\n")
    
    for csv_path in csv_files:
        check_csv_gaps(csv_path)


if __name__ == "__main__":
    main()

