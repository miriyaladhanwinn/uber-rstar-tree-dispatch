"""
SurgeEngine - Real-Time Dynamic Spatial Surge Pricing & Density Heatmap Model.

Calculates dynamic surge multipliers (1.0x to 3.8x) directly from R*-Tree
node density metrics and real-time demand hotspots without external databases.
"""

from typing import List, Dict, Tuple, Any
from core.geometry import Rectangle
from core.rstar_tree import RStarTree


class SurgeZone:
    """Represents a spatial surge pricing zone."""
    __slots__ = ('zone_id', 'mbr', 'multiplier', 'supply', 'demand', 'label')

    def __init__(self, zone_id: str, mbr: Rectangle, multiplier: float, supply: int, demand: int, label: str):
        self.zone_id = zone_id
        self.mbr = mbr
        self.multiplier = multiplier
        self.supply = supply
        self.demand = demand
        self.label = label


class SurgeEngine:
    """
    Evaluates localized vehicle density vs ride request volume to establish
    fair, real-time surge pricing multipliers across metropolitan sectors.
    """

    def __init__(self, tree: RStarTree, map_width: float = 860.0, map_height: float = 640.0):
        self.tree = tree
        self.map_width = map_width
        self.map_height = map_height
        self.active_zones: List[SurgeZone] = []
        self.demand_hotspots: List[Tuple[float, float, int]] = []  # (x, y, weight)

    def register_ride_request(self, qx: float, qy: float, weight: int = 1) -> None:
        """Records rider trip demand origin."""
        self.demand_hotspots.append((qx, qy, weight))
        if len(self.demand_hotspots) > 200:
            self.demand_hotspots.pop(0)

    def recalculate_surge_zones(self, grid_divisions: int = 4) -> List[SurgeZone]:
        """
        Partitions map into geographic grid sectors and calculates localized surge multipliers
        by querying the R*-Tree for available vehicle supply.
        """
        self.active_zones.clear()
        step_x = self.map_width / grid_divisions
        step_y = self.map_height / grid_divisions

        zone_idx = 1
        for i in range(grid_divisions):
            for j in range(grid_divisions):
                x1 = i * step_x
                y1 = j * step_y
                x2 = x1 + step_x
                y2 = y1 + step_y
                mbr = Rectangle(x1, y1, x2, y2)

                # Query R*-Tree for live driver supply in this MBR in O(log N)
                supply = self.tree.count_drivers_in_mbr(mbr, available_only=True)

                # Count demand in this MBR
                demand = sum(
                    w for hx, hy, w in self.demand_hotspots
                    if mbr.contains_point(hx, hy)
                ) + 1  # Base demand factor

                # Calculate surge multiplier
                ratio = demand / max(1, supply)
                if ratio > 2.5:
                    multiplier = min(3.8, round(1.0 + (ratio - 1.0) * 0.45, 1))
                    label = "EXTREME SURGE"
                elif ratio > 1.4:
                    multiplier = round(1.0 + (ratio - 1.0) * 0.35, 1)
                    label = "MODERATE SURGE"
                else:
                    multiplier = 1.0
                    label = "STANDARD RATE"

                self.active_zones.append(
                    SurgeZone(f"ZONE_{zone_idx}", mbr, multiplier, supply, demand, label)
                )
                zone_idx += 1

        return self.active_zones

    def get_surge_at(self, x: float, y: float) -> Tuple[float, str]:
        """Returns the surge multiplier applicable at query coordinate (x, y)."""
        for zone in self.active_zones:
            if zone.mbr.contains_point(x, y):
                return zone.multiplier, zone.label
        return 1.0, "STANDARD RATE"
