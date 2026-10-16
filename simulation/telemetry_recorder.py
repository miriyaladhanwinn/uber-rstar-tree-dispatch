"""
TelemetryRecorder - Event Logging & Historical Playback for Fleet Simulation.
"""

import time
import json
from typing import List, Dict, Any, Optional


class TelemetryFrame:
    """Snapshot of fleet telemetry at a specific instant."""
    __slots__ = ('timestamp', 'drivers', 'trips', 'query')

    def __init__(self, timestamp: float, drivers: List[Dict[str, Any]], trips: List[Dict[str, Any]], query: Optional[Dict[str, Any]]):
        self.timestamp = timestamp
        self.drivers = drivers
        self.trips = trips
        self.query = query

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "drivers": self.drivers,
            "trips": self.trips,
            "query": self.query
        }


class TelemetryRecorder:
    """
    Records and buffers real-time simulation events for post-evaluation analysis,
    auditing, and animated historical playback.
    """

    def __init__(self, max_frames: int = 600):
        self.max_frames = max_frames
        self.frames: List[TelemetryFrame] = []
        self.is_recording = True
        self.is_replaying = False
        self.replay_index = 0

    def capture_frame(self, all_drivers, active_trips, query_center, query_radius) -> None:
        if not self.is_recording or self.is_replaying:
            return

        drivers_data = [
            {
                "id": d.driver_id,
                "x": round(d.x, 1),
                "y": round(d.y, 1),
                "status": d.status,
                "tier": d.vehicle_type,
                "heading": round(d.heading, 1)
            }
            for d in all_drivers
        ]

        trips_data = [
            {
                "trip_id": t.trip_id,
                "driver_id": t.driver_id,
                "phase": t.phase,
                "pickup": (t.pickup_x, t.pickup_y),
                "dropoff": (t.dropoff_x, t.dropoff_y)
            }
            for t in active_trips.values()
        ]

        q_data = None
        if query_center:
            q_data = {"center": query_center, "radius": query_radius}

        frame = TelemetryFrame(time.time(), drivers_data, trips_data, q_data)
        self.frames.append(frame)
        if len(self.frames) > self.max_frames:
            self.frames.pop(0)

    def start_replay(self) -> None:
        self.is_replaying = True
        self.replay_index = 0

    def stop_replay(self) -> None:
        self.is_replaying = False

    def get_current_replay_frame(self) -> Optional[TelemetryFrame]:
        if not self.is_replaying or not self.frames:
            return None
        frame = self.frames[self.replay_index]
        self.replay_index = (self.replay_index + 1) % len(self.frames)
        return frame

    def export_json(self, filepath: str) -> None:
        data = [f.to_dict() for f in self.frames]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
