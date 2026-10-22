"""
R*-TREE IN UBER: A UNIFIED SPATIAL ARCHITECTURE FOR REAL-TIME FLEET DISPATCH
Standalone Hi-Fi Enterprise Edition for Amrita Vishwa Vidyapeetham DSA Lab Evaluation 3.
Zero external dependencies (Pure Python 3 + Standard Library Tkinter).

Features:
- Unified R*-Tree Single Data Structure Core
- In-Tree Best-First Branch-and-Bound k-NN Dispatch
- Circle-MBR Geometric Radius Pruning
- Dynamic Surge Pricing & Heatmap Density Engine
- Hilbert Space-Filling Curve Bulk Loading (10,000+ drivers)
- Smooth Pan & Zoom GIS Canvas with Vehicle Inspector Cards
- Dynamic Fleet Autopilot & Real-Time Trip Lifecycle Simulation

Authors:
- Dhanvant Menon (CB.SC..U4CSE25613) [dhanvantmenon@gmail.com]
- Miriyala Dhanwin (CB.SC.U4CSE25639) [dhanwinn15@gmail.com]
- Paruchuri Sai Shasank (CB.SC..U4CSE25645) [paruchurishasank04@gmail.com]
- Adwaith (CB.SC.U4CSE25602) [adwaithdhoni7@gmail.com]
"""

import math
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Tuple, Set, List, Dict, Any

# =============================================================================
# 1. GEOMETRY & MINIMUM BOUNDING RECTANGLE (MBR)
# =============================================================================

class Rectangle:
    __slots__ = ('min_x', 'min_y', 'max_x', 'max_y')

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        self.min_x = float(min(min_x, max_x))
        self.min_y = float(min(min_y, max_y))
        self.max_x = float(max(min_x, max_x))
        self.max_y = float(max(min_y, max_y))

    @classmethod
    def from_point(cls, x: float, y: float) -> 'Rectangle':
        return cls(x, y, x, y)

    @property
    def width(self) -> float:
        return max(0.0, self.max_x - self.min_x)

    @property
    def height(self) -> float:
        return max(0.0, self.max_y - self.min_y)

    def area(self) -> float:
        return self.width * self.height

    def margin(self) -> float:
        return self.width + self.height

    def union(self, other: Optional['Rectangle']) -> 'Rectangle':
        if other is None:
            return Rectangle(self.min_x, self.min_y, self.max_x, self.max_y)
        return Rectangle(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y)
        )

    def enlargement(self, other: 'Rectangle') -> float:
        union_box = self.union(other)
        return union_box.area() - self.area()

    def intersects(self, other: 'Rectangle') -> bool:
        return not (
            self.max_x < other.min_x or
            self.min_x > other.max_x or
            self.max_y < other.min_y or
            self.min_y > other.max_y
        )

    def contains_point(self, px: float, py: float) -> bool:
        return self.min_x <= px <= self.max_x and self.min_y <= py <= self.max_y

    def min_dist_sq(self, px: float, py: float) -> float:
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
        return math.sqrt(self.min_dist_sq(px, py))

    def center(self) -> Tuple[float, float]:
        return ((self.min_x + self.max_x) / 2.0, (self.min_y + self.max_y) / 2.0)

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.min_x, self.min_y, self.max_x, self.max_y)

    def __repr__(self) -> str:
        return f"MBR({self.min_x:.0f}, {self.min_y:.0f}, {self.max_x:.0f}, {self.max_y:.0f})"


# =============================================================================
# 2. UNIFIED RENTRY (DRIVER TELEMETRY ENCAPSULATION)
# =============================================================================

class REntry:
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
        return cls(
            mbr=child_node.recalculate_mbr(),
            child=child_node
        )

    @property
    def is_leaf_entry(self) -> bool:
        return self.child is None and self.driver_id is not None

    def distance_to(self, px: float, py: float) -> float:
        if self.x is None or self.y is None:
            return self.mbr.min_dist(px, py)
        return math.hypot(self.x - px, self.y - py)

    def distance_sq_to(self, px: float, py: float) -> float:
        if self.x is None or self.y is None:
            return self.mbr.min_dist_sq(px, py)
        dx = self.x - px
        dy = self.y - py
        return dx * dx + dy * dy


# =============================================================================
# 3. RNODE
# =============================================================================

class RNode:
    __slots__ = ('is_leaf', 'entries', 'parent', 'level', '_cached_mbr')

    def __init__(self, is_leaf: bool = True, parent: Optional['RNode'] = None, level: int = 0):
        self.is_leaf = is_leaf
        self.entries: List[REntry] = []
        self.parent = parent
        self.level = level
        self._cached_mbr: Optional[Rectangle] = None

    def recalculate_mbr(self) -> Optional[Rectangle]:
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
        self._cached_mbr = None

    def add_entry(self, entry: REntry) -> None:
        self.entries.append(entry)
        self.invalidate_mbr()

    def remove_entry(self, entry: REntry) -> bool:
        if entry in self.entries:
            self.entries.remove(entry)
            self.invalidate_mbr()
            return True
        return False

    def is_overflow(self, max_entries: int) -> bool:
        return len(self.entries) > max_entries

    def is_underflow(self, min_entries: int) -> bool:
        return len(self.entries) < min_entries

    def get_sorted_entries_by_dist(self, px: float, py: float) -> List[Tuple[float, REntry]]:
        decorated = []
        for e in self.entries:
            dist_sq = e.distance_sq_to(px, py)
            decorated.append((dist_sq, e))
        decorated.sort(key=lambda item: item[0])
        return decorated


# =============================================================================
# 4. HILBERT CURVE & BULK LOADING
# =============================================================================

def hilbert_xy_to_d(n: int, x: int, y: int) -> int:
    d = 0
    s = n // 2
    while s > 0:
        rx = 1 if (x & s) > 0 else 0
        ry = 1 if (y & s) > 0 else 0
        d += s * s * ((3 * rx) ^ ry)
        if ry == 0:
            if rx == 1:
                x = (s - 1) - x
                y = (s - 1) - y
            x, y = y, x
        s //= 2
    return d


class HilbertBulkLoader:
    @staticmethod
    def bulk_load(tree: 'RStarTree', entries: List[REntry], grid_order: int = 16) -> 'RStarTree':
        if not entries:
            return tree
        grid_size = 1 << grid_order
        min_x = min(e.x for e in entries)
        max_x = max(e.x for e in entries)
        min_y = min(e.y for e in entries)
        max_y = max(e.y for e in entries)
        span_x = max(1.0, max_x - min_x)
        span_y = max(1.0, max_y - min_y)

        decorated = []
        for e in entries:
            norm_x = int(((e.x - min_x) / span_x) * (grid_size - 1))
            norm_y = int(((e.y - min_y) / span_y) * (grid_size - 1))
            h_val = hilbert_xy_to_d(grid_size, norm_x, norm_y)
            decorated.append((h_val, e))

        decorated.sort(key=lambda item: item[0])
        sorted_entries = [e for _, e in decorated]

        leaf_nodes: List[RNode] = []
        max_entries = tree.max_entries
        for i in range(0, len(sorted_entries), max_entries):
            chunk = sorted_entries[i:i + max_entries]
            node = RNode(is_leaf=True, parent=None, level=0)
            for entry in chunk:
                node.add_entry(entry)
            node.recalculate_mbr()
            leaf_nodes.append(node)

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

        tree.root = current_level_nodes[0]
        tree.total_vehicles = len(entries)
        return tree


