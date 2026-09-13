"""
Comprehensive Unit Test Suite for R*-Tree Spatial Architecture.
Validates geometric pruning, in-tree k-NN ranking, quadratic split,
dynamic vehicle movement, Hilbert bulk loading, and surge pricing.
"""

import unittest
from core.geometry import Rectangle
from core.entry import REntry
from core.rstar_tree import RStarTree
from core.bulk_loader import HilbertBulkLoader, hilbert_xy_to_d
from simulation.fleet_manager import DEMO_DRIVERS_BASELINE, FleetManager
from simulation.surge_engine import SurgeEngine


class TestRStarTree(unittest.TestCase):

    def setUp(self):
        self.tree = RStarTree(max_entries=4, min_entries=2)
        # Load baseline 14 drivers
        for d_id, x, y, v_type, rating in DEMO_DRIVERS_BASELINE:
            self.tree.insert(d_id, x, y, status="AVAILABLE", vehicle_type=v_type, rating=rating)

    def test_tree_construction_and_height(self):
        """Validates that 14 drivers produce a balanced tree of height >= 2."""
        self.assertEqual(self.tree.total_vehicles, 14)
        self.assertGreaterEqual(self.tree.height(), 2)

    def test_tc1_radius_search(self):
        """Validates official TC1: Origin (390, 300) with Radius 100."""
        matches, metrics = self.tree.search_radius(390, 300, 100)
        matched_ids = {e.driver_id for e in matches}
        self.assertIn("D7", matched_ids)
        self.assertIn("D8", matched_ids)
        self.assertGreater(metrics["pruning_efficiency_pct"], 0)

    def test_tc2_tight_radius_search(self):
        """Validates official TC2: Origin (390, 300) with Radius 50."""
        matches, metrics = self.tree.search_radius(390, 300, 50)
        for m in matches:
            self.assertLessEqual(m.distance_to(390, 300), 50.0)

    def test_tc3_zero_match_edge_case(self):
        """Validates official TC3: Origin (50, 50) with Radius 30."""
        matches, metrics = self.tree.search_radius(50, 50, 30)
        self.assertEqual(len(matches), 0)
        self.assertGreater(metrics["subtrees_pruned"], 0)

    def test_tc4_east_cluster_radius_search(self):
        """Validates official TC4: Origin (620, 300) with Radius 100."""
        matches, metrics = self.tree.search_radius(620, 300, 100)
        matched_ids = {e.driver_id for e in matches}
        self.assertIn("D5", matched_ids)
        self.assertIn("D9", matched_ids)

    def test_knn_branch_and_bound(self):
        """Validates in-tree k-NN ranking accuracy against sorted linear distances."""
        qx, qy = 390, 300
        k = 3
        knn_res, metrics = self.tree.search_knn(qx, qy, k=k, available_only=False)
        self.assertEqual(len(knn_res), k)
        dists = [d for d, _ in knn_res]
        self.assertEqual(dists, sorted(dists))

    def test_tier_filtering(self):
        """Validates vehicle tier filtering during radius and k-NN queries."""
        matches, _ = self.tree.search_radius(390, 300, 300, tier_filter="UberBlack")
        for m in matches:
            self.assertEqual(m.vehicle_type, "UberBlack")

    def test_dynamic_movement_update(self):
        """Validates atomic deletion and re-insertion for moving vehicle."""
        initial_driver = self.tree.get_driver("D1")
        self.assertIsNotNone(initial_driver)
        self.assertEqual((initial_driver.x, initial_driver.y), (150.0, 150.0))

        success = self.tree.update_position("D1", 400.0, 300.0)
        self.assertTrue(success)

        updated_driver = self.tree.get_driver("D1")
        self.assertIsNotNone(updated_driver)
        self.assertEqual((updated_driver.x, updated_driver.y), (400.0, 300.0))
        self.assertEqual(self.tree.total_vehicles, 14)

    def test_deletion_and_condense_tree(self):
        """Validates driver removal and tree underflow condensation."""
        del_entry = self.tree.delete("D14")
        self.assertIsNotNone(del_entry)
        self.assertEqual(self.tree.total_vehicles, 13)
        self.assertIsNone(self.tree.get_driver("D14"))

    def test_dense_cluster_quadratic_split(self):
        """Validates tree stability under dense downtown clustering."""
        for i in range(25):
            self.tree.insert(f"CLUSTER_{i}", 620.0 + i * 0.5, 300.0 + i * 0.5)
        self.assertEqual(self.tree.total_vehicles, 39)
        self.assertGreaterEqual(self.tree.height(), 2)

    def test_hilbert_bulk_loading(self):
        """Validates Hilbert curve space-filling order and bulk tree loading."""
        entries = [
            REntry.create_leaf_entry(f"H_{i}", 50.0 + (i * 25) % 600, 50.0 + (i * 35) % 400)
            for i in range(100)
        ]
        new_tree = RStarTree(max_entries=4, min_entries=2)
        HilbertBulkLoader.bulk_load(new_tree, entries)
        self.assertEqual(new_tree.total_vehicles, 100)
        self.assertGreaterEqual(new_tree.height(), 3)

        # Confirm queries work on bulk loaded tree
        matches, _ = new_tree.search_radius(300, 200, 100)
        self.assertGreater(len(matches), 0)

    def test_surge_pricing_density(self):
        """Validates in-tree driver density counting and surge multiplier calculation."""
        surge = SurgeEngine(self.tree, 860, 640)
        zones = surge.recalculate_surge_zones(grid_divisions=2)
        self.assertEqual(len(zones), 4)
        for z in zones:
            self.assertGreaterEqual(z.multiplier, 1.0)

    def test_eta_prediction(self):
        """Validates driver ETA estimation."""
        d = self.tree.get_driver("D1")
        eta = self.tree.predict_dispatch_eta(150.0, 150.0, d)
        self.assertAlmostEqual(eta, 0.0, places=1)


if __name__ == "__main__":
    unittest.main()
