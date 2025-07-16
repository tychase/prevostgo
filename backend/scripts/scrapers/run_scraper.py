#!/usr/bin/env python3
"""
Quick script to run the scraper and populate the database
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the scraper
from scraper_final_v2 import main

if __name__ == "__main__":
    print("Running Prevost inventory scraper...")
    print("This will populate the database with coaches from prevost-stuff.com")
    print("-" * 60)
    
    try:
        main()
        print("\n✓ Scraper completed successfully!")
        print("\nYou can now refresh your browser to see the coaches.")
    except Exception as e:
        print(f"\n✗ Error running scraper: {e}")
        import traceback
        traceback.print_exc()