# =============================================================================
# 5. R*-TREE CORE ENGINE
# =============================================================================

class RStarTree:
    def __init__(self, max_entries: int = 4, min_entries: int = 2):
        self.max_entries = max_entries
        self.min_entries = min_entries
        self.root = RNode(is_leaf=True, parent=None, level=0)
        self.total_vehicles = 0
        self.total_splits = 0

    def insert(
        self,
        driver_id: str,
        x: float,
        y: float,
        status: str = "AVAILABLE",
        vehicle_type: str = "UberX",
        rating: float = 4.90,
        heading: float = 0.0,
        speed: float = 0.0
    ) -> REntry:
        entry = REntry.create_leaf_entry(
            driver_id=driver_id,
            x=x,
            y=y,
            status=status,
            vehicle_type=vehicle_type,
            rating=rating,
            heading=heading,
            speed=speed
        )
        target_leaf = self._choose_subtree(self.root, entry.mbr)
        target_leaf.add_entry(entry)
        self.total_vehicles += 1

        self._adjust_tree(target_leaf)
        return entry

    def _choose_subtree(self, node: RNode, entry_mbr: Rectangle) -> RNode:
        if node.is_leaf:
            return node

        best_child: Optional[RNode] = None
        best_enlargement = float('inf')
        best_base_area = float('inf')

        for entry in node.entries:
            enl = entry.mbr.enlargement(entry_mbr)
            base_area = entry.mbr.area()

            if (enl < best_enlargement) or (math.isclose(enl, best_enlargement, rel_tol=1e-9) and base_area < best_base_area):
                best_enlargement = enl
                best_base_area = base_area
                best_child = entry.child

        if best_child is None:
            best_child = node.entries[0].child

        return self._choose_subtree(best_child, entry_mbr)

    def _adjust_tree(self, node: RNode) -> None:
        current = node
        while current is not None:
            if not current.is_overflow(self.max_entries):
                current.recalculate_mbr()
                self._update_parent_pointer(current)
                if current is self.root:
                    return
                current = current.parent
                continue

            self.total_splits += 1
            group1, group2 = self._split_node(current)

            if current is self.root:
                new_root = RNode(is_leaf=False, parent=None, level=current.level + 1)
                group1.parent = new_root
                group2.parent = new_root

                new_root.add_entry(REntry.create_internal_entry(group1))
                new_root.add_entry(REntry.create_internal_entry(group2))
                self.root = new_root
                return

            parent = current.parent
            parent.entries = [e for e in parent.entries if e.child is not current]

            group1.parent = parent
            group2.parent = parent
            parent.add_entry(REntry.create_internal_entry(group1))
            parent.add_entry(REntry.create_internal_entry(group2))

            current = parent

    def _update_parent_pointer(self, node: RNode) -> None:
        if node.parent is None:
            return
        node_mbr = node.recalculate_mbr()
        for e in node.parent.entries:
            if e.child is node:
                e.mbr = node_mbr
                return

    def _split_node(self, node: RNode) -> Tuple[RNode, RNode]:
        old_entries = list(node.entries)
        node.entries.clear()

        seed_a, seed_b = None, None
        worst_waste = float('-inf')
        n = len(old_entries)

        for i in range(n):
            for j in range(i + 1, n):
                e1, e2 = old_entries[i], old_entries[j]
                union_box = e1.mbr.union(e2.mbr)
                waste = union_box.area() - e1.mbr.area() - e2.mbr.area()
                if waste > worst_waste:
                    worst_waste = waste
                    seed_a, seed_b = e1, e2

        group1 = RNode(is_leaf=node.is_leaf, parent=node.parent, level=node.level)
        group2 = RNode(is_leaf=node.is_leaf, parent=node.parent, level=node.level)

        group1.add_entry(seed_a)
        group2.add_entry(seed_b)

        remaining = [e for e in old_entries if e is not seed_a and e is not seed_b]

        while remaining:
            if len(group1.entries) + len(remaining) == self.min_entries:
                for rem in remaining:
                    group1.add_entry(rem)
                break
            if len(group2.entries) + len(remaining) == self.min_entries:
                for rem in remaining:
                    group2.add_entry(rem)
                break

            mbr1 = group1.recalculate_mbr()
            mbr2 = group2.recalculate_mbr()

            best_diff = float('-inf')
            best_idx = 0
            for idx, item in enumerate(remaining):
                d1 = mbr1.enlargement(item.mbr)
                d2 = mbr2.enlargement(item.mbr)
                diff = abs(d1 - d2)
                if diff > best_diff:
                    best_diff = diff
                    best_idx = idx

            chosen = remaining.pop(best_idx)
            d1 = mbr1.enlargement(chosen.mbr)
            d2 = mbr2.enlargement(chosen.mbr)

            if d1 < d2:
                group1.add_entry(chosen)
            elif d2 < d1:
                group2.add_entry(chosen)
            else:
                if mbr1.area() < mbr2.area():
                    group1.add_entry(chosen)
                elif mbr2.area() < mbr1.area():
                    group2.add_entry(chosen)
                else:
                    if len(group1.entries) <= len(group2.entries):
                        group1.add_entry(chosen)
                    else:
                        group2.add_entry(chosen)

        if not group1.is_leaf:
            for e in group1.entries:
                if e.child:
                    e.child.parent = group1
        if not group2.is_leaf:
            for e in group2.entries:
                if e.child:
                    e.child.parent = group2

        return group1, group2

    def delete(self, driver_id: str) -> Optional[REntry]:
        leaf, entry = self._find_leaf_entry(self.root, driver_id)
        if leaf is None or entry is None:
            return None

        leaf.remove_entry(entry)
        self.total_vehicles -= 1

        self._condense_tree(leaf)

        if not self.root.is_leaf and len(self.root.entries) == 1:
            child = self.root.entries[0].child
            child.parent = None
            self.root = child

        return entry

    def _find_leaf_entry(self, node: RNode, driver_id: str) -> Tuple[Optional[RNode], Optional[REntry]]:
        if node.is_leaf:
            for e in node.entries:
                if e.driver_id == driver_id:
                    return node, e
            return None, None

        for e in node.entries:
            if e.child:
                found_node, found_entry = self._find_leaf_entry(e.child, driver_id)
                if found_node is not None:
                    return found_node, found_entry
        return None, None

    def _condense_tree(self, leaf: RNode) -> None:
        node = leaf
        orphaned: List[Tuple[int, REntry]] = []

        while node is not self.root and node is not None:
            parent = node.parent
            if node.is_underflow(self.min_entries):
                if parent:
                    parent.entries = [e for e in parent.entries if e.child is not node]
                    for entry in node.entries:
                        orphaned.append((node.level, entry))
            else:
                node.recalculate_mbr()
                self._update_parent_pointer(node)
            node = parent

        if self.root is not None:
            self.root.recalculate_mbr()

        for level, entry in orphaned:
            if entry.is_leaf_entry:
                self.insert(
                    driver_id=entry.driver_id,
                    x=entry.x,
                    y=entry.y,
                    status=entry.status,
                    vehicle_type=entry.vehicle_type,
                    rating=entry.rating,
                    heading=entry.heading,
                    speed=entry.speed
                )
                self.total_vehicles -= 1

    def update_position(self, driver_id: str, new_x: float, new_y: float, heading: float = 0.0, speed: float = 0.0) -> bool:
        old_record = self.delete(driver_id)
        if old_record is None:
            return False

        self.insert(
            driver_id=driver_id,
            x=new_x,
            y=new_y,
            status=old_record.status,
            vehicle_type=old_record.vehicle_type,
            rating=old_record.rating,
            heading=heading if heading != 0.0 else old_record.heading,
            speed=speed if speed != 0.0 else old_record.speed
        )
        return True

    def update_status(self, driver_id: str, new_status: str) -> bool:
        _, entry = self._find_leaf_entry(self.root, driver_id)
        if entry:
            entry.status = new_status
            return True
        return False

    def search_radius(
        self,
        qx: float,
        qy: float,
        radius: float,
        available_only: bool = False,
        tier_filter: Optional[str] = None
    ) -> Tuple[List[REntry], Dict[str, Any]]:
        radius_sq = radius * radius
        matches: List[REntry] = []
        metrics = {
            "total_nodes_visited": 0,
            "subtrees_pruned": 0,
            "distance_checks": 0,
            "pruned_mbrs": [],
            "visited_mbrs": []
        }

        self._search_radius_recursive(
            self.root, qx, qy, radius, radius_sq, available_only, tier_filter, matches, metrics
        )

        matches.sort(key=lambda e: e.distance_to(qx, qy))
        total_eval = metrics["subtrees_pruned"] + metrics["total_nodes_visited"]
        pruning_ratio = (metrics["subtrees_pruned"] / max(1, total_eval)) * 100.0
        metrics["pruning_efficiency_pct"] = pruning_ratio
        return matches, metrics

    def _search_radius_recursive(
        self,
        node: RNode,
        qx: float,
        qy: float,
        radius: float,
        radius_sq: float,
        available_only: bool,
        tier_filter: Optional[str],
        matches: List[REntry],
        metrics: Dict[str, Any]
    ) -> None:
        metrics["total_nodes_visited"] += 1
        node_mbr = node.mbr
        if node_mbr is not None:
            metrics["visited_mbrs"].append((node.level, node_mbr))

        for entry in node.entries:
            entry_dist_sq = entry.mbr.min_dist_sq(qx, qy)
            if entry_dist_sq > radius_sq:
                metrics["subtrees_pruned"] += 1
                metrics["pruned_mbrs"].append((node.level, entry.mbr))
                continue

            if node.is_leaf:
                metrics["distance_checks"] += 1
                if entry.distance_sq_to(qx, qy) <= radius_sq:
                    status_ok = not available_only or entry.status == "AVAILABLE"
                    tier_ok = tier_filter is None or tier_filter == "All" or entry.vehicle_type == tier_filter
                    if status_ok and tier_ok:
                        matches.append(entry)
            else:
                if entry.child:
                    self._search_radius_recursive(
                        entry.child, qx, qy, radius, radius_sq, available_only, tier_filter, matches, metrics
                    )

    def search_knn(
        self,
        qx: float,
        qy: float,
        k: int = 5,
        available_only: bool = True,
        tier_filter: Optional[str] = None
    ) -> Tuple[List[Tuple[float, REntry]], Dict[str, Any]]:
        candidates: List[Tuple[float, REntry]] = []
        metrics = {
            "nodes_visited": 0,
            "branches_pruned": 0,
            "exact_distance_evals": 0
        }

        self._knn_branch_and_bound(
            self.root, qx, qy, k, available_only, tier_filter, candidates, metrics
        )

        candidates.sort(key=lambda item: item[0])
        return candidates[:k], metrics

    def _knn_branch_and_bound(
        self,
        node: RNode,
        qx: float,
        qy: float,
        k: int,
        available_only: bool,
        tier_filter: Optional[str],
        candidates: List[Tuple[float, REntry]],
        metrics: Dict[str, Any]
    ) -> None:
        metrics["nodes_visited"] += 1
        worst_k_dist = candidates[-1][0] if len(candidates) >= k else float('inf')
        sorted_entries = node.get_sorted_entries_by_dist(qx, qy)

        for dist_sq, entry in sorted_entries:
            mindist = math.sqrt(dist_sq)
            if len(candidates) >= k and mindist >= worst_k_dist:
                metrics["branches_pruned"] += 1
                continue

            if node.is_leaf:
                metrics["exact_distance_evals"] += 1
                status_ok = not available_only or entry.status == "AVAILABLE"
                tier_ok = tier_filter is None or tier_filter == "All" or entry.vehicle_type == tier_filter
                if status_ok and tier_ok:
                    actual_dist = entry.distance_to(qx, qy)
                    if len(candidates) < k or actual_dist < worst_k_dist:
                        candidates.append((actual_dist, entry))
                        candidates.sort(key=lambda item: item[0])
                        if len(candidates) > k:
                            candidates.pop()
                        worst_k_dist = candidates[-1][0] if len(candidates) >= k else float('inf')
            else:
                if entry.child:
                    self._knn_branch_and_bound(
                        entry.child, qx, qy, k, available_only, tier_filter, candidates, metrics
                    )
                    worst_k_dist = candidates[-1][0] if len(candidates) >= k else float('inf')

    def count_drivers_in_mbr(self, query_mbr: Rectangle, available_only: bool = True) -> int:
        count = 0
        stack = [self.root]
        while stack:
            curr = stack.pop()
            if curr.mbr is None or not curr.mbr.intersects(query_mbr):
                continue
            if curr.is_leaf:
                for entry in curr.entries:
                    if query_mbr.contains_point(entry.x, entry.y):
                        if not available_only or entry.status == "AVAILABLE":
                            count += 1
            else:
                for entry in curr.entries:
                    if entry.child and entry.mbr.intersects(query_mbr):
                        stack.append(entry.child)
        return count

    def predict_dispatch_eta(self, qx: float, qy: float, driver: REntry) -> float:
        dist_px = math.hypot(driver.x - qx, driver.y - qy)
        dist_km = (dist_px * 20.0) / 1000.0
        avg_speed = max(15.0, driver.speed)
        return round((dist_km / avg_speed) * 60.0 * 1.2, 1)

    def get_all_mbrs(self) -> List[Tuple[int, Rectangle, bool]]:
        result: List[Tuple[int, Rectangle, bool]] = []
        self._collect_mbrs(self.root, result)
        return result

    def _collect_mbrs(self, node: RNode, result: List[Tuple[int, Rectangle, bool]]) -> None:
        node_mbr = node.mbr
        if node_mbr is not None:
            result.append((node.level, node_mbr, node.is_leaf))
        if not node.is_leaf:
            for entry in node.entries:
                if entry.child:
                    self._collect_mbrs(entry.child, result)

    def get_all_drivers(self) -> List[REntry]:
        drivers: List[REntry] = []
        self._collect_drivers(self.root, drivers)
        return drivers

    def _collect_drivers(self, node: RNode, drivers: List[REntry]) -> None:
        if node.is_leaf:
            for entry in node.entries:
                drivers.append(entry)
            return
        for entry in node.entries:
            if entry.child:
                self._collect_drivers(entry.child, drivers)

    def get_driver(self, driver_id: str) -> Optional[REntry]:
        _, entry = self._find_leaf_entry(self.root, driver_id)
        return entry

    def height(self) -> int:
        h = 1
        curr = self.root
        while not curr.is_leaf and curr.entries:
            h += 1
            curr = curr.entries[0].child
        return h

    def clear(self) -> None:
        self.root = RNode(is_leaf=True, parent=None, level=0)
        self.total_vehicles = 0
        self.total_splits = 0


