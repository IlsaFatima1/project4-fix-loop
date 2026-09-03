"""Demonstration — Case 2: DELIBERATELY BAD FIX.

The bad fix appears to fix the one obvious test case but breaks other
valid cases. The reviewer must catch this and return FAIL, so that no PR
is opened.

Flow:
    Implementer
      -> Bad fix
      -> Reviewer -> FAIL (with reasons)
      -> No PR

Usage:
    python demo/bad_fix.py
"""

import subprocess
import sys
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKTREE = os.path.join(REPO, ".worktrees/bad_fix")
PR_FILE = os.path.join(REPO, "pull_requests", "fix-bad_fix.md")


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
    print("# DEMONSTRATION 2 — DELIBERATELY BAD FIX (expect reviewer FAIL, no PR)")
    print("#" * 60)

    bug_patch = os.path.join(REPO, "fixes", "bad_fix.patch")

    print("\n--- Step 1: Implementer applies the (bad) fix on its own branch ---")
    run([sys.executable, os.path.join(REPO, "implementer", "implementer.py"),
         "bad_fix", bug_patch])

    print("\n--- Step 2: Reviewer independently checks the fix ---")
    r = run([sys.executable, os.path.join(REPO, "reviewer", "reviewer.py"),
             "fix/bad_fix"], fail_ok=True)
    verdict = "PASS" if r.returncode == 0 else "FAIL"

    print("\n--- Step 3: Attempt to open a PR (blocked unless PASS) ---")
    run([sys.executable, os.path.join(REPO, "pr", "pr_manager.py"),
         "fix/bad_fix", verdict], fail_ok=True)

    print("\n--- Results ---")
    pr_created = os.path.exists(PR_FILE)
    if verdict == "FAIL" and not pr_created:
        print("BAD FIX -> FAIL -> NO PR (correctly blocked) [OK]")
    else:
        print("ERROR: reviewer passed the bad fix or a PR was created.")
        print("Tighten the reviewer criteria and re-run.")
        sys.exit(1)

    if os.path.exists(WORKTREE):
        subprocess.run(["git", "worktree", "remove", "--force", WORKTREE],
                       cwd=REPO, capture_output=True)


if __name__ == "__main__":
    main()
