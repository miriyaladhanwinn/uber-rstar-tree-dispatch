"""
Hilbert Space-Filling Curve & Bulk Loading Algorithm for R*-Tree.

Enables instant initialization of massive vehicle fleets (10,000+ drivers)
with optimal spatial locality, minimal MBR overlap, and deterministic balance.
"""

import math
from typing import List, Tuple
from core.geometry import Rectangle
from core.entry import REntry
from core.node import RNode
from core.rstar_tree import RStarTree


def hilbert_xy_to_d(n: int, x: int, y: int) -> int:
    """
    Converts 2D coordinates (x, y) to a 1D Hilbert curve distance d.
    n must be a power of 2 representing grid resolution.
    """
    d = 0
    s = n // 2
    while s > 0:
        rx = 1 if (x & s) > 0 else 0
        ry = 1 if (y & s) > 0 else 0
        d += s * s * ((3 * rx) ^ ry)
        
        # Rotate quadrant
        if ry == 0:
            if rx == 1:
                x = (s - 1) - x
                y = (s - 1) - y
            # Swap x and y
            x, y = y, x
        s //= 2
    return d


class HilbertBulkLoader:
    """
    Implements Kamel & Faloutsos (1994) Hilbert R-Tree bulk loading.
    Orders entries along the 1D Hilbert fractal curve and packs nodes bottom-up.
    """

    @staticmethod
    def bulk_load(
        tree: RStarTree,
        entries: List[REntry],
        grid_order: int = 16
    ) -> RStarTree:
        """
        Packs entries into R*-Tree with maximum space utilization and zero dead space.
        """
        if not entries:
            return tree

        grid_size = 1 << grid_order  # e.g., 65536 for 16-bit

        # Find fleet bounding box to normalize coordinates into Hilbert grid
        min_x = min(e.x for e in entries)
        max_x = max(e.x for e in entries)
        min_y = min(e.y for e in entries)
        max_y = max(e.y for e in entries)

        span_x = max(1.0, max_x - min_x)
        span_y = max(1.0, max_y - min_y)

        # Decorate entries with Hilbert index
        decorated = []
        for e in entries:
            norm_x = int(((e.x - min_x) / span_x) * (grid_size - 1))
            norm_y = int(((e.y - min_y) / span_y) * (grid_size - 1))
            h_val = hilbert_xy_to_d(grid_size, norm_x, norm_y)
            decorated.append((h_val, e))

        # Sort entries along Hilbert space-filling curve
        decorated.sort(key=lambda item: item[0])
        sorted_entries = [e for _, e in decorated]

        # Pack leaf nodes
        leaf_nodes: List[RNode] = []
        max_entries = tree.max_entries

        for i in range(0, len(sorted_entries), max_entries):
            chunk = sorted_entries[i:i + max_entries]
            node = RNode(is_leaf=True, parent=None, level=0)
            for entry in chunk:
                node.add_entry(entry)
            node.recalculate_mbr()
            leaf_nodes.append(node)

        # Build internal levels bottom-up
        current_level_nodes = leaf_nodes
        level = 1

        while len(current_level_nodes) > 1:
            next_level_nodes: List[RNode] = []
            for i in range(0, len(current_level_nodes), max_entries):
                chunk = current_level_nodes[i:i + max_entries]
                parent = RNode(is_leaf=False, parent=None, level=level)
                for child in chunk:
                    child.parent = parent
                    parent.add_entry(REntry.create_internal_entry(child))
                parent.recalculate_mbr()
                next_level_nodes.append(parent)
            current_level_nodes = next_level_nodes
            level += 1

        # Set tree root
        tree.root = current_level_nodes[0]
        tree.total_vehicles = len(entries)
        return tree