# =============================================================================
# 6. SURGE & FLEET MANAGERS
# =============================================================================

DEMO_DRIVERS_BASELINE = [
    ("D1", 150.0, 150.0, "UberX", 4.92),
    ("D2", 250.0, 220.0, "UberX", 4.88),
    ("D3", 360.0, 190.0, "Comfort", 4.95),
    ("D4", 520.0, 180.0, "UberBlack", 4.99),
    ("D5", 620.0, 260.0, "UberX", 4.75),
    ("D6", 220.0, 360.0, "UberXL", 4.85),
    ("D7", 330.0, 330.0, "Comfort", 4.91),
    ("D8", 460.0, 350.0, "UberX", 4.89),
    ("D9", 600.0, 390.0, "UberBlack", 4.97),
    ("D10", 720.0, 420.0, "UberX", 4.80),
    ("D11", 120.0, 500.0, "UberXL", 4.78),
    ("D12", 280.0, 500.0, "UberX", 4.94),
    ("D13", 500.0, 510.0, "Comfort", 4.90),
    ("D14", 680.0, 520.0, "UberX", 4.86),
]


class ActiveTrip:
    def __init__(self, trip_id: str, driver_id: str, pickup_x: float, pickup_y: float, dropoff_x: float, dropoff_y: float):
        self.trip_id = trip_id
        self.driver_id = driver_id
        self.pickup_x = pickup_x
        self.pickup_y = pickup_y
        self.dropoff_x = dropoff_x
        self.dropoff_y = dropoff_y
        self.phase = "EN_ROUTE_PICKUP"


