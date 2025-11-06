#!/usr/bin/env python3
"""Import all PDFs into the database."""

import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import os

from models import Monument, Base
from read_pdf import extract_table
from pdf_config import COLUMN_COORDS, TABLE_BBOX_PERCENT, OTHER_PAGES_TOP


def get_county_from_filename(filename: str) -> str:
    """Extract county name from filename (remove .pdf extension)."""
    return Path(filename).stem


def map_row_to_monument(row: list, county: str) -> Monument:
    """Map extracted row data to Monument model.
    
    Row columns: [Nr. crt., Cod LMI, Denumire, Localitate, Adresă, Datare]
    """
    try:
        # Parse row number (first column)
        id_value = int(row[0]) if row[0] and row[0].strip() else None
        
        return Monument(
            id=id_value,
            lmi_code=row[1] if len(row) > 1 and row[1] else "",
            name=row[2] if len(row) > 2 and row[2] else "",
            city=row[3] if len(row) > 3 and row[3] else "",
            address=row[4] if len(row) > 4 and row[4] else None,
            dating=row[5] if len(row) > 5 and row[5] else None,
            county=county,
        )
    except (ValueError, IndexError):
        return None


def import_pdf(pdf_path: Path, db_session, county: str):
    """Import a single PDF into the database."""
    print(f"Processing: {pdf_path.name}")
    
    rows = extract_table(
        str(pdf_path),
        column_coords=COLUMN_COORDS,
        table_bbox_percent=TABLE_BBOX_PERCENT,
        page_num=None,  # Process all pages
        other_pages_top=OTHER_PAGES_TOP,
    )
    
    if not rows:
        print(f"  No rows extracted")
        return 0, 0
    
    imported = 0
    errors = 0
    
    for row in rows:
        monument = map_row_to_monument(row, county)
        if not monument:
            errors += 1
            continue
        
        try:
            db_session.add(monument)
            db_session.commit()
            imported += 1
        except IntegrityError:
            db_session.rollback()
            # Try to update existing record
            try:
                existing = db_session.query(Monument).filter_by(lmi_code=monument.lmi_code).first()
                if existing:
                    existing.id = monument.id
                    existing.name = monument.name
                    existing.city = monument.city
                    existing.address = monument.address
                    existing.dating = monument.dating
                    existing.county = monument.county
                    db_session.commit()
                    imported += 1
                else:
                    errors += 1
            except Exception as e:
                db_session.rollback()
                errors += 1
        except Exception as e:
            db_session.rollback()
            errors += 1
    
    print(f"  Imported: {imported}, Errors: {errors}")
    return imported, errors


def main():
    script_dir = Path(__file__).parent
    pdfs_dir = script_dir / "pdfs"
    
    if not pdfs_dir.exists():
        print(f"Error: PDFs directory not found: {pdfs_dir}")
        sys.exit(1)
    
    # Database setup
    database_url = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/patrimoniu")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get all PDF files
    pdf_files = sorted(pdfs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {pdfs_dir}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files\n")
    
    db_session = SessionLocal()
    total_imported = 0
    total_errors = 0
    
    try:
        for pdf_path in pdf_files:
            county = get_county_from_filename(pdf_path.name)
            imported, errors = import_pdf(pdf_path, db_session, county)
            total_imported += imported
            total_errors += errors
    finally:
        db_session.close()
    
    print(f"\nImport complete: {total_imported} monuments imported from {len(pdf_files)} PDFs, {total_errors} errors")


if __name__ == "__main__":
    main()

