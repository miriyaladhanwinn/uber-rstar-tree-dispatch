"""
RNode - Node representation for the Hierarchical Multidimensional R*-Tree.
"""

from typing import List, Optional, Tuple
from core.geometry import Rectangle
from core.entry import REntry


class RNode:
    """
    R*-Tree Node representing an internal branch or a leaf page.
    Maintains [MIN_ENTRIES, MAX_ENTRIES] occupancy bounds.
    """
    __slots__ = ('is_leaf', 'entries', 'parent', 'level', '_cached_mbr')

    def __init__(self, is_leaf: bool = True, parent: Optional['RNode'] = None, level: int = 0):
        self.is_leaf = is_leaf
        self.entries: List[REntry] = []
        self.parent = parent
        self.level = level
        self._cached_mbr: Optional[Rectangle] = None

    def recalculate_mbr(self) -> Optional[Rectangle]:
        """
        Recomputes the tightest Minimum Bounding Rectangle that encloses all child entries.
        """
        if not self.entries:
            self._cached_mbr = None
            return None

        current = self.entries[0].mbr
        for e in self.entries[1:]:
            current = current.union(e.mbr)

        self._cached_mbr = current
        return current

    @property
    def mbr(self) -> Optional[Rectangle]:
        if self._cached_mbr is None:
            return self.recalculate_mbr()
        return self._cached_mbr

    def invalidate_mbr(self) -> None:
        """Flags cached MBR as dirty."""
        self._cached_mbr = None

    def add_entry(self, entry: REntry) -> None:
        """Appends entry to node and clears cached MBR."""
        self.entries.append(entry)
        self.invalidate_mbr()

    def remove_entry(self, entry: REntry) -> bool:
        """Removes specified entry and clears cached MBR."""
        if entry in self.entries:
            self.entries.remove(entry)
            self.invalidate_mbr()
            return True
        return False

    def is_overflow(self, max_entries: int) -> bool:
        """True if node occupancy exceeds maximum branch limit."""
        return len(self.entries) > max_entries

    def is_underflow(self, min_entries: int) -> bool:
        """True if node occupancy drops below minimum bound (50% rule)."""
        return len(self.entries) < min_entries

    def get_sorted_entries_by_dist(self, px: float, py: float) -> List[Tuple[float, REntry]]:
        """
        Sorts entries by ascending Euclidean lower-bound distance to query point (px, py).
        Essential for Best-First Branch-and-Bound k-NN ranking.
        """
        decorated = []
        for e in self.entries:
            dist_sq = e.distance_sq_to(px, py)
            decorated.append((dist_sq, e))
        decorated.sort(key=lambda item: item[0])
        return decorated

    def __repr__(self) -> str:
        kind = "LeafNode" if self.is_leaf else "InternalNode"
        return f"{kind}(Level={self.level}, Entries={len(self.entries)}, MBR={self.mbr})"