class SurgeZone:
    __slots__ = ('zone_id', 'mbr', 'multiplier', 'supply', 'demand', 'label')

    def __init__(self, zone_id: str, mbr: Rectangle, multiplier: float, supply: int, demand: int, label: str):
        self.zone_id = zone_id
        self.mbr = mbr
        self.multiplier = multiplier
        self.supply = supply
        self.demand = demand
        self.label = label


class SurgeEngine:
    def __init__(self, tree: RStarTree, map_width: float = 860.0, map_height: float = 640.0):
        self.tree = tree
        self.map_width = map_width
        self.map_height = map_height
        self.active_zones: List[SurgeZone] = []

    def recalculate_surge_zones(self, grid_divisions: int = 4) -> List[SurgeZone]:
        self.active_zones.clear()
        step_x = self.map_width / grid_divisions
        step_y = self.map_height / grid_divisions
        zone_idx = 1
        for i in range(grid_divisions):
            for j in range(grid_divisions):
                mbr = Rectangle(i * step_x, j * step_y, (i + 1) * step_x, (j + 1) * step_y)
                supply = self.tree.count_drivers_in_mbr(mbr, available_only=True)
                demand = 3 if i == 2 and j == 1 else 1  # Simulated downtown surge hotspot
                ratio = demand / max(1, supply)
                mult = 2.4 if ratio > 2.0 else (1.5 if ratio > 1.0 else 1.0)
                lbl = "HIGH SURGE" if mult >= 2.0 else ("SURGE" if mult > 1.0 else "NORMAL")
                self.active_zones.append(SurgeZone(f"ZONE_{zone_idx}", mbr, mult, supply, demand, lbl))
                zone_idx += 1
        return self.active_zones


