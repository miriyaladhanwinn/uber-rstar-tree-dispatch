"""
Hi-Fi Theme Constants and Styling for the Uber R*-Tree Command Center.
Obsidian Dark Mode inspired by Kepler.gl, Uber Hex, and professional GIS tooling.
"""

# Palette
BG_ROOT = "#0B0F19"         # Ultra-deep obsidian
BG_PANEL = "#111827"        # Charcoal card background
BG_PANEL_ALT = "#161F30"    # Elevated container surface
BG_CANVAS = "#070A10"       # Pitch black map canvas
BG_INPUT = "#1F2937"        # Input box fill
BORDER_COLOR = "#2D3748"    # Subtle borders
BORDER_FOCUS = "#3B82F6"    # Active focus border

TEXT_PRIMARY = "#F9FAFB"    # Crisp pure white
TEXT_SECONDARY = "#9CA3AF"  # Soft slate
TEXT_MUTED = "#6B7280"      # Muted labels
TEXT_ACCENT = "#38BDF8"     # Electric sky blue

# Dynamic Status Accent Colors
COLOR_AVAILABLE = "#10B981"  # Emerald Green (Driver Available)
COLOR_DISPATCHED = "#F59E0B" # Amber Gold (Driver En Route)
COLOR_ON_TRIP = "#A855F7"    # Electric Purple (Passenger On Board)
COLOR_OFFLINE = "#6B7280"    # Dim Gray
COLOR_QUERY = "#00F0FF"      # Neon Cyan (Rider Query / Pickup)
COLOR_PRUNED = "#EF4444"     # Crimson Red (Pruned MBR / Out of radius)
COLOR_DROPOFF = "#EC4899"    # Magenta Pink (Trip Dropoff)

# MBR Level Colors
MBR_LEVEL_COLORS = {
    0: "#14B8A6",  # Leaf Level (Teal)
    1: "#06B6D4",  # Internal Level 1 (Cyan)
    2: "#8B5CF6",  # Internal Level 2 (Royal Purple)
    3: "#F59E0B",  # High-level Root (Amber Gold)
}

# Typography
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SUBTITLE = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI", 9, "bold")
FONT_CODE = ("Consolas", 9)
FONT_STAT_VAL = ("Segoe UI", 13, "bold")
FONT_STAT_LBL = ("Segoe UI", 8)
