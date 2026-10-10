"""
RoadNetwork - Realistic Metropolitan Transit Corridors & Road Grid Architecture.
"""

from typing import List, Tuple


class RoadSegment:
    """Represents a city street or transit corridor."""
    __slots__ = ('name', 'start', 'end', 'lanes', 'is_highway')

    def __init__(self, name: str, start: Tuple[float, float], end: Tuple[float, float], lanes: int = 2, is_highway: bool = False):
        self.name = name
        self.start = start
        self.end = end
        self.lanes = lanes
        self.is_highway = is_highway


class RoadNetwork:
    """Generates metropolitan road network for realistic vehicle navigation."""

    @staticmethod
    def generate_metropolitan_grid(width: float = 860.0, height: float = 640.0) -> List[RoadSegment]:
        roads: List[RoadSegment] = []

        # Major Highways (Thick arteries)
        roads.append(RoadSegment("Interstate 101 Northbound", (100.0, 0.0), (100.0, height), lanes=4, is_highway=True))
        roads.append(RoadSegment("Interstate 101 Southbound", (115.0, 0.0), (115.0, height), lanes=4, is_highway=True))
        roads.append(RoadSegment("Expressway 280 Eastbound", (0.0, 300.0), (width, 300.0), lanes=4, is_highway=True))
        roads.append(RoadSegment("Expressway 280 Westbound", (0.0, 315.0), (width, 315.0), lanes=4, is_highway=True))

        # Diagonal Metropolitan Boulevards
        roads.append(RoadSegment("Grand Diagonal Parkway", (40.0, 40.0), (width - 40.0, height - 40.0), lanes=3, is_highway=False))
        roads.append(RoadSegment("Riverside Drive", (width - 40.0, 40.0), (40.0, height - 40.0), lanes=3, is_highway=False))

        # Avenues (Vertical)
        for x in range(200, int(width), 120):
            roads.append(RoadSegment(f"Avenue {x // 100}", (float(x), 0.0), (float(x), height), lanes=2, is_highway=False))

        # Streets (Horizontal)
        for y in range(100, int(height), 100):
            if abs(y - 300) > 30:  # Skip highway overlap
                roads.append(RoadSegment(f"Street {y // 50}", (0.0, float(y)), (width, float(y)), lanes=2, is_highway=False))

        return roads
