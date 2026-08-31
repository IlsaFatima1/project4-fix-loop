"""Initialize the project-4 git repository for the fix-loop demonstration.

Creates the git repo (if needed), commits the buggy baseline on `main`,
and verifies the base test suite fails (proving the bug exists).

Usage:
    python demo/init_repo.py
"""

import subprocess
import sys
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def sh(args, cwd=REPO, check=True):
    print(f"    $ git {' '.join(args)}")
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, check=False)
    if r.stdout.strip():
        print(r.stdout.strip())
    if check and r.returncode != 0:
        print(r.stderr)
        sys.exit(f"git failed: {args}")
    return r


def main():
    os.makedirs(os.path.join(REPO, "src"), exist_ok=True)
    os.makedirs(os.path.join(REPO, "tests"), exist_ok=True)
    os.makedirs(os.path.join(REPO, "skills"), exist_ok=True)

    if not os.path.isdir(os.path.join(REPO, ".git")):
        print("Initializing git repository...")
        sh(["init", "-b", "main"])

    # Ensure a clean git identity so commits work in this repo only.
    for key, val in (("user.name", "Fix Loop Demo"),
                     ("user.email", "demo@example.com")):
        sh(["config", "user." + key, val])
    sh(["config", "commit.gpgsign", "false"], check=False)

    if sh(["rev-parse", "--verify", "HEAD"], check=False).returncode != 0:
        print("\nCreating baseline (buggy) commit on main...")
        sh(["add", "-A"])
        sh(["commit", "-m", "baseline: buggy calculate_total (price+quantity)"])
    else:
        print("\nBaseline commit already exists.")

    print("\nVerifying the bug is real: the baseline test suite should FAIL.")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=REPO,
                       capture_output=True, text=True)
    print(r.stdout)
    if r.returncode == 0:
        print("!! Expected baseline tests to fail (the bug should be live).")
        sys.exit(1)
    print("Confirmed: bug is present on main (tests fail).\n")


if __name__ == "__main__":
    main()