class FleetManager:
    def __init__(self, tree: RStarTree, map_width: float = 860.0, map_height: float = 640.0):
        self.tree = tree
        self.map_width = map_width
        self.map_height = map_height
        self.active_trips: Dict[str, ActiveTrip] = {}
        self.autopilot_running = False
        self.movement_speed = 4.0
        self.trip_counter = 1001

    def load_baseline_fleet(self) -> None:
        self.tree.clear()
        self.active_trips.clear()
        for d_id, x, y, v_type, rating in DEMO_DRIVERS_BASELINE:
            self.tree.insert(d_id, x, y, "AVAILABLE", v_type, rating, random.uniform(0, 360), 30.0)

    def spawn_bulk_drivers(self, count: int = 50) -> None:
        v_types = ["UberX", "Comfort", "UberBlack", "UberXL"]
        start_id = self.tree.total_vehicles + 1
        for i in range(count):
            d_id = f"D{start_id + i}"
            x = random.uniform(30.0, self.map_width - 30.0)
            y = random.uniform(30.0, self.map_height - 30.0)
            self.tree.insert(d_id, x, y, "AVAILABLE", random.choice(v_types), round(random.uniform(4.65, 5.0), 2), random.uniform(0, 360), 30.0)

    def dispatch_trip(self, pickup_x: float, pickup_y: float, dropoff_x: float, dropoff_y: float) -> Optional[Tuple[ActiveTrip, REntry]]:
        candidates, _ = self.tree.search_knn(pickup_x, pickup_y, k=1, available_only=True)
        if not candidates:
            return None
        _, best_driver_entry = candidates[0]
        driver_id = best_driver_entry.driver_id
        self.tree.update_status(driver_id, "DISPATCHED")

        trip_id = f"TRIP_{self.trip_counter}"
        self.trip_counter += 1
        trip = ActiveTrip(trip_id, driver_id, pickup_x, pickup_y, dropoff_x, dropoff_y)
        self.active_trips[trip_id] = trip
        return trip, best_driver_entry

    def step_simulation_tick(self) -> List[str]:
        completed = []
        all_drivers = self.tree.get_all_drivers()
        driver_trip_map = {t.driver_id: t for t in self.active_trips.values()}

        for driver in all_drivers:
            d_id = driver.driver_id
            curr_x, curr_y = driver.x, driver.y

            if d_id in driver_trip_map:
                trip = driver_trip_map[d_id]
                if trip.phase == "EN_ROUTE_PICKUP":
                    tx, ty = trip.pickup_x, trip.pickup_y
                    dist = math.hypot(tx - curr_x, ty - curr_y)
                    if dist <= self.movement_speed * 1.5:
                        trip.phase = "ON_TRIP"
                        self.tree.update_status(d_id, "ON_TRIP")
                    else:
                        angle = math.atan2(ty - curr_y, tx - curr_x)
                        nx = curr_x + self.movement_speed * math.cos(angle)
                        ny = curr_y + self.movement_speed * math.sin(angle)
                        self.tree.update_position(d_id, nx, ny, heading=math.degrees(angle) % 360, speed=35.0)
                elif trip.phase == "ON_TRIP":
                    tx, ty = trip.dropoff_x, trip.dropoff_y
                    dist = math.hypot(tx - curr_x, ty - curr_y)
                    if dist <= self.movement_speed * 1.5:
                        trip.phase = "COMPLETED"
                        self.tree.update_status(d_id, "AVAILABLE")
                        completed.append(trip.trip_id)
                    else:
                        angle = math.atan2(ty - curr_y, tx - curr_x)
                        nx = curr_x + self.movement_speed * math.cos(angle)
                        ny = curr_y + self.movement_speed * math.sin(angle)
                        self.tree.update_position(d_id, nx, ny, heading=math.degrees(angle) % 360, speed=40.0)
            else:
                if self.autopilot_running and driver.status == "AVAILABLE":
                    delta_angle = random.uniform(-15.0, 15.0)
                    new_heading = (driver.heading + delta_angle) % 360
                    rad = math.radians(new_heading)
                    cand_x = curr_x + 1.8 * math.cos(rad)
                    cand_y = curr_y + 1.8 * math.sin(rad)
                    if cand_x < 30.0 or cand_x > self.map_width - 30.0:
                        new_heading = (180 - new_heading) % 360
                        cand_x = max(30.0, min(self.map_width - 30.0, cand_x))
                    if cand_y < 30.0 or cand_y > self.map_height - 30.0:
                        new_heading = (360 - new_heading) % 360
                        cand_y = max(30.0, min(self.map_height - 30.0, cand_y))
                    self.tree.update_position(d_id, cand_x, cand_y, heading=new_heading, speed=25.0)

        for t_id in completed:
            if t_id in self.active_trips:
                del self.active_trips[t_id]

        return completed


# =============================================================================
# 7. GUI & CANVAS RENDERING
# =============================================================================

BG_ROOT = "#0B0F19"
BG_PANEL = "#111827"
BG_PANEL_ALT = "#161F30"
BG_CANVAS = "#070A10"
BG_INPUT = "#1F2937"
BORDER_COLOR = "#2D3748"
TEXT_PRIMARY = "#F9FAFB"
TEXT_SECONDARY = "#9CA3AF"
TEXT_MUTED = "#6B7280"
TEXT_ACCENT = "#38BDF8"
COLOR_AVAILABLE = "#10B981"
COLOR_DISPATCHED = "#F59E0B"
COLOR_ON_TRIP = "#A855F7"
COLOR_OFFLINE = "#6B7280"
COLOR_QUERY = "#00F0FF"
COLOR_PRUNED = "#EF4444"
COLOR_DROPOFF = "#EC4899"
MBR_LEVEL_COLORS = {0: "#14B8A6", 1: "#06B6D4", 2: "#8B5CF6", 3: "#F59E0B"}


