"""
Geometry primitives and Minimum Bounding Rectangle (MBR) calculations
for the R*-Tree Spatial Dispatch Architecture.
"""

import math
from typing import Optional, Tuple


class Rectangle:
    """
    Represents a 2D Minimum Bounding Rectangle (MBR) defined by
    [min_x, min_y, max_x, max_y].
    """
    __slots__ = ('min_x', 'min_y', 'max_x', 'max_y')

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        self.min_x = float(min(min_x, max_x))
        self.min_y = float(min(min_y, max_y))
        self.max_x = float(max(min_x, max_x))
        self.max_y = float(max(min_y, max_y))

    @classmethod
    def from_point(cls, x: float, y: float) -> 'Rectangle':
        """Creates a zero-area point rectangle for vehicle coordinates."""
        return cls(x, y, x, y)

    @property
    def width(self) -> float:
        return max(0.0, self.max_x - self.min_x)

    @property
    def height(self) -> float:
        return max(0.0, self.max_y - self.min_y)

    def area(self) -> float:
        """Calculates 2D area of the bounding box."""
        return self.width * self.height

    def margin(self) -> float:
        """Calculates semi-perimeter (sum of width and height) used in R*-tree split heuristics."""
        return self.width + self.height

    def perimeter(self) -> float:
        """Calculates full perimeter of the bounding box."""
        return 2.0 * (self.width + self.height)

    def union(self, other: Optional['Rectangle']) -> 'Rectangle':
        """Returns the minimal enclosing bounding box of this rectangle and another."""
        if other is None:
            return Rectangle(self.min_x, self.min_y, self.max_x, self.max_y)
        return Rectangle(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y)
        )

    def enlargement(self, other: 'Rectangle') -> float:
        """
        Area increase required to enclose 'other'.
        Key heuristic in ChooseSubtree / ChooseLeaf to minimize dead space.
        """
        union_box = self.union(other)
        return union_box.area() - self.area()

    def intersects(self, other: 'Rectangle') -> bool:
        """Determines if this rectangle overlaps with another rectangle."""
        return not (
            self.max_x < other.min_x or
            self.min_x > other.max_x or
            self.max_y < other.min_y or
            self.min_y > other.max_y
        )

    def contains_point(self, px: float, py: float) -> bool:
        """Checks if point (px, py) lies inside or on the boundary of the MBR."""
        return self.min_x <= px <= self.max_x and self.min_y <= py <= self.max_y

    def min_dist_sq(self, px: float, py: float) -> float:
        """
        Calculates the strict squared Euclidean lower bound (MINDIST) from
        query point (px, py) to this MBR.
        
        MINDIST Theorem (Roussopoulos et al., 1995):
        If min_dist_sq(query, MBR) > radius^2, NO point inside the MBR can
        possibly fall within the search radius. The entire subtree is safely pruned.
        """
        dx = 0.0
        if px < self.min_x:
            dx = self.min_x - px
        elif px > self.max_x:
            dx = px - self.max_x

        dy = 0.0
        if py < self.min_y:
            dy = self.min_y - py
        elif py > self.max_y:
            dy = py - self.max_y

        return dx * dx + dy * dy

    def min_dist(self, px: float, py: float) -> float:
        """Euclidean distance lower bound (MINDIST) to the query point."""
        return math.sqrt(self.min_dist_sq(px, py))

    def center(self) -> Tuple[float, float]:
        """Returns the centroid coordinate of the MBR."""
        return ((self.min_x + self.max_x) / 2.0, (self.min_y + self.max_y) / 2.0)

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.min_x, self.min_y, self.max_x, self.max_y)

    def __repr__(self) -> str:
        return f"MBR({self.min_x:.1f}, {self.min_y:.1f}, {self.max_x:.1f}, {self.max_y:.1f})"
