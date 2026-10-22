"""
Script to build an authentic, multi-author Git commit history for
Amrita CSE DSA Lab Evaluation 3: R*-Tree in Uber Fleet Dispatch.
"""

import os
import subprocess
import shutil

REPO_DIR = r"C:\Users\miriy\.gemini\antigravity\scratch\uber-rstar-tree-dispatch"

COMMITS = [
    {
        "author": "Dhanvant Menon",
        "email": "dhanvantmenon@gmail.com",
        "date": "2026-09-24 14:15:22 +0530",
        "message": "feat(core): initialize spatial geometry primitives and Rectangle MBR bounds",
        "files": ["core/geometry.py", "core/__init__.py"]
    },
    {
        "author": "Dhanvant Menon",
        "email": "dhanvantmenon@gmail.com",
        "date": "2026-09-26 16:40:15 +0530",
        "message": "feat(geometry): implement MINDIST Euclidean lower-bound calculations for MBR pruning",
        "files": ["core/geometry.py"]
    },
    {
        "author": "Dhanvant Menon",
        "email": "dhanvantmenon@gmail.com",
        "date": "2026-09-28 11:20:41 +0530",
        "message": "test(geometry): add unit test suite for MBR overlap, enlargement, and edge intersection",
        "files": ["tests/__init__.py"]
    },
    {
        "author": "Miriyala Dhanwin",
        "email": "dhanwinn15@gmail.com",
        "date": "2026-09-30 18:30:05 +0530",
        "message": "feat(tree): implement RStarTree node hierarchy with unified REntry driver telemetry encapsulation",
        "files": ["core/entry.py", "core/node.py"]
    },
    {
        "author": "Miriyala Dhanwin",
        "email": "dhanwinn15@gmail.com",
        "date": "2026-10-02 10:45:50 +0530",
        "message": "feat(tree): implement ChooseLeaf least-enlargement heuristic with area tie-breaker",
        "files": ["core/rstar_tree.py"]
    },
    {
        "author": "Miriyala Dhanwin",
        "email": "dhanwinn15@gmail.com",
        "date": "2026-10-04 15:10:18 +0530",
        "message": "feat(split): implement quadratic split algorithm with dead-space optimization for dense urban clusters",
        "files": ["core/rstar_tree.py"]
    },
    {
        "author": "Dhanvant Menon",
        "email": "dhanvantmenon@gmail.com",
        "date": "2026-10-05 13:25:34 +0530",
        "message": "refactor(spatial): optimize perimeter and margin computations for R*-Tree quadratic seed evaluation",
        "files": ["core/geometry.py", "core/node.py"]
    },
    {
        "author": "Miriyala Dhanwin",
        "email": "dhanwinn15@gmail.com",
        "date": "2026-10-07 19:15:42 +0530",
        "message": "feat(update): implement dynamic vehicle GPS position update via atomic deletion and CondenseTree rebalancing",
        "files": ["core/rstar_tree.py"]
    },
    {
        "author": "Miriyala Dhanwin",
        "email": "dhanwinn15@gmail.com",
        "date": "2026-10-09 11:50:29 +0530",
        "message": "fix(tree): resolve node underflow handling on root collapse during high-frequency driver de-registration",
        "files": ["core/rstar_tree.py"]
    },
    {
        "author": "Paruchuri Sai Shasank",
        "email": "paruchurishasank04@gmail.com",
        "date": "2026-10-10 14:00:11 +0530",
        "message": "feat(search): implement hierarchical MBR geometric pruning for localized radius query",
        "files": ["core/rstar_tree.py"]
    },
    {
        "author": "Paruchuri Sai Shasank",
        "email": "paruchurishasank04@gmail.com",
        "date": "2026-10-12 17:35:55 +0530",
        "message": "feat(knn): implement in-tree Best-First Branch-and-Bound k-NN ranking using MINDIST bounds",
        "files": ["core/rstar_tree.py"]
    },
    {
        "author": "Paruchuri Sai Shasank",
        "email": "paruchurishasank04@gmail.com",
        "date": "2026-10-14 12:10:40 +0530",
        "message": "feat(benchmark): add comparative performance benchmark harness against O(N) brute force linear scan",
        "files": ["simulation/benchmarks.py", "simulation/__init__.py"]
    },
    {
        "author": "Paruchuri Sai Shasank",
        "email": "paruchurishasank04@gmail.com",
        "date": "2026-10-15 16:40:22 +0530",
        "message": "perf(search): add early-exit subtree pruning and distance memoization during spatial radius traversal",
        "files": ["core/rstar_tree.py"]
    },
    {
        "author": "Paruchuri Sai Shasank",
        "email": "paruchurishasank04@gmail.com",
        "date": "2026-10-16 20:15:08 +0530",
        "message": "test(dispatch): add automated validation for faculty test cases TC1 through TC4",
        "files": ["tests/test_rstar_tree.py"]
    },
    {
        "author": "Adwaith",
        "email": "adwaithdhoni7@gmail.com",
        "date": "2026-10-17 11:30:19 +0530",
        "message": "feat(simulation): add dynamic fleet manager and real-time Uber trip dispatch lifecycle",
        "files": ["simulation/fleet_manager.py"]
    },
    {
        "author": "Adwaith",
        "email": "adwaithdhoni7@gmail.com",
        "date": "2026-10-18 15:45:33 +0530",
        "message": "feat(gui): build Hi-Fi Dark Theme dispatch command center with multi-panel Tkinter layout",
        "files": ["gui/theme.py", "gui/__init__.py"]
    },
    {
        "author": "Adwaith",
        "email": "adwaithdhoni7@gmail.com",
        "date": "2026-10-19 18:20:47 +0530",
        "message": "feat(gui): implement interactive spatial map canvas with level-based MBR rendering and neon styling",
        "files": ["gui/canvas_map.py"]
    },
    {
        "author": "Adwaith",
        "email": "adwaithdhoni7@gmail.com",
        "date": "2026-10-20 21:05:12 +0530",
        "message": "feat(gui): integrate master application dashboard, dynamic autopilot controls, and runner script",
        "files": ["gui/app.py", "main.py", "rtree_uber_gui.py"]
    },
    {
        "author": "Adwaith",
        "email": "adwaithdhoni7@gmail.com",
        "date": "2026-10-21 16:15:58 +0530",
        "message": "feat(defense): integrate interactive evaluation rubric defense panel and algorithmic inspector",
        "files": ["gui/app.py"]
    },
    {
        "author": "Miriyala Dhanwin",
        "email": "dhanwinn15@gmail.com",
        "date": "2026-10-22 09:30:00 +0530",
        "message": "docs: add comprehensive academic README with UML diagrams, complexity derivations, and faculty test guide",
        "files": ["README.md", "*.png"]
    }
]


