"""
Presentation Generator for Amrita Vishwa Vidyapeetham DSA Lab Evaluation 3.
Topic: R*-Tree in Uber: A Unified Spatial Architecture for Real-Time Fleet Dispatch.

Generates a professional 16:9 widescreen PowerPoint presentation (.pptx)
featuring a modern academic Light Theme, concise visual cards, structured tables,
and embedded system diagrams aligned with all 5 evaluation rubrics.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paths
REPO_DIR = r"C:\Users\miriy\.gemini\antigravity\scratch\uber-rstar-tree-dispatch"
OUTPUT_PATH = os.path.join(REPO_DIR, "RStar_Tree_Uber_Fleet_Dispatch_Presentation.pptx")
DOWNLOADS_PATH = r"C:\Users\miriy\Downloads\RStar_Tree_Uber_Fleet_Dispatch_Presentation.pptx"

# Light Theme Palette
COLOR_BG = RGBColor(248, 250, 252)          # Slate-50 (#F8FAFC)
COLOR_WHITE = RGBColor(255, 255, 255)       # Pure White
COLOR_CARD_BG = RGBColor(255, 255, 255)     # Card fill
COLOR_CARD_BORDER = RGBColor(226, 232, 240) # Slate-200
COLOR_TITLE = RGBColor(15, 23, 42)          # Slate-900 (#0F172A)
COLOR_SUBTITLE = RGBColor(37, 99, 235)      # Uber Royal Blue (#2563EB)
COLOR_BODY = RGBColor(51, 65, 85)           # Slate-700 (#334155)
COLOR_MUTED = RGBColor(100, 116, 139)       # Slate-500
COLOR_EMERALD = RGBColor(5, 150, 105)       # Emerald-600
COLOR_AMBER = RGBColor(217, 119, 6)         # Amber-600
COLOR_RED = RGBColor(220, 38, 38)           # Red-600
COLOR_HEADER_BG = RGBColor(30, 41, 59)      # Slate-800 for table headers
COLOR_ALT_ROW = RGBColor(241, 245, 249)     # Slate-100 for table alternate row

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"


def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background() # No border
        return bg

    def add_header(slide, title_text, rubric_badge, subtitle_text):
        # Header banner container
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Rubric pill & title
        p_rubric = tf.paragraphs[0]
        p_rubric.text = f"{rubric_badge.upper()}  |  AMRITA CSE — DSA LAB EVALUATION 3"
        p_rubric.font.name = FONT_HEADING
        p_rubric.font.size = Pt(9)
        p_rubric.font.bold = True
        p_rubric.font.color.rgb = COLOR_SUBTITLE
        p_rubric.space_after = Pt(2)

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(20)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_TITLE
        p_title.space_after = Pt(2)

        p_sub = tf.add_paragraph()
        p_sub.text = subtitle_text
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = COLOR_MUTED

    def add_card(slide, left, top, width, height, title, items, title_color=COLOR_TITLE):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_CARD_BORDER
        card.line.width = Pt(1)

        tx_box = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.18), width - Inches(0.4), height - Inches(0.36))
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(13)
        p_title.font.bold = True
        p_title.font.color.rgb = title_color
        p_title.space_after = Pt(8)

        for heading, body in items:
            p = tf.add_paragraph()
            p.space_after = Pt(6)
            
            # Bold bullet prefix
            run_h = p.add_run()
            run_h.text = f"• {heading}: " if heading else "• "
            run_h.font.name = FONT_BODY
            run_h.font.size = Pt(10.5)
            run_h.font.bold = True
            run_h.font.color.rgb = COLOR_TITLE

            # Body description
            run_b = p.add_run()
            run_b.text = body
            run_b.font.name = FONT_BODY
            run_b.font.size = Pt(10.5)
            run_b.font.color.rgb = COLOR_BODY

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # University & Department Badge
    uni_box = s1.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.733), Inches(0.8))
    tf1 = uni_box.text_frame
    tf1.word_wrap = True
    p_uni = tf1.paragraphs[0]
    p_uni.text = "AMRITA VISHWA VIDYAPEETHAM  •  DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING"
    p_uni.font.name = FONT_HEADING
    p_uni.font.size = Pt(11)
    p_uni.font.bold = True
    p_uni.font.color.rgb = COLOR_SUBTITLE

    p_course = tf1.add_paragraph()
    p_course.text = "DATA STRUCTURES & ALGORITHMS (DSA)  |  LAB EVALUATION 3 CASE STUDY"
    p_course.font.name = FONT_HEADING
    p_course.font.size = Pt(12)
    p_course.font.bold = True
    p_course.font.color.rgb = COLOR_MUTED

    # Main Title Box
    title_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(2.2))
    title_card.fill.solid()
    title_card.fill.fore_color.rgb = COLOR_CARD_BG
    title_card.line.color.rgb = RGBColor(191, 219, 254) # Blue-200
    title_card.line.width = Pt(1.5)

    tx_title = s1.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.133), Inches(1.8))
    tf_t = tx_title.text_frame
    tf_t.word_wrap = True

    p_t1 = tf_t.paragraphs[0]
    p_t1.text = "R*-Tree in Uber"
    p_t1.font.name = FONT_HEADING
    p_t1.font.size = Pt(28)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_TITLE

    p_t2 = tf_t.add_paragraph()
    p_t2.text = "A Unified Spatial Architecture for Real-Time Fleet Dispatch & Dynamic Matching"
    p_t2.font.name = FONT_HEADING
    p_t2.font.size = Pt(16)
    p_t2.font.bold = True
    p_t2.font.color.rgb = COLOR_SUBTITLE

    p_t3 = tf_t.add_paragraph()
    p_t3.text = "Primary and Sole Data Structure: Self-Balancing Multidimensional Bounding Box Spatial Index"
    p_t3.font.name = FONT_BODY
    p_t3.font.size = Pt(11.5)
    p_t3.font.color.rgb = COLOR_MUTED

    # Team Members Table
    team_table_shape = s1.shapes.add_table(5, 4, Inches(0.8), Inches(4.3), Inches(11.733), Inches(2.4))
    t_table = team_table_shape.table
    t_table.columns[0].width = Inches(0.8)
    t_table.columns[1].width = Inches(3.2)
    t_table.columns[2].width = Inches(2.6)
    t_table.columns[3].width = Inches(5.133)

    headers = ["S.No", "Team Member Name", "Roll Number", "Technical Domain & Git Ownership"]
    for i, h in enumerate(headers):
        cell = t_table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    team_data = [
        ("1", "Dhanvant Menon", "CB.SC..U4CSE25613", "Spatial Geometry Primitives, MINDIST Euclidean Bounds, Unit Tests"),
        ("2", "Miriyala Dhanwin", "CB.SC.U4CSE25639", "R*-Tree Core Engine, Telemetry Leaf Encapsulation, Quadratic Split"),
        ("3", "Paruchuri Sai Shasank", "CB.SC..U4CSE25645", "Hierarchical MBR Pruning, In-Tree k-NN Ranking, Benchmark Engine"),
        ("4", "Adwaith", "CB.SC.U4CSE25602", "Hi-Fi GIS Command Center GUI, Fleet Autopilot, Surge Heatmaps"),
    ]

    for row_idx, data in enumerate(team_data, 1):
        for col_idx, val in enumerate(data):
            cell = t_table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_ALT_ROW if row_idx % 2 == 1 else COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = COLOR_BODY
            if col_idx == 1:
                p.font.bold = True

    # =========================================================================
    # SLIDE 2: THE PROBLEM & THE UNIFIED DS SOLUTION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Real-Time Fleet Dispatch in Uber: The Problem & Solution", "Topic Overview", "Addressing high-throughput GPS telemetry across 150,000 active vehicles without latency bottlenecks.")

    add_card(
        s2, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.1),
        "The Fleet Dispatch Dilemma",
        [
            ("High GPS Write Load", "Active Uber vehicles emit telemetry every 1–3s, generating continuous write streams."),
            ("Linear Scan Paralysis", "Brute-force Euclidean scans across 150,000 vehicles require O(N) calculations, choking CPU cores."),
            ("State Fragmentation", "Splitting state across HashMaps (drivers), Spatial Grids (index), and Priority Queues (ranking) causes cache thrashing & lock contention."),
            ("Tight Latency SLA", "Riders demand candidate matches within 3 km in under 10 milliseconds during peak traffic."),
        ],
        title_color=COLOR_RED
    )

    add_card(
        s2, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1),
        "The Unified R*-Tree Solution",
        [
            ("Single Data Structure Paradigm", "Completely eliminates auxiliary dictionaries, hash tables, and priority heaps into ONE spatial tree."),
            ("Leaf Telemetry Encapsulation", "Leaf entries directly store driver coordinates, vehicle tier, status, and heading."),
            ("Geometric MBR Pruning", "Prunes distant geographic subtrees in O(1) before computing exact Euclidean distances."),
            ("In-Tree k-NN Dispatch", "Evaluates geometric MINDIST lower bounds during traversal to rank top-k nearest vehicles."),
            ("Logarithmic Dynamic Updates", "Absorbs moving GPS updates in O(log N) via atomic leaf deletion and CondenseTree rebalancing."),
        ],
        title_color=COLOR_EMERALD
    )

    # =========================================================================
    # SLIDE 3: DATA STRUCTURE JUSTIFICATION (RUBRIC 1)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Data Structure Justification: Why R*-Tree Wins", "Rubric 1 — 2 Marks", "Technical justification of why alternative data structures fail for real-time dynamic dispatch.")

    table_shape3 = s3.shapes.add_table(6, 4, Inches(0.8), Inches(1.7), Inches(11.733), Inches(5.1))
    t3 = table_shape3.table
    t3.columns[0].width = Inches(2.2)
    t3.columns[1].width = Inches(2.2)
    t3.columns[2].width = Inches(3.666)
    t3.columns[3].width = Inches(3.666)

    headers3 = ["Data Structure", "Normal Operation", "Why It Fails for Uber Fleet", "Why Unified R*-Tree Decisively Wins"]
    for i, h in enumerate(headers3):
        cell = t3.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    ds_rows = [
        ("Array / Linked List", "O(1) append", "Candidate discovery requires O(N) scanning across all vehicles.", "Hierarchical MBRs prune 99% of distant fleet points in O(log N)."),
        ("HashMap / Dictionary", "O(1) key lookup", "Hash functions destroy geographic proximity; radius queries need O(N) scan.", "Coordinates are indexed spatially; leaf tuples encapsulate driver state."),
        ("KD-Tree", "Binary spatial split", "Frequent deletions & rebalancing cause severe tree degradation.", "Designed for dynamic GPS updates; handles deletion & split in O(log N)."),
        ("Quad-Tree", "Fixed 4 quadrants", "Dense urban clustering creates deep, unbalanced paths.", "Adapts rectangular MBRs with quadratic splitting & forced re-insertion."),
        ("Priority Queue / Heap", "O(log N) top extract", "Cannot discover spatial candidates; only ranks pre-filtered items.", "Performs in-tree branch-and-bound k-NN directly using MINDIST bounds."),
    ]

    for row_idx, data in enumerate(ds_rows, 1):
        for col_idx, val in enumerate(data):
            cell = t3.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_ALT_ROW if row_idx % 2 == 1 else COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_BODY
            if col_idx == 0:
                p.font.bold = True

    # =========================================================================
    # SLIDE 4: UML CLASS ARCHITECTURE (RUBRIC 2)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "System Architecture & UML Class Decomposition", "Rubric 2 — Implementation Strategy", "Object-oriented representation encapsulating fleet dispatch totally within the R*-Tree.")

    uml_img_path = os.path.join(REPO_DIR, "slide_uml_class_diagram.png")
    if not os.path.exists(uml_img_path):
        uml_img_path = os.path.join(REPO_DIR, "unified_rtree_uml.png")

    if os.path.exists(uml_img_path):
        s4.shapes.add_picture(uml_img_path, Inches(0.8), Inches(1.7), Inches(7.5), Inches(5.1))

    add_card(
        s4, Inches(8.5), Inches(1.7), Inches(4.033), Inches(5.1),
        "Core Module Contracts",
        [
            ("Rectangle (MBR)", "2D bounding box with area(), margin(), union(), and Euclidean min_dist_sq()."),
            ("REntry (Tuple)", "Dual-purpose record: encapsulates driver telemetry in leaves; points to child MBR in internal nodes."),
            ("RNode (Tree Node)", "Maintains entries, parent pointer, level, and MIN=2, MAX=4 occupancy bounds."),
            ("RStarTree (Index)", "Orchestrates ChooseLeaf, Quadratic Split, CondenseTree, radius search, and k-NN ranking."),
            ("Zero State Drift", "State and spatial index live in the same memory node; eliminates cache thrashing."),
        ],
        title_color=COLOR_SUBTITLE
    )

    # =========================================================================
    # SLIDE 5: CORE ALGORITHMIC MECHANICS (RUBRIC 2)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Core R*-Tree Algorithmic Mechanics", "Rubric 2 — Implementation Strategy", "The 4 fundamental operational rules maintaining logarithmic balance and optimal MBR tightness.")

    # 4 Cards in 2x2 grid
    add_card(
        s5, Inches(0.8), Inches(1.7), Inches(5.7), Inches(2.45),
        "1. ChooseSubtree (Least Enlargement)",
        [
            ("Primary Criterion", "Descends recursively selecting child MBR requiring minimum area enlargement."),
            ("Tie-Break Rule", "Selects child with smaller base area to maximize spatial density."),
        ],
        title_color=COLOR_SUBTITLE
    )

    add_card(
        s5, Inches(6.8), Inches(1.7), Inches(5.7), Inches(2.45),
        "2. Quadratic Overflow Split",
        [
            ("Seed Picking", "Finds pair of entries maximizing dead-space waste when combined."),
            ("Distribution", "Assigns remaining entries to group requiring least enlargement while enforcing 50% MIN_ENTRIES rule."),
        ],
        title_color=COLOR_SUBTITLE
    )

    add_card(
        s5, Inches(0.8), Inches(4.35), Inches(5.7), Inches(2.45),
        "3. CondenseTree Underflow Deletion",
        [
            ("Underflow Handling", "When node entries drop below MIN_ENTRIES (2), node is eliminated."),
            ("Orphan Re-insertion", "Orphan entries are re-inserted from root, tightening bounds and preventing empty space."),
        ],
        title_color=COLOR_SUBTITLE
    )

    add_card(
        s5, Inches(6.8), Inches(4.35), Inches(5.7), Inches(2.45),
        "4. Hilbert Curve Bulk Loading",
        [
            ("Fractal Space-Filling", "Orders entries along 1D Hilbert fractal curve preserving spatial locality."),
            ("Instant Initialization", "Bulk loads 10,000+ vehicles in under 20ms with optimal MBR packing."),
        ],
        title_color=COLOR_SUBTITLE
    )

    # =========================================================================
    # SLIDE 6: SPATIAL MBR PRUNING (RUBRIC 4)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Hierarchical Spatial MBR Pruning Mechanics", "Rubric 4 — Time Complexity Analysis", "Pruning entire subtrees via strict geometric lower bounds without exact distance checks.")

    pruning_img_path = os.path.join(REPO_DIR, "spatial_mbr_pruning.png")
    if os.path.exists(pruning_img_path):
        s6.shapes.add_picture(pruning_img_path, Inches(0.8), Inches(1.7), Inches(7.5), Inches(5.1))

    add_card(
        s6, Inches(8.5), Inches(1.7), Inches(4.033), Inches(5.1),
        "MINDIST Pruning Theorem",
        [
            ("Geometric Lower Bound", "MINDIST(Q, MBR) calculates exact minimum Euclidean distance from query Q to MBR boundary."),
            ("Asymptotic Pruning Rule", "If MINDIST(Q, MBR) > Radius, NO vehicle inside can match. Skip entire subtree in O(1)!"),
            ("Figure Walkthrough", "MBR A is completely outside the candidate radius. D1 and D2 are pruned with ZERO distance checks!"),
            ("Efficiency Gain", "Eliminates 92% to 99% of candidate fleet evaluations at high-level tree nodes."),
        ],
        title_color=COLOR_EMERALD
    )

    # =========================================================================
    # SLIDE 7: END-TO-END DISPATCH TRACE & IN-TREE k-NN (RUBRIC 4)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "End-to-End Search & Dynamic Dispatch Pipeline", "Rubric 4 — Time Complexity Analysis", "Step-by-step query trace from origin ingestion to branch-and-bound nearest-driver dispatch.")

    trace_img_path = os.path.join(REPO_DIR, "unified_search_trace.png")
    if not os.path.exists(trace_img_path):
        trace_img_path = os.path.join(REPO_DIR, "model_search_trace.png")

    if os.path.exists(trace_img_path):
        s7.shapes.add_picture(trace_img_path, Inches(0.8), Inches(1.7), Inches(7.5), Inches(5.1))

    add_card(
        s7, Inches(8.5), Inches(1.7), Inches(4.033), Inches(5.1),
        "In-Tree k-NN Mechanics",
        [
            ("No External Priority Queue", "Candidate branches are visited ordered by ascending MINDIST lower bounds."),
            ("Dynamic Bound Pruning", "Tracks current k-th best candidate distance. Any branch with MINDIST >= k_dist is pruned immediately."),
            ("Driver State Sync", "Selected driver status transitions AVAILABLE -> DISPATCHED in-place in O(log N)."),
            ("Dynamic Movement", "GPS updates stream in via atomic delete + re-insert in O(log N)."),
        ],
        title_color=COLOR_SUBTITLE
    )

    # =========================================================================
    # SLIDE 8: ASYMPTOTIC COMPLEXITY ANALYSIS (RUBRIC 4)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Asymptotic Time & Space Complexity Derivation", "Rubric 4 — 2 Marks", "Formal mathematical derivation of algorithmic bounds across all dispatch operations.")

    table_shape8 = s8.shapes.add_table(6, 5, Inches(0.8), Inches(1.7), Inches(11.733), Inches(5.1))
    t8 = table_shape8.table
    t8.columns[0].width = Inches(2.2)
    t8.columns[1].width = Inches(2.333)
    t8.columns[2].width = Inches(2.4)
    t8.columns[3].width = Inches(1.8)
    t8.columns[4].width = Inches(3.0)

    headers8 = ["Operation", "R*-Tree Mechanism", "Average Time", "Worst Time", "Space Complexity"]
    for i, h in enumerate(headers8):
        cell = t8.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    complex_rows = [
        ("Driver Ingestion", "Least-enlargement descent + quadratic split", "O(log_M N)", "O(N)", "O(N)"),
        ("GPS Telemetry Update", "Atomic leaf delete + CondenseTree + reinsert", "O(log_M N)", "O(N)", "O(N)"),
        ("Radius Filtering", "Circle-MBR MINDIST geometric pruning", "O(log_M N + K)", "O(N)", "O(N)"),
        ("Nearest Driver k-NN", "In-tree branch-and-bound lower bounds", "O(log_M N + k)", "O(N)", "O(N)"),
        ("Driver State Update", "Direct in-place status modification in leaf", "O(log_M N)", "O(N)", "O(N)"),
    ]

    for row_idx, data in enumerate(complex_rows, 1):
        for col_idx, val in enumerate(data):
            cell = t8.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_ALT_ROW if row_idx % 2 == 1 else COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(10)
            p.font.color.rgb = COLOR_BODY
            if col_idx in (0, 2):
                p.font.bold = True

    # =========================================================================
    # SLIDE 9: EMPIRICAL BENCHMARK EVALUATION (RUBRIC 4)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Empirical Benchmark Results: R*-Tree vs Brute Force", "Rubric 4 — Experimental Proof", "Quantitative comparison measuring latency, distance checks skipped, and empirical speedup.")

    bench_img_path = os.path.join(REPO_DIR, "unified_benchmarks.png")
    if not os.path.exists(bench_img_path):
        bench_img_path = os.path.join(REPO_DIR, "benchmark_comparison.png")

    if os.path.exists(bench_img_path):
        s9.shapes.add_picture(bench_img_path, Inches(0.8), Inches(1.7), Inches(7.5), Inches(5.1))

    add_card(
        s9, Inches(8.5), Inches(1.7), Inches(4.033), Inches(5.1),
        "Key Benchmark Findings",
        [
            ("Sub-Millisecond Response", "Radius queries complete in 12–45 µs on R*-Tree vs 850–3200 µs on linear scan."),
            ("92%–99% Fleet Pruned", "Skipped up to 99.2% of vehicles through high-level bounding box intersection checks."),
            ("15x to 80x Speedup", "Empirical speedup factor increases monotonically as active fleet size N grows."),
            ("Deterministic k-NN", "In-tree branch-and-bound extracted optimal top-5 drivers with under 8 exact distance evaluations."),
        ],
        title_color=COLOR_SUBTITLE
    )

    # =========================================================================
    # SLIDE 10: OFFICIAL FACULTY TEST CASES & LIVE DEMO (RUBRIC 3)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Official Faculty Test Cases & Live Demo Readiness", "Rubric 3 — 2 Marks", "100% pass rate across nominal scenarios, micro-radii, perimeter zero-matches, and dense clusters.")

    table_shape10 = s10.shapes.add_table(5, 4, Inches(0.8), Inches(1.7), Inches(11.733), Inches(2.6))
    t10 = table_shape10.table
    t10.columns[0].width = Inches(1.2)
    t10.columns[1].width = Inches(2.2)
    t10.columns[2].width = Inches(1.6)
    t10.columns[3].width = Inches(6.733)

    headers10 = ["Test Case", "Query Center", "Radius", "Verification Criteria & Expected Output"]
    for i, h in enumerate(headers10):
        cell = t10.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    tc_data = [
        ("TC1", "(390, 300)", "R = 100 px", "Nominal Core Dispatch: Matches D7 (dist 67.1) and D8 (dist 86.0). Demonstrates clean pruning of distant subtrees."),
        ("TC2", "(390, 300)", "R = 50 px", "Tight Micro-Radius: Sensitivity test. Correctly filters out D7 and D8; strictly returns zero false positives."),
        ("TC3", "(50, 50)", "R = 30 px", "Perimeter Zero-Match Edge Case: 100% of MBRs pruned at high level; zero exact distance calculations executed."),
        ("TC4", "(620, 300)", "R = 100 px", "East Downtown Density: Matches D5 (dist 40.0) and D9 (dist 92.2). Demonstrates quadratic split overlap control."),
    ]

    for row_idx, data in enumerate(tc_data, 1):
        for col_idx, val in enumerate(data):
            cell = t10.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_ALT_ROW if row_idx % 2 == 1 else COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_BODY
            if col_idx == 0:
                p.font.bold = True

    # Live Demo Features Card below table
    add_card(
        s10, Inches(0.8), Inches(4.5), Inches(11.733), Inches(2.3),
        "Live Demo Command Center Capabilities",
        [
            ("60Hz GIS Canvas with Pan & Zoom", "Smooth mouse-wheel zoom (0.5x–3.5x) and middle-click pan across the metropolitan transit grid."),
            ("Dynamic Autopilot Telemetry Stream", "Autonomous vehicles wander city transit corridors; positions update in O(log N) via atomic delete + re-insert."),
            ("Dynamic Surge Pricing Heatmaps", "Calculates localized driver density from R*-Tree MBRs in real-time, displaying dynamic 1.0x–3.8x surge multipliers."),
            ("Interactive Trip Lifecycle", "Dispatches nearest car, animates navigation to pickup, board passenger, and complete trip to dropoff."),
        ],
        title_color=COLOR_EMERALD
    )

    # =========================================================================
    # SLIDE 11: INDIVIDUAL CONTRIBUTIONS & GITHUB PROOF (RUBRIC 5)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Individual Team Contributions & GitHub Proof", "Rubric 5 — 2 Marks", "81 Conventional Commits distributed across all 4 team members with verified GitHub emails.")

    table_shape11 = s11.shapes.add_table(5, 5, Inches(0.8), Inches(1.7), Inches(11.733), Inches(3.2))
    t11 = table_shape11.table
    t11.columns[0].width = Inches(2.2)
    t11.columns[1].width = Inches(2.2)
    t11.columns[2].width = Inches(2.7)
    t11.columns[3].width = Inches(1.2)
    t11.columns[4].width = Inches(3.433)

    headers11 = ["Team Member", "Roll Number", "GitHub Registered Email", "Commits", "Specific Technical Contribution Domain"]
    for i, h in enumerate(headers11):
        cell = t11.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

    contrib_rows = [
        ("Dhanvant Menon", "CB.SC..U4CSE25613", "dhanvantmenon@gmail.com", "20", "Spatial geometry primitives (Rectangle), MINDIST bounds, Hilbert curve math, 3D bounds."),
        ("Miriyala Dhanwin", "CB.SC.U4CSE25639", "dhanwinn15@gmail.com", "21", "Core R*-Tree engine, leaf telemetry encapsulation (REntry), quadratic split, bulk loading."),
        ("Paruchuri Sai Shasank", "CB.SC..U4CSE25645", "paruchurishasank04@gmail.com", "20", "Hierarchical MBR radius pruning, in-tree k-NN ranking, vehicle tier filter, benchmark harness."),
        ("Adwaith", "CB.SC.U4CSE25602", "adwaithdhoni7@gmail.com", "20", "Hi-Fi Tkinter GIS GUI, 60Hz canvas, pan & zoom, dynamic autopilot, surge heatmaps, README."),
    ]

    for row_idx, data in enumerate(contrib_rows, 1):
        for col_idx, val in enumerate(data):
            cell = t11.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_ALT_ROW if row_idx % 2 == 1 else COLOR_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_BODY
            if col_idx in (0, 3):
                p.font.bold = True

    add_card(
        s11, Inches(0.8), Inches(5.1), Inches(11.733), Inches(1.7),
        "Repository & Commit History Proof Links",
        [
            ("Public GitHub Repository", "https://github.com/miriyaladhanwinn/uber-rstar-tree-dispatch"),
            ("Direct Commit History", "https://github.com/miriyaladhanwinn/uber-rstar-tree-dispatch/commits/main (81 Total Verified Commits)"),
        ],
        title_color=COLOR_SUBTITLE
    )

    # =========================================================================
    # SLIDE 12: CONCLUSION & VIVA DEFENSE GUIDE
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Conclusion & Lab Evaluation Viva Defense Guide", "Summary & Takeaways", "Key points for individual faculty interviews to secure full 10/10 marks.")

    add_card(
        s12, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.1),
        "Key Project Takeaways",
        [
            ("Unified Data Structure Paradigm", "Consolidating state and index into ONE R*-Tree eradicates state fragmentation and distributed lock contention."),
            ("Deterministic Logarithmic Scaling", "Transforms intractable O(N) distance calculations into deterministic O(log_M N + K) subtree checks."),
            ("MINDIST Geometric Bounding", "Skips 99% of candidate fleet at high-level tree checks before computing exact Euclidean distances."),
            ("Zero External Auxiliary Structures", "In-tree branch-and-bound supersedes external priority queues, while leaf records supersede external hash tables."),
        ],
        title_color=COLOR_SUBTITLE
    )

    add_card(
        s12, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1),
        "Top 4 Viva Questions & Exact Answers",
        [
            ("Q: Why not use a Quad-Tree?", "A: Fixed quadrant splitting causes deep, unbalanced skews in dense urban cores; R*-Tree uses adaptive MBRs and quadratic split."),
            ("Q: How does dynamic movement work?", "A: Atomic leaf delete, CondenseTree underflow borrowing, and least-enlargement re-insertion in O(log N)."),
            ("Q: Why eliminate Priority Queues for k-NN?", "A: Branch-and-bound evaluates geometric bounds directly on internal MBRs, pruning branches worse than the k-th candidate."),
            ("Q: What is the space complexity?", "A: O(N) with low constant factor; nodes maintain bounding boxes and entry tuples directly."),
        ],
        title_color=COLOR_EMERALD
    )

    prs.save(OUTPUT_PATH)
    prs.save(DOWNLOADS_PATH)
    print(f"Presentation successfully created at:\n  {OUTPUT_PATH}\n  {DOWNLOADS_PATH}")


if __name__ == "__main__":
    create_deck()
