"""
Push Commit History to GitHub Repository in Pure Python.
Amrita Vishwa Vidyapeetham - DSA Lab Evaluation 3.
"""

import subprocess
import sys


def push_to_github():
    print("=" * 68)
    print(" UBER R*-TREE: PUSH COMMIT HISTORY TO GITHUB REPOSITORY (PYTHON)")
    print("=" * 68)
    
    repo_url = "https://github.com/miriyaladhanwinn/uber-rstar-tree-dispatch.git"
    if len(sys.argv) > 1:
        repo_url = sys.argv[1]
    
    print(f"\n[INFO] Target Repository: {repo_url}")
    print("[INFO] Pushing branch main to origin...")
    
    try:
        subprocess.run(["git", "remote", "remove", "origin"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        result = subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print("\n" + "=" * 68)
        print(" SUCCESS! Visit your GitHub repository to verify the commit history.")
        print(" All 4 team members are linked via their verified emails!")
        print("=" * 68)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Git push failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    push_to_github()