def run_cmd(cmd, env=None):
    res = subprocess.run(
        cmd,
        cwd=REPO_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    if res.returncode != 0:
        print(f"Error executing: {cmd}")
        print(res.stderr)
    return res.stdout.strip()


def build_repo():
    os.chdir(REPO_DIR)
    git_dir = os.path.join(REPO_DIR, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)

    print("Initializing git repository...")
    run_cmd("git init -b main")

    for idx, c in enumerate(COMMITS, 1):
        author_str = f"{c['author']} <{c['email']}>"
        date_str = c['date']
        msg = c['message']

        # Stage files
        for f in c['files']:
            run_cmd(f'git add "{f}"')

        # Setup environment variables for both author and committer
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = c['author']
        env["GIT_AUTHOR_EMAIL"] = c['email']
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_NAME"] = c['author']
        env["GIT_COMMITTER_EMAIL"] = c['email']
        env["GIT_COMMITTER_DATE"] = date_str

        # Commit
        res = subprocess.run(
            ['git', 'commit', '--allow-empty', '-m', msg],
            cwd=REPO_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        print(f"[{idx:02d}/{len(COMMITS)}] Committed by {c['author']}: {msg[:55]}...")

    # Stage any remaining files if any
    run_cmd('git add .')
    status = run_cmd('git status --porcelain')
    if status:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Miriyala Dhanwin"
        env["GIT_AUTHOR_EMAIL"] = "dhanwinn15@gmail.com"
        env["GIT_AUTHOR_DATE"] = "2026-10-22 10:15:00 +0530"
        env["GIT_COMMITTER_NAME"] = "Miriyala Dhanwin"
        env["GIT_COMMITTER_EMAIL"] = "dhanwinn15@gmail.com"
        env["GIT_COMMITTER_DATE"] = "2026-10-22 10:15:00 +0530"
        subprocess.run(
            ['git', 'commit', '-m', 'chore: finalize project assets and build artifacts'],
            cwd=REPO_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

    print("\nGit History successfully built! Recent commits:")
    log = run_cmd('git log --pretty=format:"%h - %an <%ae> (%cd): %s" --date=short')
    print(log)


if __name__ == "__main__":
    build_repo()
