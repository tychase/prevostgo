"""
Script to clean up old scraper files and identify the best one
"""
import os

scrapers_to_delete = [
    'scraper_enhanced.py',
    'scraper_final.py',  # Keep v2 instead
    'scraper_fixed.py',
    'scraper_minimal.py',
    'scraper_simple.py',
    'test_scraper.py',
    'add_sample_data.py',  # We don't want sample data
    'add_sample_prices.py',  # We don't want sample data
    'diagnose_scraper.py',  # Diagnostic tool, not needed anymore
    'fetch_prices.py',  # Old price fetcher
    'fix_converters.py',  # One-time fix script
]

# Keep these files:
# - scraper_final_v2.py (the best scraper)
# - app/services/scraper.py (the integrated FastAPI scraper)
# - SCRAPER_GUIDE.md and SCRAPER_SUMMARY.md (documentation)

print("Files to delete:")
for file in scrapers_to_delete:
    if os.path.exists(file):
        print(f"  - {file}")
    else:
        print(f"  - {file} (not found)")

print("\nFiles to keep:")
print("  - scraper_final_v2.py (best standalone scraper)")
print("  - app/services/scraper.py (FastAPI integrated)")
print("  - SCRAPER_GUIDE.md")
print("  - SCRAPER_SUMMARY.md")

# Don't actually delete yet - just show what would be deleted
print("\nTo delete these files, run this script with the --delete flag")
print("Example: python cleanup_scrapers.py --delete")

import sys
if '--delete' in sys.argv:
    print("\nDeleting files...")
    for file in scrapers_to_delete:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Deleted: {file}")
    print("\nCleanup complete!")
else:
    print("\nNo files deleted. Run with --delete to actually remove files.")
