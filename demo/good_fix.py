"""Demonstration — Case 1: GOOD FIX.

Flow:
    Bug found
      -> Implementer fixes it on a branch
      -> Reviewer independently checks -> PASS
      -> PR opened

Usage:
    python demo/good_fix.py
"""

import subprocess
import sys
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKTREE = os.path.join(REPO, ".worktrees/good_fix")
PR_FILE = os.path.join(REPO, "pull_requests", "fix-good_fix.md")
PROJECT_TESTS_DIR = os.path.join(REPO, "tests")


def run(args, fail_ok=False):
    r = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    for line in out.splitlines():
        print("   |", line)
    if r.returncode != 0 and not fail_ok:
        raise SystemExit(f"step failed: {' '.join(args)}")
    return r


def main():
    print("#" * 60)
    print("# DEMONSTRATION 1 — GOOD FIX (expect reviewer PASS, PR opened)")
    print("#" * 60)

    bug_patch = os.path.join(REPO, "fixes", "good_fix.patch")

    print("\n--- Step 1: Implementer fixes the bug on its own branch ---")
    run([sys.executable, os.path.join(REPO, "implementer", "implementer.py"),
         "good_fix", bug_patch])

    print("\n--- Step 2: Reviewer independently checks the fix ---")
    r = run([sys.executable, os.path.join(REPO, "reviewer", "reviewer.py"),
             "fix/good_fix"], fail_ok=True)
    verdict = "PASS" if r.returncode == 0 else "FAIL"

    print("\n--- Step 3: Open a PR (only if reviewer returned PASS) ---")
    run([sys.executable, os.path.join(REPO, "pr", "pr_manager.py"),
         "fix/good_fix", verdict], fail_ok=(verdict != "PASS"))

    print("\n--- Results ---")
    pr_created = os.path.exists(PR_FILE)
    if verdict == "PASS" and pr_created:
        print("GOOD FIX -> PASS -> PR CREATED ✓")
    else:
        print("ERROR: expected PASS and a PR for the good fix.")
        sys.exit(1)

    # Clean up the review worktree so re-runs stay tidy.
    if os.path.exists(WORKTREE):
        subprocess.run(["git", "worktree", "remove", "--force", WORKTREE],
                       cwd=REPO, capture_output=True)


if __name__ == "__main__":
    main()
