"""
Fleet Manager - Handles dynamic vehicle movement, live telemetry streams,
and real-time Uber trip dispatch lifecycles.
"""

import math
import random
import time
from typing import List, Dict, Tuple, Optional, Callable
from core.rstar_tree import RStarTree
from core.entry import REntry


# Canonical Amrita Lab Case Study Baseline 14 Drivers
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
    """Represents an active Uber trip dispatched to a driver."""
    def __init__(
        self,
        trip_id: str,
        driver_id: str,
        pickup_x: float,
        pickup_y: float,
        dropoff_x: float,
        dropoff_y: float
    ):
        self.trip_id = trip_id
        self.driver_id = driver_id
        self.pickup_x = pickup_x
        self.pickup_y = pickup_y
        self.dropoff_x = dropoff_x
        self.dropoff_y = dropoff_y
        self.phase = "EN_ROUTE_PICKUP"  # EN_ROUTE_PICKUP -> ON_TRIP -> COMPLETED
        self.created_at = time.time()
        self.path_points: List[Tuple[float, float]] = []


class FleetManager:
    """
    Manages active vehicle state records, dynamic GPS movement simulation,
    and end-to-end trip dispatch workflows.
    """

    def __init__(self, tree: RStarTree, map_width: float = 850.0, map_height: float = 620.0):
        self.tree = tree
        self.map_width = map_width
        self.map_height = map_height
        self.active_trips: Dict[str, ActiveTrip] = {}
        self.autopilot_running = False
        self.movement_speed = 4.0  # Pixels per simulation tick
        self.trip_counter = 1001

    def load_baseline_fleet(self) -> None:
        """Initializes the canonical 14 demo drivers."""
        self.tree.clear()
        self.active_trips.clear()

        for d_id, x, y, v_type, rating in DEMO_DRIVERS_BASELINE:
            self.tree.insert(
                driver_id=d_id,
                x=x,
                y=y,
                status="AVAILABLE",
                vehicle_type=v_type,
                rating=rating,
                heading=random.uniform(0, 360),
                speed=random.uniform(20.0, 45.0)
            )

    def spawn_bulk_drivers(self, count: int = 50) -> None:
        """Injects random driver fleet across the transit area to test scaling."""
        v_types = ["UberX", "Comfort", "UberBlack", "UberXL"]
        start_id = self.tree.total_vehicles + 1
        for i in range(count):
            d_id = f"D{start_id + i}"
            x = random.uniform(30.0, self.map_width - 30.0)
            y = random.uniform(30.0, self.map_height - 30.0)
            self.tree.insert(
                driver_id=d_id,
                x=x,
                y=y,
                status="AVAILABLE",
                vehicle_type=random.choice(v_types),
                rating=round(random.uniform(4.65, 5.0), 2),
                heading=random.uniform(0, 360),
                speed=random.uniform(15.0, 50.0)
            )

    def spawn_dense_cluster(self, center_x: float = 620.0, center_y: float = 300.0, count: int = 30) -> None:
        """Simulates dense urban downtown cluster to test quadratic split and overlap."""
        v_types = ["UberX", "UberBlack"]
        start_id = self.tree.total_vehicles + 1
        for i in range(count):
            d_id = f"DC_{start_id + i}"
            # Clustered within a small 35px radius
            angle = random.uniform(0, 2 * math.pi)
            rad = random.uniform(2, 35)
            x = center_x + rad * math.cos(angle)
            y = center_y + rad * math.sin(angle)
            self.tree.insert(
                driver_id=d_id,
                x=x,
                y=y,
                status="AVAILABLE",
                vehicle_type=random.choice(v_types),
                rating=4.95,
                heading=random.uniform(0, 360),
                speed=12.0
            )

    def dispatch_trip(
        self,
        pickup_x: float,
        pickup_y: float,
        dropoff_x: float,
        dropoff_y: float,
        k: int = 1
    ) -> Optional[Tuple[ActiveTrip, REntry]]:
        """
        Executes end-to-end Uber dispatch:
        1. In-tree branch-and-bound k-NN lookup for nearest AVAILABLE driver.
        2. Transitions driver state to DISPATCHED.
        3. Instantiates ActiveTrip tracker.
        """
        candidates, _ = self.tree.search_knn(pickup_x, pickup_y, k=k, available_only=True)
        if not candidates:
            return None

        _, best_driver_entry = candidates[0]
        driver_id = best_driver_entry.driver_id

        # Update in-tree status to DISPATCHED
        self.tree.update_status(driver_id, "DISPATCHED")

        trip_id = f"TRIP_{self.trip_counter}"
        self.trip_counter += 1

        trip = ActiveTrip(
            trip_id=trip_id,
            driver_id=driver_id,
            pickup_x=pickup_x,
            pickup_y=pickup_y,
            dropoff_x=dropoff_x,
            dropoff_y=dropoff_y
        )
        self.active_trips[trip_id] = trip
        return trip, best_driver_entry

    def step_simulation_tick(self) -> List[str]:
        """
        Advances dynamic simulation by one tick:
        - Free drivers wander with smooth random walks.
        - Dispatched drivers travel along trajectory towards pickup / dropoff.
        - Updates GPS positions in the R*-Tree via atomic delete + reinsert.
        """
        completed_trips = []
        all_drivers = self.tree.get_all_drivers()

        # Build mapping of driver_id to active trip
        driver_trip_map: Dict[str, ActiveTrip] = {
            t.driver_id: t for t in self.active_trips.values()
        }

        for driver in all_drivers:
            d_id = driver.driver_id
            curr_x = driver.x
            curr_y = driver.y

            if d_id in driver_trip_map:
                trip = driver_trip_map[d_id]
                # Vehicle is assigned to an active trip
                if trip.phase == "EN_ROUTE_PICKUP":
                    target_x, target_y = trip.pickup_x, trip.pickup_y
                    dist = math.hypot(target_x - curr_x, target_y - curr_y)
                    if dist <= self.movement_speed * 1.5:
                        # Arrived at pickup!
                        trip.phase = "ON_TRIP"
                        self.tree.update_status(d_id, "ON_TRIP")
                        new_x, new_y = target_x, target_y
                    else:
                        angle = math.atan2(target_y - curr_y, target_x - curr_x)
                        new_x = curr_x + self.movement_speed * math.cos(angle)
                        new_y = curr_y + self.movement_speed * math.sin(angle)
                        heading = math.degrees(angle) % 360
                        self.tree.update_position(d_id, new_x, new_y, heading=heading, speed=35.0)

                elif trip.phase == "ON_TRIP":
                    target_x, target_y = trip.dropoff_x, trip.dropoff_y
                    dist = math.hypot(target_x - curr_x, target_y - curr_y)
                    if dist <= self.movement_speed * 1.5:
                        # Trip Completed!
                        trip.phase = "COMPLETED"
                        self.tree.update_status(d_id, "AVAILABLE")
                        completed_trips.append(trip.trip_id)
                        new_x, new_y = target_x, target_y
                    else:
                        angle = math.atan2(target_y - curr_y, target_x - curr_x)
                        new_x = curr_x + self.movement_speed * math.cos(angle)
                        new_y = curr_y + self.movement_speed * math.sin(angle)
                        heading = math.degrees(angle) % 360
                        self.tree.update_position(d_id, new_x, new_y, heading=heading, speed=40.0)

            else:
                # Idle vehicle roaming in city transit network
                if self.autopilot_running and driver.status == "AVAILABLE":
                    delta_angle = random.uniform(-15.0, 15.0)
                    new_heading = (driver.heading + delta_angle) % 360
                    rad = math.radians(new_heading)

                    wander_speed = random.uniform(1.0, 2.5)
                    cand_x = curr_x + wander_speed * math.cos(rad)
                    cand_y = curr_y + wander_speed * math.sin(rad)

                    # Bounce off map borders
                    if cand_x < 30.0 or cand_x > self.map_width - 30.0:
                        new_heading = (180 - new_heading) % 360
                        cand_x = max(30.0, min(self.map_width - 30.0, cand_x))
                    if cand_y < 30.0 or cand_y > self.map_height - 30.0:
                        new_heading = (360 - new_heading) % 360
                        cand_y = max(30.0, min(self.map_height - 30.0, cand_y))

                    self.tree.update_position(
                        d_id,
                        cand_x,
                        cand_y,
                        heading=new_heading,
                        speed=random.uniform(20.0, 40.0)
                    )

        # Cleanup completed trips
        for t_id in completed_trips:
            if t_id in self.active_trips:
                del self.active_trips[t_id]

        return completed_trips
