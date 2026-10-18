"""
ReportGenerator - Audit Logging & Lab Evaluation Documentation Exporter.
"""

import csv
import json
import time
from typing import List, Dict, Any
from core.rstar_tree import RStarTree


class ReportGenerator:
    """Exports dispatch audit trails, spatial tree snapshots, and benchmark reports."""

    @staticmethod
    def export_csv_dispatch_log(filepath: str, matches: List[Any], query_center: tuple, radius: float) -> None:
        """Exports radius or k-NN matched candidate logs to CSV."""
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "Query_X", "Query_Y", "Radius",
                "Driver_ID", "Driver_X", "Driver_Y", "Vehicle_Type",
                "Rating", "Distance_px", "Status"
            ])
            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            qx, qy = query_center
            for m in matches:
                writer.writerow([
                    now_str, qx, qy, radius,
                    m.driver_id, m.x, m.y, m.vehicle_type,
                    m.rating, round(m.distance_to(qx, qy), 2), m.status
                ])

    @staticmethod
    def export_json_tree_snapshot(filepath: str, tree: RStarTree) -> None:
        """Exports entire R*-Tree bounding box structure to JSON for external GIS tools."""
        mbrs = tree.get_all_mbrs()
        drivers = tree.get_all_drivers()

        data = {
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_vehicles": tree.total_vehicles,
                "tree_height": tree.height(),
                "total_nodes": len(mbrs)
            },
            "mbr_hierarchy": [
                {
                    "level": level,
                    "is_leaf": is_leaf,
                    "min_x": mbr.min_x,
                    "min_y": mbr.min_y,
                    "max_x": mbr.max_x,
                    "max_y": mbr.max_y,
                    "area": mbr.area()
                }
                for level, mbr, is_leaf in mbrs if mbr
            ],
            "drivers": [
                {
                    "id": d.driver_id,
                    "x": d.x,
                    "y": d.y,
                    "tier": d.vehicle_type,
                    "rating": d.rating,
                    "heading": d.heading,
                    "speed": d.speed,
                    "status": d.status
                }
                for d in drivers
            ]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
