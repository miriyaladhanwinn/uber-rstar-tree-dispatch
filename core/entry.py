"""
REntry - Unified Leaf and Internal Entry Specification for the R*-Tree in Uber.

In this unified architecture, leaf entries natively encapsulate driver telemetry tuples
directly inside the spatial index, completely eliminating the need for external hash maps.
"""

import time
import math
from typing import Optional, Tuple, Any
from core.geometry import Rectangle


class REntry:
    """
    Unified entry in an R*-Tree node.
    - If part of an Internal Node: owns a child pointer and the child's bounding MBR.
    - If part of a Leaf Node: encapsulates full vehicle telemetry (driver_id, status, GPS coords, rating).
    """
    __slots__ = (
        'mbr', 'child', 'driver_id', 'x', 'y', 'status',
        'vehicle_type', 'rating', 'heading', 'speed', 'timestamp'
    )

    def __init__(
        self,
        mbr: Rectangle,
        child: Optional[Any] = None,
        driver_id: Optional[str] = None,
        x: Optional[float] = None,
        y: Optional[float] = None,
        status: str = "AVAILABLE",
        vehicle_type: str = "UberX",
        rating: float = 4.90,
        heading: float = 0.0,
        speed: float = 0.0,
        timestamp: Optional[float] = None
    ):
        self.mbr = mbr
        self.child = child
        self.driver_id = driver_id
        self.x = x
        self.y = y
        self.status = status
        self.vehicle_type = vehicle_type
        self.rating = rating
        self.heading = heading
        self.speed = speed
        self.timestamp = timestamp if timestamp is not None else time.time()

    @classmethod
    def create_leaf_entry(
        cls,
        driver_id: str,
        x: float,
        y: float,
        status: str = "AVAILABLE",
        vehicle_type: str = "UberX",
        rating: float = 4.90,
        heading: float = 0.0,
        speed: float = 0.0
    ) -> 'REntry':
        """Constructs a leaf entry encapsulating a live driver record."""
        point_mbr = Rectangle.from_point(x, y)
        return cls(
            mbr=point_mbr,
            child=None,
            driver_id=driver_id,
            x=x,
            y=y,
            status=status,
            vehicle_type=vehicle_type,
            rating=rating,
            heading=heading,
            speed=speed
        )

    @classmethod
    def create_internal_entry(cls, child_node: Any) -> 'REntry':
        """Constructs an internal entry referencing a child subtree."""
        return cls(
            mbr=child_node.recalculate_mbr(),
            child=child_node
        )

    @property
    def is_leaf_entry(self) -> bool:
        """True if this entry represents a vehicle point leaf record."""
        return self.child is None and self.driver_id is not None

    def distance_to(self, px: float, py: float) -> float:
        """Euclidean distance from query point to driver coordinate."""
        if self.x is None or self.y is None:
            return self.mbr.min_dist(px, py)
        return math.hypot(self.x - px, self.y - py)

    def distance_sq_to(self, px: float, py: float) -> float:
        """Squared Euclidean distance from query point to driver coordinate."""
        if self.x is None or self.y is None:
            return self.mbr.min_dist_sq(px, py)
        dx = self.x - px
        dy = self.y - py
        return dx * dx + dy * dy

    def to_driver_dict(self) -> dict:
        """Serializes leaf record for UI rendering and telemetry display."""
        return {
            "driver_id": self.driver_id,
            "x": self.x,
            "y": self.y,
            "status": self.status,
            "vehicle_type": self.vehicle_type,
            "rating": self.rating,
            "heading": self.heading,
            "speed": self.speed,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        if self.is_leaf_entry:
            return f"REntry[Driver: {self.driver_id} ({self.x:.1f}, {self.y:.1f}) | {self.status}]"
        return f"REntry[Subtree Child MBR: {self.mbr}]"
