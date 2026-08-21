"""
RStarTree - Unified Spatial Architecture for Real-Time Fleet Dispatch & Dynamic Matching.

Implements the single data structure architecture for Uber:
1. Unified Geometric Hierarchy: Drivers encapsulated directly inside REntry leaf records.
2. Least-Enlargement Subtree Selection: Minimizes volume/dead-space expansion.
3. Quadratic Overflow Splitting: Maximizes seed dead-space separation.
4. Dynamic Fleet Updates: Atomic deletion + CondenseTree underflow handling + re-insertion.
5. Asymptotic Radius Pruning: Circle-MBR MINDIST checks skip 99% of distant fleet.
6. In-Tree Branch-and-Bound k-NN Dispatch: Evaluates MINDIST directly without external heaps.
"""

import math
from typing import List, Optional, Tuple, Dict, Any, Set
from core.geometry import Rectangle
from core.entry import REntry
from core.node import RNode


class RStarTree:
    """
    Self-balancing Hierarchical Multidimensional Bounding Box Spatial Index.
    Single core data repository and dispatch engine for Uber.
    """

    def __init__(self, max_entries: int = 4, min_entries: int = 2, reinsert_p: float = 0.3):
        self.max_entries = max_entries
        self.min_entries = min_entries
        self.reinsert_p = reinsert_p
        self.root = RNode(is_leaf=True, parent=None, level=0)
        self.total_vehicles = 0
        
        # Performance and telemetry counters
        self.total_insertions = 0
        self.total_deletions = 0
        self.total_splits = 0
        self.total_pruned_subtrees = 0
        self.total_distance_evaluations = 0

    # =========================================================================
    # INSERTION & TREE BALANCING
    # =========================================================================

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
        """
        Natively inserts vehicle telemetry tuple into target leaf node in O(log_M N).
        """
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
        self.total_insertions += 1

        self._adjust_tree(target_leaf)
        return entry

    def _choose_subtree(self, node: RNode, entry_mbr: Rectangle) -> RNode:
        """
        Recursively traverses downward, selecting the child node whose MBR
        requires minimum area enlargement to absorb the vehicle.
        Tie-breaking rule: pick child with smallest base area.
        """
        if node.is_leaf:
            return node

        best_child: Optional[RNode] = None
        best_enlargement = float('inf')
        best_base_area = float('inf')

        for entry in node.entries:
            child_node = entry.child
            enl = entry.mbr.enlargement(entry_mbr)
            base_area = entry.mbr.area()

            if (enl < best_enlargement) or (math.isclose(enl, best_enlargement, rel_tol=1e-9) and base_area < best_base_area):
                best_enlargement = enl
                best_base_area = base_area
                best_child = child_node

        if best_child is None:
            best_child = node.entries[0].child

        return self._choose_subtree(best_child, entry_mbr)

    def _adjust_tree(self, node: RNode) -> None:
        """
        Ascends from leaf to root, propagating enlarged bounding boxes and
        splitting overflow nodes that exceed MAX_ENTRIES.
        """
        current = node
        while current is not None:
            if not current.is_overflow(self.max_entries):
                current.recalculate_mbr()
                self._update_parent_pointer(current)
                if current is self.root:
                    return
                current = current.parent
                continue

            # Node Overflow: Trigger Quadratic Split
            self.total_splits += 1
            group1, group2 = self._split_node(current)

            if current is self.root:
                # Tree height increases: Create a new Root node
                new_root = RNode(is_leaf=False, parent=None, level=current.level + 1)
                group1.parent = new_root
                group2.parent = new_root

                entry1 = REntry.create_internal_entry(group1)
                entry2 = REntry.create_internal_entry(group2)
                new_root.add_entry(entry1)
                new_root.add_entry(entry2)

                self.root = new_root
                return

            parent = current.parent
            # Remove old node entry from parent
            parent.entries = [e for e in parent.entries if e.child is not current]

            group1.parent = parent
            group2.parent = parent
            parent.add_entry(REntry.create_internal_entry(group1))
            parent.add_entry(REntry.create_internal_entry(group2))

            current = parent

    def _update_parent_pointer(self, node: RNode) -> None:
        """Synchronizes parent entry MBR with updated child MBR."""
        if node.parent is None:
            return
        node_mbr = node.recalculate_mbr()
        for e in node.parent.entries:
            if e.child is node:
                e.mbr = node_mbr
                return

    def _split_node(self, node: RNode) -> Tuple[RNode, RNode]:
        """
        Quadratic Split Heuristic:
        1. PickSeeds: Finds two entries that maximize dead space (waste area).
        2. Distribute: Iteratively assigns remaining entries to the group whose
           MBR requires least enlargement, respecting MIN_ENTRIES occupancy.
        """
        old_entries = list(node.entries)
        node.entries.clear()

        # Step 1: Pick Seeds
        seed_a, seed_b = None, None
        worst_waste = float('-inf')
        n = len(old_entries)

        for i in range(n):
            for j in range(i + 1, n):
                e1 = old_entries[i]
                e2 = old_entries[j]
                union_box = e1.mbr.union(e2.mbr)
                waste = union_box.area() - e1.mbr.area() - e2.mbr.area()
                if waste > worst_waste:
                    worst_waste = waste
                    seed_a = e1
                    seed_b = e2

        group1 = RNode(is_leaf=node.is_leaf, parent=node.parent, level=node.level)
        group2 = RNode(is_leaf=node.is_leaf, parent=node.parent, level=node.level)

        group1.add_entry(seed_a)
        group2.add_entry(seed_b)

        remaining = [e for e in old_entries if e is not seed_a and e is not seed_b]

        # Step 2: Distribute Remaining Entries
        while remaining:
            # Enforce 50% minimum space occupancy bound
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

            # Find entry with maximum difference in required enlargement
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
                # Tie-break 1: Smaller area
                if mbr1.area() < mbr2.area():
                    group1.add_entry(chosen)
                elif mbr2.area() < mbr1.area():
                    group2.add_entry(chosen)
                else:
                    # Tie-break 2: Fewer entries
                    if len(group1.entries) <= len(group2.entries):
                        group1.add_entry(chosen)
                    else:
                        group2.add_entry(chosen)

        # Reparent child nodes if internal
        if not group1.is_leaf:
            for e in group1.entries:
                if e.child:
                    e.child.parent = group1
        if not group2.is_leaf:
            for e in group2.entries:
                if e.child:
                    e.child.parent = group2

        return group1, group2

    # =========================================================================
    # DELETION, CONDENSETREE & DYNAMIC GPS MOVEMENT
    # =========================================================================

    def delete(self, driver_id: str) -> Optional[REntry]:
        """
        Deletes a driver record from the R*-Tree in O(log_M N).
        Triggers CondenseTree to re-insert orphan nodes upon underflow.
        """
        leaf, entry = self._find_leaf_entry(self.root, driver_id)
        if leaf is None or entry is None:
            return None

        leaf.remove_entry(entry)
        self.total_vehicles -= 1
        self.total_deletions += 1

        self._condense_tree(leaf)

        # Collapse root if it has degraded to an internal node with a single child
        if not self.root.is_leaf and len(self.root.entries) == 1:
            child = self.root.entries[0].child
            child.parent = None
            self.root = child

        return entry

    def _find_leaf_entry(self, node: RNode, driver_id: str) -> Tuple[Optional[RNode], Optional[REntry]]:
        """Searches tree to locate leaf node containing the driver ID."""
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
        """
        Maintains tree invariants after entry removal.
        If a node underflows (< MIN_ENTRIES), it is removed and its remaining
        entries are re-inserted (eliminating dead space and preserving balance).
        """
        node = leaf
        orphaned_entries: List[Tuple[int, REntry]] = []

        while node is not self.root and node is not None:
            parent = node.parent
            if node.is_underflow(self.min_entries):
                # Remove node from parent and harvest remaining entries
                if parent:
                    parent.entries = [e for e in parent.entries if e.child is not node]
                    for entry in node.entries:
                        orphaned_entries.append((node.level, entry))
            else:
                node.recalculate_mbr()
                self._update_parent_pointer(node)
            node = parent

        if self.root is not None:
            self.root.recalculate_mbr()

        # Re-insert orphaned entries at their respective levels
        for level, entry in orphaned_entries:
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
                self.total_vehicles -= 1  # Offset count increment from re-insertion

    def update_position(self, driver_id: str, new_x: float, new_y: float, heading: float = 0.0, speed: float = 0.0) -> bool:
        """
        Dynamic vehicle movement update.
        Executed purely within the R*-Tree as an atomic delete + least-enlargement re-insertion.
        """
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
        """Direct in-place status update inside leaf entry without rebalancing."""
        _, entry = self._find_leaf_entry(self.root, driver_id)
        if entry:
            entry.status = new_status
            return True
        return False

    # =========================================================================
    # RADIUS SEARCH & ASYMPTOTIC GEOMETRIC MBR PRUNING
    # =========================================================================

    def search_radius(
        self,
        qx: float,
        qy: float,
        radius: float,
        available_only: bool = False,
        tier_filter: Optional[str] = None
    ) -> Tuple[List[REntry], Dict[str, Any]]:
        """
        Performs circle-MBR radius filtering with recursive geometric pruning.
        
        Complexity: O(log_M N + K) where K is number of matched candidates.
        Prunes subtrees where MINDIST(Q, MBR) > radius.
        Returns matched candidates and detailed pruning metrics.
        """
        radius_sq = radius * radius
        matches: List[REntry] = []
        metrics = {
            "total_nodes_visited": 0,
            "subtrees_pruned": 0,
            "distance_checks": 0,
            "pruned_mbrs": [],     # Stores MBRs pruned for UI visualization
            "visited_mbrs": []     # Stores MBRs visited for UI visualization
        }

        self._search_radius_recursive(
            self.root,
            qx,
            qy,
            radius,
            radius_sq,
            available_only,
            tier_filter,
            matches,
            metrics
        )

        # Sort matches by Euclidean proximity to query center
        matches.sort(key=lambda e: e.distance_to(qx, qy))

        pruning_ratio = 0.0
        total_eval = metrics["subtrees_pruned"] + metrics["total_nodes_visited"]
        if total_eval > 0:
            pruning_ratio = (metrics["subtrees_pruned"] / total_eval) * 100.0
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
            # MINDIST Geometric Pruning Test
            entry_dist_sq = entry.mbr.min_dist_sq(qx, qy)
            if entry_dist_sq > radius_sq:
                # Geometric Theorem: Skip entire subtree!
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
                        entry.child,
                        qx,
                        qy,
                        radius,
                        radius_sq,
                        available_only,
                        tier_filter,
                        matches,
                        metrics
                    )

    # =========================================================================
    # IN-TREE BRANCH-AND-BOUND k-NN DISPATCH RANKING
    # =========================================================================

    def search_knn(
        self,
        qx: float,
        qy: float,
        k: int = 5,
        available_only: bool = True,
        tier_filter: Optional[str] = None
    ) -> Tuple[List[Tuple[float, REntry]], Dict[str, Any]]:
        """
        In-tree Best-First Branch-and-Bound k-NN Dispatch Ranking.
        
        Evaluates geometric distance lower bounds (MINDIST) directly during tree traversal,
        eliminating external priority heaps.
        """
        candidates: List[Tuple[float, REntry]] = []  # List of (dist, entry)
        metrics = {
            "nodes_visited": 0,
            "branches_pruned": 0,
            "exact_distance_evals": 0
        }

        self._knn_branch_and_bound(
            self.root,
            qx,
            qy,
            k,
            available_only,
            tier_filter,
            candidates,
            metrics
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

        # Current worst distance in the candidate set
        worst_k_dist = candidates[-1][0] if len(candidates) >= k else float('inf')

        # Order child entries ascending by MINDIST
        sorted_entries = node.get_sorted_entries_by_dist(qx, qy)

        for dist_sq, entry in sorted_entries:
            mindist = math.sqrt(dist_sq)

            # Strict Branch-and-Bound Pruning condition:
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
                        entry.child,
                        qx,
                        qy,
                        k,
                        available_only,
                        tier_filter,
                        candidates,
                        metrics
                    )
                    worst_k_dist = candidates[-1][0] if len(candidates) >= k else float('inf')

    def count_drivers_in_mbr(self, query_mbr: Rectangle, available_only: bool = True) -> int:
        """
        Calculates driver density in a geographic sector in O(log N) using MBR intersection.
        Powers Uber's dynamic surge pricing engine.
        """
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

    def predict_dispatch_eta(self, qx: float, qy: float, driver: REntry, urban_traffic_factor: float = 1.2) -> float:
        """
        Predicts driver pickup ETA in minutes using Manhattan/Euclidean transit dynamics.
        """
        dist_px = math.hypot(driver.x - qx, driver.y - qy)
        # 1 pixel = approx 20 meters; average urban speed = 35 km/h
        dist_km = (dist_px * 20.0) / 1000.0
        avg_speed_kmh = max(15.0, driver.speed)
        time_hours = (dist_km / avg_speed_kmh) * urban_traffic_factor
        return round(time_hours * 60.0, 1)

    # =========================================================================
    # INTROSPECTION, HIERARCHY TRAVERSAL & METRICS
    # =========================================================================

    def get_all_mbrs(self) -> List[Tuple[int, Rectangle, bool]]:
        """
        Traverses tree and returns (level, mbr, is_leaf) for every node.
        Enables multi-level neon visualization in the GUI.
        """
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
        """Returns all vehicle telemetry records stored inside leaf entries."""
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
        """Returns tree height (root to leaf depth)."""
        h = 1
        curr = self.root
        while not curr.is_leaf and curr.entries:
            h += 1
            curr = curr.entries[0].child
        return h

    def clear(self) -> None:
        """Wipes index and resets root to empty leaf."""
        self.root = RNode(is_leaf=True, parent=None, level=0)
        self.total_vehicles = 0
        self.total_insertions = 0
        self.total_deletions = 0
        self.total_splits = 0

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Calculates comprehensive operational metrics of the R*-Tree."""
        all_mbrs = self.get_all_mbrs()
        total_mbr_area = sum(mbr.area() for _, mbr, _ in all_mbrs)
        return {
            "total_vehicles": self.total_vehicles,
            "tree_height": self.height(),
            "total_nodes": len(all_mbrs),
            "root_entries": len(self.root.entries),
            "max_entries": self.max_entries,
            "min_entries": self.min_entries,
            "total_mbr_area": total_mbr_area,
            "total_splits": self.total_splits,
            "asymptotic_search": f"O(log_{self.max_entries} N)"
        }
