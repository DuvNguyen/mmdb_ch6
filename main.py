"""
main.py
=======
Demo tat ca 3 chuc nang cua bai tap Chuong 6.

Luong hoat dong:
  1. CreateIndex  -> xay dung DocTable + TermTable
  2. Luu index    -> index.json
  3. Find(word)   -> tim 1 tu
  4. FindWordFile -> tim nhieu tu tu file
"""

import sys
import os

# Set path to current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import run

def main():
    print("=" * 60)
    print("  INVERTED INDEX - Chuong 6 GUI")
    print("=" * 60)
    
    # Launch GUI
    run()

if __name__ == "__main__":
    main()
