#!/usr/bin/env python3
"""Simple script to test DB2 driver availability."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("Testing DB2 Driver Availability...\n")
print("=" * 50)

# Try importing the db2_checker module
try:
    from db2_checker import get_db2_driver_info, is_db2_available
    
    driver_info = get_db2_driver_info()
    
    print(f"\nDriver Available: {driver_info['available']}")
    print(f"Driver Type: {driver_info['driver_type'] or 'None'}")
    print(f"Driver Module: {driver_info['driver_module'] or 'None'}")
    
    if not driver_info['available']:
        print("\n" + "=" * 50)
        print("No DB2 driver found!")
        print("=" * 50)
        print("\nPlease install one of the following:\n")
        print("Option 1 - pyodbc (RECOMMENDED - easier to install):")
        print("  pip install pyodbc")
        print("\nOption 2 - ibm_db (requires IBM Data Server Driver):")
        print("  1. Install IBM Data Server Driver from IBM website")
        print("  2. pip install ibm_db")
        print("\nSee INSTALL_DB2_DRIVERS.md for detailed instructions.")
        sys.exit(1)
    else:
        print("\n" + "=" * 50)
        print(f"✓ DB2 driver ({driver_info['driver_type']}) is ready to use!")
        print("=" * 50)
        sys.exit(0)
        
except Exception as e:
    print(f"\nError: {e}")
    sys.exit(1)