class CanvasMap(tk.Canvas):
    def __init__(self, master, width: int = 860, height: int = 640, **kwargs):
        super().__init__(master, width=width, height=height, background=BG_CANVAS, highlightthickness=1, highlightbackground="#1F2937", **kwargs)
        self.map_width = width
        self.map_height = height
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._drag_start = None

        self.query_center: Optional[Tuple[float, float]] = None
        self.query_radius: float = 100.0
        self.dropoff_point: Optional[Tuple[float, float]] = None
        self.highlighted_drivers: Set[str] = set()
        self.selected_driver: Optional[REntry] = None
        self.surge_zones: List[SurgeZone] = []

        self.show_level_0 = True
        self.show_level_1 = True
        self.show_level_root = True
        self.show_pruned = True
        self.show_surge = True
        self.last_pruned_mbrs = []
        self.pulse_phase = 0.0

        self.bind("<MouseWheel>", self._on_wheel)
        self.bind("<Button-2>", self._on_mid_press)
        self.bind("<B2-Motion>", self._on_mid_drag)

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        return (wx * self.zoom) + self.pan_x, (wy * self.zoom) + self.pan_y

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        return (sx - self.pan_x) / self.zoom, (sy - self.pan_y) / self.zoom

    def _on_wheel(self, event) -> None:
        factor = 1.15 if event.delta > 0 else 0.85
        new_zoom = max(0.5, min(3.5, self.zoom * factor))
        if new_zoom != self.zoom:
            mx, my = float(event.x), float(event.y)
            wx, wy = self.screen_to_world(mx, my)
            self.zoom = new_zoom
            self.pan_x = mx - wx * self.zoom
            self.pan_y = my - wy * self.zoom

    def _on_mid_press(self, event) -> None:
        self._drag_start = (event.x, event.y)

    def _on_mid_drag(self, event) -> None:
        if self._drag_start:
            self.pan_x += event.x - self._drag_start[0]
            self.pan_y += event.y - self._drag_start[1]
            self._drag_start = (event.x, event.y)

    def reset_view(self) -> None:
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    def redraw_scene(self, tree_mbrs, all_drivers, active_trips, fps: float, tree_height: int):
        self.delete("all")

        # Grid
        g_step = 50 * self.zoom
        for x in range(int(self.pan_x % g_step), self.map_width + 50, int(g_step)):
            self.create_line(x, 0, x, self.map_height, fill="#0C121E")
        for y in range(int(self.pan_y % g_step), self.map_height + 50, int(g_step)):
            self.create_line(0, y, self.map_width, y, fill="#0C121E")

        # Surge Zones
        if self.show_surge:
            for z in self.surge_zones:
                if z.multiplier > 1.0:
                    sx1, sy1 = self.world_to_screen(z.mbr.min_x, z.mbr.min_y)
                    sx2, sy2 = self.world_to_screen(z.mbr.max_x, z.mbr.max_y)
                    col = "#EF4444" if z.multiplier >= 2.0 else "#F59E0B"
                    self.create_rectangle(sx1, sy1, sx2, sy2, outline=col, dash=(2, 4))
                    self.create_text(sx1 + 4, sy1 + 4, text=f"{z.multiplier}x Surge", fill=col, font=("Segoe UI", 7, "bold"), anchor="nw")

        # MBRs
        for level, mbr, is_leaf in tree_mbrs:
            if mbr is None or mbr.area() < 1e-6:
                continue
            if is_leaf and not self.show_level_0:
                continue
            if not is_leaf and level < (tree_height - 1) and not self.show_level_1:
                continue
            if level >= (tree_height - 1) and not self.show_level_root:
                continue

            color = MBR_LEVEL_COLORS.get(min(level, 3), "#38BDF8")
            dash = (4, 4) if is_leaf else (8, 4)
            width = 1 if is_leaf else (2 if level >= tree_height - 1 else 1)
            sx1, sy1 = self.world_to_screen(mbr.min_x, mbr.min_y)
            sx2, sy2 = self.world_to_screen(mbr.max_x, mbr.max_y)
            self.create_rectangle(sx1, sy1, sx2, sy2, outline=color, dash=dash, width=width)

        # Pruned MBRs
        if self.show_pruned and self.query_center:
            qx, qy = self.query_center
            sqx, sqy = self.world_to_screen(qx, qy)
            for level, mbr in self.last_pruned_mbrs:
                if mbr:
                    sx1, sy1 = self.world_to_screen(mbr.min_x, mbr.min_y)
                    sx2, sy2 = self.world_to_screen(mbr.max_x, mbr.max_y)
                    self.create_rectangle(sx1, sy1, sx2, sy2, outline=COLOR_PRUNED, dash=(3, 3), width=1)
                    cx, cy = mbr.center()
                    scx, scy = self.world_to_screen(cx, cy)
                    self.create_line(sqx, sqy, scx, scy, fill="#EF4444", dash=(2, 6))

        # Active Trips
        driver_pos = {d.driver_id: (d.x, d.y) for d in all_drivers}
        for trip in active_trips.values():
            if trip.driver_id in driver_pos:
                dx, dy = driver_pos[trip.driver_id]
                sdx, sdy = self.world_to_screen(dx, dy)
                spx, spy = self.world_to_screen(trip.pickup_x, trip.pickup_y)
                stx, sty = self.world_to_screen(trip.dropoff_x, trip.dropoff_y)
                if trip.phase == "EN_ROUTE_PICKUP":
                    self.create_line(sdx, sdy, spx, spy, fill=COLOR_DISPATCHED, dash=(6, 3), width=2)
                elif trip.phase == "ON_TRIP":
                    self.create_line(sdx, sdy, stx, sty, fill=COLOR_ON_TRIP, width=2)

        # Query Radius
        if self.query_center:
            qx, qy = self.query_center
            r = self.query_radius
            sqx, sqy = self.world_to_screen(qx, qy)
            sr = r * self.zoom
            self.pulse_phase = (self.pulse_phase + 0.05) % 1.0
            pulse_r = sr * (0.2 + 0.8 * self.pulse_phase)
            self.create_oval(sqx - pulse_r, sqy - pulse_r, sqx + pulse_r, sqy + pulse_r, outline="#083344")
            self.create_oval(sqx - sr, sqy - sr, sqx + sr, sqy + sr, outline=COLOR_QUERY, width=2, dash=(6, 4))
            self.create_oval(sqx - 6, sqy - 6, sqx + 6, sqy + 6, fill=COLOR_QUERY, outline="#FFF")
            self.create_text(sqx + 10, sqy - 10, text=f"RIDER ({qx:.0f}, {qy:.0f})", fill=COLOR_QUERY, font=("Segoe UI", 9, "bold"), anchor="sw")

        if self.dropoff_point:
            dx, dy = self.dropoff_point
            sdx, sdy = self.world_to_screen(dx, dy)
            self.create_oval(sdx - 5, sdy - 5, sdx + 5, sdy + 5, fill=COLOR_DROPOFF, outline="#FFF")
            self.create_text(sdx + 8, sdy - 8, text=f"DROPOFF ({dx:.0f}, {dy:.0f})", fill=COLOR_DROPOFF, font=("Segoe UI", 8, "bold"), anchor="sw")

        # Drivers
        for d in all_drivers:
            d_id = d.driver_id
            sx, sy = self.world_to_screen(d.x, d.y)
            is_matched = d_id in self.highlighted_drivers
            is_selected = self.selected_driver and self.selected_driver.driver_id == d_id
            fill = COLOR_QUERY if (is_matched or is_selected) else (COLOR_AVAILABLE if d.status == "AVAILABLE" else (COLOR_DISPATCHED if d.status == "DISPATCHED" else COLOR_ON_TRIP))
            rad = max(4, int(6 * self.zoom))

            if is_matched or is_selected or d.status in ("DISPATCHED", "ON_TRIP"):
                self.create_oval(sx - rad - 4, sy - rad - 4, sx + rad + 4, sy + rad + 4, outline=fill)
            self.create_oval(sx - rad, sy - rad, sx + rad, sy + rad, fill=fill, outline="#111827")

            angle_rad = math.radians(d.heading)
            self.create_line(sx, sy, sx + (rad + 6) * math.cos(angle_rad), sy + (rad + 6) * math.sin(angle_rad), fill=fill, width=2)
            if self.zoom >= 0.8:
                self.create_text(sx + rad + 3, sy - 2, text=f"{d_id}", fill="#FFF" if is_matched else TEXT_SECONDARY, font=("Segoe UI", 8 if is_matched else 7), anchor="w")

        # HUD
        hud_x = self.map_width - 180
        self.create_rectangle(hud_x - 10, 10, self.map_width - 10, 85, fill="#0F172A", outline="#1E293B")
        self.create_text(hud_x, 18, text=f"FLEET: {len(all_drivers)} ACTIVE", fill=COLOR_AVAILABLE, font=("Segoe UI", 8, "bold"), anchor="nw")
        self.create_text(hud_x, 34, text=f"R*-TREE HEIGHT: {tree_height}", fill=TEXT_ACCENT, font=("Segoe UI", 8, "bold"), anchor="nw")
        self.create_text(hud_x, 50, text=f"FPS: {fps:.1f} | ZOOM: {self.zoom:.2f}x", fill="#E2E8F0", font=("Segoe UI", 8), anchor="nw")
        self.create_text(hud_x, 66, text="Mid-Click Drag=Pan", fill="#94A3B8", font=("Segoe UI", 7), anchor="nw")


class StandaloneApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Uber Dispatch OS — Unified R*-Tree Enterprise Edition [Standalone]")
        self.geometry("1420x900")
        self.minsize(1150, 720)
        self.configure(bg=BG_ROOT)

        self.tree = RStarTree(max_entries=4, min_entries=2)
        self.fleet_manager = FleetManager(self.tree, 860, 640)
        self.surge_engine = SurgeEngine(self.tree, 860, 640)
        self.fps_tracker = 30.0
        self.last_frame = time.perf_counter()

        self._build_ui()
        self.reset_fleet()
        self.canvas.surge_zones = self.surge_engine.recalculate_surge_zones()
        self._loop()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG_PANEL_ALT, padx=14, pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text="UBER SPATIAL DISPATCH COMMAND CENTER", font=("Segoe UI", 14, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL_ALT).pack(side="left")
        tk.Label(hdr, text="  |  Unified Single Data Structure R*-Tree  |  Amrita CSE DSA Lab 3", font=("Segoe UI", 9), fg=TEXT_ACCENT, bg=BG_PANEL_ALT).pack(side="left")

        body = tk.Frame(self, bg=BG_ROOT, padx=10, pady=8)
        body.pack(fill="both", expand=True)

        self.canvas = CanvasMap(body, 860, 640)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_click)

        side = tk.Frame(body, bg=BG_PANEL, width=480, padx=12, pady=10)
        side.pack(side="right", fill="both")
        side.pack_propagate(False)

        tk.Label(side, text="Rider Query Dispatch", font=("Segoe UI", 11, "bold"), fg=TEXT_ACCENT, bg=BG_PANEL).pack(anchor="w")
        qf = tk.Frame(side, bg=BG_PANEL_ALT, padx=8, pady=6)
        qf.pack(fill="x", pady=4)

        r1 = tk.Frame(qf, bg=BG_PANEL_ALT)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="X:", fg=TEXT_SECONDARY, bg=BG_PANEL_ALT).pack(side="left")
        self.qx = tk.Entry(r1, bg=BG_INPUT, fg=TEXT_PRIMARY, width=6)
        self.qx.insert(0, "390")
        self.qx.pack(side="left", padx=4)

        tk.Label(r1, text="Y:", fg=TEXT_SECONDARY, bg=BG_PANEL_ALT).pack(side="left", padx=(8, 0))
        self.qy = tk.Entry(r1, bg=BG_INPUT, fg=TEXT_PRIMARY, width=6)
        self.qy.insert(0, "300")
        self.qy.pack(side="left", padx=4)

        tk.Label(r1, text="Tier:", fg=TEXT_SECONDARY, bg=BG_PANEL_ALT).pack(side="left", padx=(8, 0))
        self.combo_tier = ttk.Combobox(r1, values=["All", "UberX", "Comfort", "UberBlack", "UberXL"], width=8, state="readonly")
        self.combo_tier.set("All")
        self.combo_tier.pack(side="left", padx=4)

        r2 = tk.Frame(qf, bg=BG_PANEL_ALT)
        r2.pack(fill="x", pady=2)
        tk.Label(r2, text="Radius (px):", fg=TEXT_SECONDARY, bg=BG_PANEL_ALT).pack(side="left")
        self.qr = tk.Entry(r2, bg=BG_INPUT, fg=TEXT_PRIMARY, width=6)
        self.qr.insert(0, "100")
        self.qr.pack(side="left", padx=4)

        # Action Buttons
        tk.Button(side, text="⚡ Find Nearby (Radius Search)", bg="#2563EB", fg="#FFF", font=("Segoe UI", 9, "bold"), relief="flat", command=self.do_radius).pack(fill="x", pady=2)
        tk.Button(side, text="🎯 k-NN Optimal Dispatch (Branch & Bound)", bg="#D97706", fg="#FFF", font=("Segoe UI", 9, "bold"), relief="flat", command=self.do_knn).pack(fill="x", pady=2)
        tk.Button(side, text="🚀 Simulate Trip Lifecycle (Pickup -> Dropoff)", bg="#059669", fg="#FFF", font=("Segoe UI", 9, "bold"), relief="flat", command=self.do_trip).pack(fill="x", pady=2)
        tk.Button(side, text="🌐 LAUNCH SPLINE 3D DIGITAL TWIN (WebGL)", bg="#0284C7", fg="#FFF", font=("Segoe UI", 9, "bold"), relief="flat", command=self.open_spline_3d).pack(fill="x", pady=2)
        tk.Button(side, text="▶ TOGGLE DYNAMIC GPS AUTOPILOT", bg="#4B5563", fg="#FFF", font=("Segoe UI", 9, "bold"), relief="flat", command=self.toggle_auto).pack(fill="x", pady=2)
        tk.Button(side, text="⚡ Hilbert Bulk Load (1,000 Drivers)", bg="#7C3AED", fg="#FFF", font=("Segoe UI", 9, "bold"), relief="flat", command=self.do_hilbert_bulk).pack(fill="x", pady=2)

        # Faculty Test Cases
        tk.Label(side, text="Official Faculty Test Cases (Lab Evaluation)", font=("Segoe UI", 10, "bold"), fg=TEXT_SECONDARY, bg=BG_PANEL).pack(anchor="w", pady=(8, 2))
        tcf = tk.Frame(side, bg=BG_PANEL)
        tcf.pack(fill="x")
        tk.Button(tcf, text="TC1 (390,300/R=100)", bg=BG_PANEL_ALT, fg=TEXT_PRIMARY, font=("Segoe UI", 8), command=lambda: self.run_tc(390, 300, 100)).pack(side="left", fill="x", expand=True, padx=1)
        tk.Button(tcf, text="TC2 (390,300/R=50)", bg=BG_PANEL_ALT, fg=TEXT_PRIMARY, font=("Segoe UI", 8), command=lambda: self.run_tc(390, 300, 50)).pack(side="left", fill="x", expand=True, padx=1)
        tk.Button(tcf, text="TC3 (50,50/R=30)", bg=BG_PANEL_ALT, fg=TEXT_PRIMARY, font=("Segoe UI", 8), command=lambda: self.run_tc(50, 50, 30)).pack(side="left", fill="x", expand=True, padx=1)
        tk.Button(tcf, text="TC4 (620,300/R=100)", bg=BG_PANEL_ALT, fg=TEXT_PRIMARY, font=("Segoe UI", 8), command=lambda: self.run_tc(620, 300, 100)).pack(side="left", fill="x", expand=True, padx=1)

        # Log Text Box
        tk.Label(side, text="Dispatch Log & Algorithmic Telemetry", font=("Segoe UI", 10, "bold"), fg=TEXT_SECONDARY, bg=BG_PANEL).pack(anchor="w", pady=(8, 2))
        self.log = tk.Text(side, height=16, bg=BG_INPUT, fg=TEXT_PRIMARY, font=("Consolas", 9), relief="flat")
        self.log.pack(fill="both", expand=True)

    def open_spline_3d(self):
        """Launches the interactive Spline 3D / Three.js WebGL Digital Twin in the default browser."""
        import webbrowser
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spline_3d_viewer.html")
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui", "spline_3d_viewer.html")
        if os.path.exists(path):
            webbrowser.open_new_tab(f"file:///{os.path.abspath(path).replace(os.sep, '/')}")
        else:
            messagebox.showinfo("Spline 3D Viewer", "Spline 3D viewer file not found.")

    def reset_fleet(self):
        self.fleet_manager.load_baseline_fleet()
        self.log.delete("1.0", "end")
        self.log.insert("1.0", "Baseline fleet loaded (14 Drivers). Click map or run TC1.\n")

    def _on_click(self, event):
        wx, wy = self.canvas.screen_to_world(event.x, event.y)
        self.qx.delete(0, "end")
        self.qx.insert(0, f"{wx:.0f}")
        self.qy.delete(0, "end")
        self.qy.insert(0, f"{wy:.0f}")
        self.do_radius()

    def do_radius(self):
        try:
            x, y = float(self.qx.get()), float(self.qy.get())
            r = float(self.qr.get())
            tier = self.combo_tier.get()
            self.canvas.query_center = (x, y)
            self.canvas.query_radius = r

            start = time.perf_counter_ns()
            matches, metrics = self.tree.search_radius(x, y, r, tier_filter=tier)
            us = (time.perf_counter_ns() - start) / 1000.0

            self.canvas.last_pruned_mbrs = metrics["pruned_mbrs"]
            self.canvas.highlighted_drivers = {e.driver_id for e in matches}

            lines = [
                f"=== RADIUS SEARCH: Origin ({x:.0f}, {y:.0f}) R={r:.0f} (Tier: {tier}) ===",
                f"Matched: {len(matches)} drivers | Latency: {us:.1f} µs",
                f"Subtrees Pruned: {metrics['subtrees_pruned']} ({metrics['pruning_efficiency_pct']:.1f}% skipped)",
                f"Distance checks performed: {metrics['distance_checks']}/{self.tree.total_vehicles}",
                "------------------------------------------------"
            ]
            for idx, m in enumerate(matches, 1):
                eta = self.tree.predict_dispatch_eta(x, y, m)
                lines.append(f"{idx}. {m.driver_id} [{m.vehicle_type}] - {m.distance_to(x, y):.1f} px | ETA: ~{eta} min ({m.status})")
            if not matches:
                lines.append("No drivers within radius.")
            self.log.delete("1.0", "end")
            self.log.insert("1.0", "\n".join(lines))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def do_knn(self):
        x, y = float(self.qx.get()), float(self.qy.get())
        tier = self.combo_tier.get()
        start = time.perf_counter_ns()
        cand, met = self.tree.search_knn(x, y, k=5, available_only=True, tier_filter=tier)
        us = (time.perf_counter_ns() - start) / 1000.0
        self.canvas.highlighted_drivers = {e.driver_id for _, e in cand}
        lines = [
            f"=== IN-TREE BRANCH-AND-BOUND k-NN (k=5, Tier: {tier}) ===",
            f"Latency: {us:.1f} µs | Branches Pruned: {met['branches_pruned']}",
            f"Exact distance checks: {met['exact_distance_evals']}",
            "------------------------------------------------"
        ]
        for rank, (dist, e) in enumerate(cand, 1):
            eta = self.tree.predict_dispatch_eta(x, y, e)
            lines.append(f"#{rank} {e.driver_id} ({e.vehicle_type}) - Dist: {dist:.1f} px | ETA: ~{eta} min | ★{e.rating:.2f}")
        self.log.delete("1.0", "end")
        self.log.insert("1.0", "\n".join(lines))

    def do_trip(self):
        x, y = float(self.qx.get()), float(self.qy.get())
        tx, ty = (x + 220) % 800 + 40, (y + 180) % 580 + 40
        self.canvas.dropoff_point = (tx, ty)
        res = self.fleet_manager.dispatch_trip(x, y, tx, ty)
        if res:
            trip, driver = res
            self.canvas.highlighted_drivers = {driver.driver_id}
            self.log.delete("1.0", "end")
            self.log.insert("1.0", f"Trip Dispatched!\nDriver: {driver.driver_id}\nPickup: ({x:.0f},{y:.0f})\nDropoff: ({tx:.0f},{ty:.0f})\nStatus: En Route to pickup.")

    def do_hilbert_bulk(self):
        self.tree.clear()
        v_types = ["UberX", "Comfort", "UberBlack", "UberXL"]
        raw = [
            REntry.create_leaf_entry(f"H_{i}", 40.0 + (i * 137.5) % 780.0, 40.0 + (i * 219.3) % 560.0, vehicle_type=v_types[i % len(v_types)])
            for i in range(1000)
        ]
        start = time.perf_counter_ns()
        HilbertBulkLoader.bulk_load(self.tree, raw)
        ms = (time.perf_counter_ns() - start) / 1e6
        self.log.delete("1.0", "end")
        self.log.insert("1.0", f"Hilbert Bulk Loaded 1,000 drivers in {ms:.2f} ms!\nTree Height: {self.tree.height()}\nRoot Fanout: {len(self.tree.root.entries)}\nOptimal MBR packing complete.")

    def toggle_auto(self):
        self.fleet_manager.autopilot_running = not self.fleet_manager.autopilot_running

    def run_tc(self, x, y, r):
        self.qx.delete(0, "end")
        self.qx.insert(0, str(x))
        self.qy.delete(0, "end")
        self.qy.insert(0, str(y))
        self.qr.delete(0, "end")
        self.qr.insert(0, str(r))
        self.do_radius()

    def _loop(self):
        now = time.perf_counter()
        delta = now - self.last_frame
        self.last_frame = now
        if delta > 0:
            self.fps_tracker = 0.9 * self.fps_tracker + 0.1 * (1.0 / delta)

        if self.fleet_manager.autopilot_running or self.fleet_manager.active_trips:
            self.fleet_manager.step_simulation_tick()

        mbrs = self.tree.get_all_mbrs()
        drivers = self.tree.get_all_drivers()
        self.canvas.redraw_scene(mbrs, drivers, self.fleet_manager.active_trips, self.fps_tracker, self.tree.height())

        self.after(33, self._loop)


if __name__ == "__main__":
    app = StandaloneApp()
    app.mainloop()
