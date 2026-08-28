"""
CanvasMap - High-Fidelity Spatial Canvas Renderer for R*-Tree Fleet Operations.
Supports multi-level MBR overlays, radar pulses, trip routes, directional vehicle icons,
live step-by-step geometric pruning inspection, dynamic surge heatmaps, and pan/zoom.
"""

import math
import tkinter as tk
from typing import Optional, Tuple, Set, List, Dict, Any
from gui.theme import (
    BG_CANVAS, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, TEXT_ACCENT,
    COLOR_AVAILABLE, COLOR_DISPATCHED, COLOR_ON_TRIP, COLOR_OFFLINE,
    COLOR_QUERY, COLOR_PRUNED, COLOR_DROPOFF, MBR_LEVEL_COLORS
)
from core.geometry import Rectangle
from core.entry import REntry


class CanvasMap(tk.Canvas):
    """
    Interactive high-definition GIS canvas rendering the R*-Tree spatial hierarchy.
    Equipped with Pan & Zoom, Surge Heatmaps, Road Network, and Driver Inspector cards.
    """

    def __init__(self, master, width: int = 860, height: int = 640, **kwargs):
        super().__init__(
            master,
            width=width,
            height=height,
            background=BG_CANVAS,
            highlightthickness=1,
            highlightbackground="#1F2937",
            **kwargs
        )
        self.map_width = width
        self.map_height = height

        # Pan and Zoom transformation state
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._drag_start = None

        # State elements
        self.query_center: Optional[Tuple[float, float]] = None
        self.query_radius: float = 100.0
        self.dropoff_point: Optional[Tuple[float, float]] = None
        self.highlighted_drivers: Set[str] = set()
        self.selected_driver: Optional[REntry] = None

        # Visualization toggles
        self.show_grid = True
        self.show_level_0_mbrs = True  # Leaf bounds
        self.show_level_1_mbrs = True  # Internal bounds
        self.show_level_root_mbrs = True  # Root bounds
        self.show_pruned_mbrs = True
        self.show_driver_labels = True
        self.show_radar_pulse = True
        self.show_hud = True
        self.show_surge_zones = True
        self.show_road_network = True
        self.show_hilbert_curve = False

        # Telemetry inspection caches
        self.last_pruned_mbrs: List[Tuple[int, Rectangle]] = []
        self.last_visited_mbrs: List[Tuple[int, Rectangle]] = []
        self.surge_zones: List[Any] = []
        self.road_segments: List[Any] = []
        self.pulse_phase = 0.0

        # Mouse interaction for Pan & Zoom
        self.bind("<MouseWheel>", self._on_mouse_wheel)
        self.bind("<Button-2>", self._on_middle_press)
        self.bind("<B2-Motion>", self._on_middle_drag)

    # -------------------------------------------------------------------------
    # COORDINATE TRANSFORMS (Pan & Zoom)
    # -------------------------------------------------------------------------

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        sx = (wx * self.zoom) + self.pan_x
        sy = (wy * self.zoom) + self.pan_y
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        wx = (sx - self.pan_x) / self.zoom
        wy = (sy - self.pan_y) / self.zoom
        return wx, wy

    def _on_mouse_wheel(self, event) -> None:
        """Zooms centered on mouse cursor."""
        factor = 1.15 if event.delta > 0 else 0.85
        new_zoom = max(0.5, min(3.5, self.zoom * factor))
        if new_zoom != self.zoom:
            mx, my = float(event.x), float(event.y)
            wx, wy = self.screen_to_world(mx, my)
            self.zoom = new_zoom
            self.pan_x = mx - wx * self.zoom
            self.pan_y = my - wy * self.zoom

    def _on_middle_press(self, event) -> None:
        self._drag_start = (event.x, event.y)

    def _on_middle_drag(self, event) -> None:
        if self._drag_start:
            dx = event.x - self._drag_start[0]
            dy = event.y - self._drag_start[1]
            self.pan_x += dx
            self.pan_y += dy
            self._drag_start = (event.x, event.y)

    def reset_view(self) -> None:
        """Resets pan and zoom to nominal 1:1 view."""
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    # -------------------------------------------------------------------------
    # QUERY CONFIGURATION
    # -------------------------------------------------------------------------

    def set_query(self, x: float, y: float, radius: float) -> None:
        self.query_center = (x, y)
        self.query_radius = radius

    def clear_query(self) -> None:
        self.query_center = None
        self.dropoff_point = None
        self.highlighted_drivers.clear()
        self.last_pruned_mbrs.clear()
        self.last_visited_mbrs.clear()
        self.selected_driver = None

    def set_dropoff(self, x: float, y: float) -> None:
        self.dropoff_point = (x, y)

    # -------------------------------------------------------------------------
    # SCENE REDRAW PIPELINE
    # -------------------------------------------------------------------------

    def redraw_scene(
        self,
        tree_mbrs: List[Tuple[int, Rectangle, bool]],
        all_drivers: List[REntry],
        active_trips: Dict[str, Any],
        fps: float = 30.0,
        tree_height: int = 1
    ) -> None:
        """Complete 60fps scene rendering pass with multi-layer compositing."""
        self.delete("all")

        # 1. Background Grid
        if self.show_grid:
            self._draw_grid()

        # 2. Road Network Corridors
        if self.show_road_network and self.road_segments:
            self._draw_roads()

        # 3. Dynamic Surge Pricing Heatmap Zones
        if self.show_surge_zones and self.surge_zones:
            self._draw_surge_zones()

        # 4. Multi-Level R*-Tree MBRs
        self._draw_tree_mbrs(tree_mbrs, tree_height)

        # 5. Pruned MBR Overlays
        if self.show_pruned_mbrs and self.query_center is not None:
            self._draw_pruned_mbrs()

        # 6. Active Trip Routes & Trajectories
        self._draw_active_trips(active_trips, all_drivers)

        # 7. Query Radius & Pulsing Radar Wave
        if self.query_center is not None:
            self._draw_query_circle()

        # 8. Dropoff Destination Pin
        if self.dropoff_point is not None:
            self._draw_dropoff_pin()

        # 9. Hilbert Space-Filling Curve
        if self.show_hilbert_curve:
            self._draw_hilbert_curve(all_drivers)

        # 10. Directional Vehicle Fleet Glyphs
        self._draw_drivers(all_drivers)

        # 11. Vehicle Inspector Card
        if self.selected_driver is not None:
            self._draw_driver_inspector()

        # 12. Heads-Up Display (HUD)
        if self.show_hud:
            self._draw_hud(len(all_drivers), tree_height, fps)

    def _draw_grid(self) -> None:
        grid_step = 50 * self.zoom
        start_x = self.pan_x % grid_step
        start_y = self.pan_y % grid_step

        for x in range(int(start_x), self.map_width + 50, int(grid_step)):
            color = "#111827" if (int((x - self.pan_x) / self.zoom) % 100 == 0) else "#0C121E"
            self.create_line(x, 0, x, self.map_height, fill=color, width=1)

        for y in range(int(start_y), self.map_height + 50, int(grid_step)):
            color = "#111827" if (int((y - self.pan_y) / self.zoom) % 100 == 0) else "#0C121E"
            self.create_line(0, y, self.map_width, y, fill=color, width=1)

    def _draw_roads(self) -> None:
        for road in self.road_segments:
            sx1, sy1 = self.world_to_screen(road.start[0], road.start[1])
            sx2, sy2 = self.world_to_screen(road.end[0], road.end[1])
            color = "#1E293B" if road.is_highway else "#131B2E"
            width = max(2, int((4 if road.is_highway else 2) * self.zoom))
            self.create_line(sx1, sy1, sx2, sy2, fill=color, width=width)

    def _draw_surge_zones(self) -> None:
        for zone in self.surge_zones:
            if zone.multiplier > 1.0:
                sx1, sy1 = self.world_to_screen(zone.mbr.min_x, zone.mbr.min_y)
                sx2, sy2 = self.world_to_screen(zone.mbr.max_x, zone.mbr.max_y)

                if zone.multiplier >= 2.5:
                    outline_c = "#EF4444"
                elif zone.multiplier >= 1.5:
                    outline_c = "#F59E0B"
                else:
                    outline_c = "#10B981"

                self.create_rectangle(sx1, sy1, sx2, sy2, outline=outline_c, width=1, dash=(2, 4))
                self.create_text(
                    sx1 + 6, sy1 + 6,
                    text=f"{zone.multiplier}x Surge",
                    fill=outline_c,
                    font=("Segoe UI", 7, "bold"),
                    anchor="nw"
                )

    def _draw_tree_mbrs(self, tree_mbrs: List[Tuple[int, Rectangle, bool]], tree_height: int) -> None:
        for level, mbr, is_leaf in tree_mbrs:
            if mbr is None or mbr.area() < 1e-6:
                continue

            if is_leaf and not self.show_level_0_mbrs:
                continue
            if not is_leaf and level < (tree_height - 1) and not self.show_level_1_mbrs:
                continue
            if level >= (tree_height - 1) and not self.show_level_root_mbrs:
                continue

            color = MBR_LEVEL_COLORS.get(min(level, 3), "#38BDF8")
            dash_pattern = (4, 4) if is_leaf else (8, 4)
            line_width = 1 if is_leaf else (2 if level >= tree_height - 1 else 1)

            sx1, sy1 = self.world_to_screen(mbr.min_x, mbr.min_y)
            sx2, sy2 = self.world_to_screen(mbr.max_x, mbr.max_y)

            self.create_rectangle(sx1, sy1, sx2, sy2, outline=color, dash=dash_pattern, width=line_width)

            if not is_leaf and (sx2 - sx1 > 40) and (sy2 - sy1 > 25):
                tag = f"L{level} Root" if level >= tree_height - 1 else f"L{level}"
                self.create_text(sx1 + 4, sy1 + 4, text=tag, fill=color, font=("Segoe UI", 7, "bold"), anchor="nw")

    def _draw_pruned_mbrs(self) -> None:
        for level, mbr in self.last_pruned_mbrs:
            if mbr is None:
                continue
            sx1, sy1 = self.world_to_screen(mbr.min_x, mbr.min_y)
            sx2, sy2 = self.world_to_screen(mbr.max_x, mbr.max_y)
            self.create_rectangle(sx1, sy1, sx2, sy2, outline=COLOR_PRUNED, dash=(3, 3), width=1)

            if self.query_center:
                qx, qy = self.query_center
                sqx, sqy = self.world_to_screen(qx, qy)
                cx, cy = mbr.center()
                scx, scy = self.world_to_screen(cx, cy)
                self.create_line(sqx, sqy, scx, scy, fill="#EF4444", dash=(2, 6), width=1)
                self.create_text(scx, scy, text="PRUNED (MINDIST > R)", fill="#F87171", font=("Segoe UI", 7, "bold"))

    def _draw_active_trips(self, active_trips: Dict[str, Any], all_drivers: List[REntry]) -> None:
        driver_pos = {d.driver_id: (d.x, d.y) for d in all_drivers}

        for trip in active_trips.values():
            if trip.driver_id in driver_pos:
                dx, dy = driver_pos[trip.driver_id]
                sdx, sdy = self.world_to_screen(dx, dy)
                spx, spy = self.world_to_screen(trip.pickup_x, trip.pickup_y)
                stx, sty = self.world_to_screen(trip.dropoff_x, trip.dropoff_y)

                if trip.phase == "EN_ROUTE_PICKUP":
                    self.create_line(sdx, sdy, spx, spy, fill=COLOR_DISPATCHED, dash=(6, 3), width=2)
                    self.create_text((sdx + spx) / 2, (sdy + spy) / 2 - 8, text="EN ROUTE", fill=COLOR_DISPATCHED, font=("Segoe UI", 7, "bold"))
                elif trip.phase == "ON_TRIP":
                    self.create_line(sdx, sdy, stx, sty, fill=COLOR_ON_TRIP, width=2)
                    self.create_text((sdx + stx) / 2, (sdy + sty) / 2 - 8, text="ON TRIP", fill=COLOR_ON_TRIP, font=("Segoe UI", 7, "bold"))

    def _draw_query_circle(self) -> None:
        qx, qy = self.query_center
        r = self.query_radius
        sqx, sqy = self.world_to_screen(qx, qy)
        sr = r * self.zoom

        if self.show_radar_pulse:
            self.pulse_phase = (self.pulse_phase + 0.05) % 1.0
            pulse_r = sr * (0.2 + 0.8 * self.pulse_phase)
            self.create_oval(sqx - pulse_r, sqy - pulse_r, sqx + pulse_r, sqy + pulse_r, outline="#083344", width=1)

        self.create_oval(sqx - sr, sqy - sr, sqx + sr, sqy + sr, outline=COLOR_QUERY, width=2, dash=(6, 4))
        self.create_oval(sqx - 6, sqy - 6, sqx + 6, sqy + 6, fill=COLOR_QUERY, outline="#FFFFFF", width=2)
        self.create_text(sqx + 10, sqy - 10, text=f"RIDER ({qx:.0f}, {qy:.0f})", fill=COLOR_QUERY, font=("Segoe UI", 9, "bold"), anchor="sw")

    def _draw_dropoff_pin(self) -> None:
        dx, dy = self.dropoff_point
        sdx, sdy = self.world_to_screen(dx, dy)
        self.create_oval(sdx - 5, sdy - 5, sdx + 5, sdy + 5, fill=COLOR_DROPOFF, outline="#FFFFFF", width=2)
        self.create_text(sdx + 8, sdy - 8, text=f"DROPOFF ({dx:.0f}, {dy:.0f})", fill=COLOR_DROPOFF, font=("Segoe UI", 8, "bold"), anchor="sw")

    def _draw_hilbert_curve(self, all_drivers: List[REntry]) -> None:
        if len(all_drivers) < 2:
            return
        sorted_d = sorted(all_drivers, key=lambda d: d.x + d.y * 1000)
        pts = [self.world_to_screen(d.x, d.y) for d in sorted_d]
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            self.create_line(x1, y1, x2, y2, fill="#3B82F6", dash=(2, 4), width=1)

    def _draw_drivers(self, all_drivers: List[REntry]) -> None:
        for driver in all_drivers:
            d_id = driver.driver_id
            sx, sy = self.world_to_screen(driver.x, driver.y)
            status = driver.status
            is_matched = d_id in self.highlighted_drivers
            is_selected = self.selected_driver and self.selected_driver.driver_id == d_id

            if is_matched or is_selected:
                fill_color = COLOR_QUERY
                radius = 8
            elif status == "AVAILABLE":
                fill_color = COLOR_AVAILABLE
                radius = 6
            elif status == "DISPATCHED":
                fill_color = COLOR_DISPATCHED
                radius = 7
            elif status == "ON_TRIP":
                fill_color = COLOR_ON_TRIP
                radius = 7
            else:
                fill_color = COLOR_OFFLINE
                radius = 5

            radius = max(3, int(radius * max(0.8, min(1.4, self.zoom))))

            # Glowing Outer Halo
            if is_matched or is_selected or status in ("DISPATCHED", "ON_TRIP"):
                self.create_oval(sx - (radius + 4), sy - (radius + 4), sx + (radius + 4), sy + (radius + 4), outline=fill_color, width=1)

            # Vehicle Dot Glyph
            self.create_oval(sx - radius, sy - radius, sx + radius, sy + radius, fill=fill_color, outline="#111827", width=1.5)

            # Heading Pointer
            rad = math.radians(driver.heading)
            arrow_len = radius + 6
            hx = sx + arrow_len * math.cos(rad)
            hy = sy + arrow_len * math.sin(rad)
            self.create_line(sx, sy, hx, hy, fill=fill_color, width=2)

            # Driver Label
            if self.show_driver_labels and self.zoom >= 0.75:
                lbl_color = "#FFFFFF" if is_matched else TEXT_SECONDARY
                lbl_font = ("Segoe UI", 8, "bold") if is_matched else ("Segoe UI", 7)
                self.create_text(sx + radius + 3, sy - 2, text=f"{d_id}", fill=lbl_color, font=lbl_font, anchor="w")

    def _draw_driver_inspector(self) -> None:
        d = self.selected_driver
        sx, sy = self.world_to_screen(d.x, d.y)
        card_w, card_h = 170, 95
        cx1, cy1 = sx + 15, sy - 10
        cx2, cy2 = cx1 + card_w, cy1 + card_h

        if cx2 > self.map_width:
            cx1 = sx - card_w - 15
            cx2 = cx1 + card_w

        self.create_rectangle(cx1, cy1, cx2, cy2, fill="#0F172A", outline="#38BDF8", width=1.5)
        self.create_text(cx1 + 8, cy1 + 10, text=f"DRIVER {d.driver_id}", fill="#38BDF8", font=("Segoe UI", 9, "bold"), anchor="nw")
        self.create_text(cx1 + 8, cy1 + 26, text=f"Tier: {d.vehicle_type} | ★{d.rating:.2f}", fill="#F8FAFC", font=("Segoe UI", 8), anchor="nw")
        self.create_text(cx1 + 8, cy1 + 42, text=f"Status: {d.status}", fill=COLOR_AVAILABLE if d.status == "AVAILABLE" else COLOR_DISPATCHED, font=("Segoe UI", 8, "bold"), anchor="nw")
        self.create_text(cx1 + 8, cy1 + 58, text=f"Speed: {d.speed:.0f} km/h | {d.heading:.0f}°", fill="#94A3B8", font=("Segoe UI", 7), anchor="nw")
        self.create_text(cx1 + 8, cy1 + 74, text=f"Coord: ({d.x:.0f}, {d.y:.0f})", fill="#64748B", font=("Segoe UI", 7), anchor="nw")

    def _draw_hud(self, fleet_count: int, tree_height: int, fps: float) -> None:
        hud_x = self.map_width - 190
        hud_y = 12
        self.create_rectangle(hud_x - 10, hud_y - 6, self.map_width - 12, hud_y + 86, fill="#0F172A", outline="#1E293B", width=1)
        self.create_text(hud_x, hud_y + 4, text=f"FLEET: {fleet_count} ACTIVE", fill=COLOR_AVAILABLE, font=("Segoe UI", 8, "bold"), anchor="nw")
        self.create_text(hud_x, hud_y + 20, text=f"R*-TREE HEIGHT: {tree_height}", fill=TEXT_ACCENT, font=("Segoe UI", 8, "bold"), anchor="nw")
        self.create_text(hud_x, hud_y + 36, text=f"FPS: {fps:.1f} | 60Hz Engine", fill="#E2E8F0", font=("Segoe UI", 8), anchor="nw")
        self.create_text(hud_x, hud_y + 52, text=f"ZOOM: {self.zoom:.2f}x | PAN: ({self.pan_x:.0f}, {self.pan_y:.0f})", fill="#94A3B8", font=("Segoe UI", 7), anchor="nw")
        self.create_text(hud_x, hud_y + 68, text="CONTROLS: Scroll=Zoom, Mid=Pan", fill="#64748B", font=("Segoe UI", 7), anchor="nw")
