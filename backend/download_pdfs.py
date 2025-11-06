#!/usr/bin/env python3
"""Download PDF files from URLs and rename them to county names."""

import sys
import re
from pathlib import Path
import requests

# Mapping of Romanian county codes to full names
COUNTY_NAMES = {
    'AB': 'Alba',
    'AR': 'Arad',
    'AG': 'Argeș',
    'BC': 'Bacău',
    'BH': 'Bihor',
    'BN': 'Bistrița-Năsăud',
    'BT': 'Botoșani',
    'BR': 'Brăila',
    'BV': 'Brașov',
    'B': 'București',
    'BZ': 'Buzău',
    'CL': 'Călărași',
    'CS': 'Caraș-Severin',
    'CJ': 'Cluj',
    'CT': 'Constanța',
    'CV': 'Covasna',
    'DB': 'Dâmbovița',
    'DJ': 'Dolj',
    'GL': 'Galați',
    'GR': 'Giurgiu',
    'GJ': 'Gorj',
    'HR': 'Harghita',
    'HD': 'Hunedoara',
    'IL': 'Ialomița',
    'IS': 'Iași',
    'IF': 'Ilfov',
    'MM': 'Maramureș',
    'MH': 'Mehedinți',
    'MS': 'Mureș',
    'NT': 'Neamț',
    'OT': 'Olt',
    'PH': 'Prahova',
    'SJ': 'Sălaj',
    'SM': 'Satu Mare',
    'SB': 'Sibiu',
    'SV': 'Suceava',
    'TR': 'Teleorman',
    'TM': 'Timiș',
    'TL': 'Tulcea',
    'VL': 'Vâlcea',
    'VS': 'Vaslui',
    'VN': 'Vrancea',
}

URLS = [
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBNml2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--fca43e566240bd75700983792ac6ba634c87c625/LMI-AB.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBNm12Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--01c11b785de56992f8d6b4eb15ead601581ee998/LMI-AR.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBNnF2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--3b4426b17ad44a0424b22ddb692af7843e08f02a/LMI-AG.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBNjJ2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--17b6ced1d05bc40aecdfaad8191f6b38f4f79a79/LMI-BC.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBN0t2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--95e148618ad1ca9a4fddc43b97fb3ca3fcdf9da2/LMI-BH.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBN1N2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--a3bb66fdc2a70955f09b0c590a089af1aaffa92e/LMI-BN.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBN2F2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--77fdb30d7eed2cc08c8af867f586e4bc53c4e986/LMI-BT.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBN2V2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--9ad9bf961515c7755fc8988756a58c1766fde3db/LMI-BR.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBN2l2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--fdd17c75cb101abdbdd2969a599e87572ff1818d/LMI-BV.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBN3F2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--30977891dee273f02a7ead7d5ac7bbcc898f9a8d/LMI-B.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBN3V2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--e333148a4b27b03d734a8ca7a60c7879c058f64d/LMI-BZ.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBN3l2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--454c1b7c16ceac0fa9d1ece59fb9765efa77ee1e/LMI-CL.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBNzJ2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--f285bf1aacc413069ca111ca0d4e03800ee0d12c/LMI-CS.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBNzZ2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--2954b48c4ff917343e3ae6dba0782137b02c5611/LMI-CJ.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOEN2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--bc5c71945089c137d9e534a0369ead8da8f8b8ce/LMI-CT.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOEd2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--dc043f325dc0911b65ba62defd38569dcf24e446/LMI-CV.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOEt2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--b10f7c60da10cd2a8b0a947d02a676898a41f4fc/LMI-DB.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOGV2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--5738919d76ca099786224ea173221c771d2bbafd/LMI-DJ.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOGl2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--52564c4014c9dd56c64ac391f7224af78d6660ac/LMI-GL.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOG12Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--da331c774d1b30cdf1d5f948b013f760a54861c8/LMI-GR.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOHF2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--44d6e8d6fb10733df329c334ef24e3a03bfcc5c9/LMI-GJ.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOHV2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--17d89fe40bb65d579cc2d9c5a771f4439c756899/LMI-HR.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOHl2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--31a5c208a5dbd1fc0b778cfc632a0ec4ecc06aa6/LMI-HD.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBODJ2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--5f1d5ea7dde9509ee6c3fdcf5de56cba4191ec83/LMI-IL.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBODZ2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--e85d5fbd0f63d5fa918c2577ad6b7b4d1c6308d4/LMI-IS.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOCt2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--5f33f2ac5b13c0d3b6f225e57941345d60eee7a3/LMI-IF.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOUd2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--8aab2465ef8899f2d696d1a96e73650890df9387/LMI-MM.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOUt2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--4ea4757a86ddf6148bf7b11a79b1a020fc467dc5/LMI-MH.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOU92Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--933214a2ee2142c1ba809f5d6a003b7258fd8a0b/LMI-MS.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOVN2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--3f5399e917e51ef08aa92ddc931222f78b9d3681/LMI-NT.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOVd2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--229aef7d9b9f0b8e6263fa102b1ca57e6f95554f/LMI-OT.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOWF2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--444b7a665a6d433d83ee91f0d3919d3d84069498/LMI-PH.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOWl2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--1e568dbdac38455e0321603f09c43510347d0a0b/LMI-SJ.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOW12Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--7173662719b2def9c4144d30e3afa6fbbb5ea90f/LMI-SM.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOXF2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--a80208b438deecdbe6645e76015ba34d2f20157d/LMI-SB.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOXV2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--20ed2d69ace77f0d2624a9773a2deabd4b57301c/LMI-SV.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOTJ2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--1f91f78100080590b292029bfb44967d3e47f177/LMI-TR.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOTZ2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--3b0c5a177f69396240ecd71ffcda6b63ce8519ae/LMI-TM.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOSt2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--926957b84fc6c39e4f4f75c998af6a2d8d8bc449/LMI-TL.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBK0N2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--2dda035214e555b41c1a1b0c8b3cc7e1c950bdbb/LMI-VL.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBK0d2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--02f2b184a1777a2b7b9550ff783087fa2efbca72/LMI-VS.pdf",
    "https://patrimoniu.eventya.net/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBK0t2Q0E9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--6cc5c7a574aa6982082b86b657e1f9423a002d48/LMI-VN.pdf",
]


