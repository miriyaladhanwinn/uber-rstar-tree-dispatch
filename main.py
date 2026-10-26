"""
Main Entry Point for the Uber R*-Tree Fleet Dispatch System.
Amrita Vishwa Vidyapeetham - Department of CSE
DSA Lab Evaluation 3
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    if len(sys.argv) > 1 and any(arg in sys.argv[1].lower() for arg in ("--test", "-t", "--cli", "--tests", "test")):
        from run_tests import run_all_faculty_tests, interactive_faculty_menu
        run_all_faculty_tests()
        if "--auto" not in sys.argv and "-a" not in sys.argv and "--batch" not in sys.argv:
            interactive_faculty_menu()
    else:
        from gui.app import launch
        launch()
