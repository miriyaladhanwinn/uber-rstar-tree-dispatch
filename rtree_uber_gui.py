"""
Uber R*-Tree Dispatch GUI Runner.
Executable script for live demonstration during DSA Lab Evaluation.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import launch

if __name__ == "__main__":
    launch()
