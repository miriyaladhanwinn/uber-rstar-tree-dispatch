"""
Main Entry Point for the Uber R*-Tree Fleet Dispatch System.
Amrita Vishwa Vidyapeetham - Department of CSE
DSA Lab Evaluation 3
"""

import sys
import os

# Ensure current directory is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import launch

if __name__ == "__main__":
    launch()