def extract_county_code(url: str) -> str:
    """Extract county code from URL (e.g., 'AB' from 'LMI-AB.pdf')."""
    match = re.search(r'LMI-([A-Z]+)\.pdf', url)
    if match:
        return match.group(1)
    return None


def clear_pdfs_folder(pdfs_dir: Path):
    """Remove all files from the pdfs folder."""
    if pdfs_dir.exists():
        for file in pdfs_dir.iterdir():
            if file.is_file():
                file.unlink()
                print(f"Removed: {file.name}")
    else:
        pdfs_dir.mkdir(parents=True, exist_ok=True)
    print(f"Cleared pdfs folder: {pdfs_dir}")


def download_pdf(url: str, output_path: Path):
    """Download a PDF from URL and save to output_path."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {output_path.name}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def main():
    script_dir = Path(__file__).parent
    pdfs_dir = script_dir / "pdfs"
    
    # Clear pdfs folder
    print("Clearing pdfs folder...")
    clear_pdfs_folder(pdfs_dir)
    print()
    
    # Download each PDF
    print(f"Downloading {len(URLS)} PDFs...")
    success_count = 0
    failed_count = 0
    
    for url in URLS:
        county_code = extract_county_code(url)
        if not county_code:
            print(f"Warning: Could not extract county code from {url}")
            failed_count += 1
            continue
        
        county_name = COUNTY_NAMES.get(county_code)
        if not county_name:
            print(f"Warning: Unknown county code: {county_code}")
            failed_count += 1
            continue
        
        output_path = pdfs_dir / f"{county_name}.pdf"
        
        if download_pdf(url, output_path):
            success_count += 1
        else:
            failed_count += 1
    
    print()
    print(f"Download complete: {success_count} succeeded, {failed_count} failed")


if __name__ == "__main__":
    main()

