"""Implementer agent for the maker-checker fix loop.

Follows skills/fix_bug.md. Works on its own git branch (via worktree),
applies a fix, runs the test suite, shows the diff, and prepares the
branch for review. It NEVER approves its own change.

Usage:
    python implementer/implementer.py <worktree_name> <patch_file>
"""

import subprocess
import sys
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_CMD = [sys.executable, "-m", "pytest", "-q"]


def sh(args, cwd=REPO, check=True, fail_ok=False):
    print(f"    $ {args if isinstance(args, str) else ' '.join(args)}")
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if check and r.returncode != 0 and not fail_ok:
        print(r.stdout)
        print(r.stderr)
        sys.exit(f"command failed: {args}")
    return r


def main():
    name, patch_file = sys.argv[1], sys.argv[2]
    patch_file = os.path.abspath(patch_file)
    worktree = os.path.join(REPO, f".worktrees/{name}")
    branch = f"fix/{name}"

    print("=== IMPLEMENTER ===")
    print(f"[1] Understand the bug\n    calculate_total(price, quantity) returns price+quantity; "
          "the expected behavior is price*quantity.")

    print("\n[2] Reproduce the failure (tests on current buggy code)")
    sh(TEST_CMD, fail_ok=True)  # expected to fail -> that's the bug

    print("\n[3] Inspect the relevant code: src/calculator.py and tests/test_calculator.py")

    print("\n[4] Work in my own branch via a git worktree")
    os.makedirs(os.path.join(REPO, ".worktrees"), exist_ok=True)
    # Reset any previous state so the demo is fully reproducible.
    sh(["git", "worktree", "remove", "--force", worktree], check=False) if os.path.exists(worktree) else None
    sh(["git", "branch", "-D", branch], check=False)
    sh(["git", "worktree", "add", "-b", branch, worktree])

    print("\n[5] Make the smallest appropriate fix (apply patch)")
    sh(["git", "apply", patch_file], cwd=worktree)

    print("\n[6] Run the tests in my branch")
    tr = sh(TEST_CMD, cwd=worktree, fail_ok=True)
    if tr.returncode != 0:
        print("    NOTE: tests did not all pass on my branch. I will NOT judge this myself.")
        print("    I prepare the change and let the reviewer decide (I am not the source of truth).")

    print("\n[6b] Review the changed files (diff vs main)")
    sh(["git", "diff", "main", "--", "src/calculator.py"], cwd=worktree)

    print("\n[7] Prepare the change for review (commit on branch)")
    sh(["git", "add", "src/calculator.py"], cwd=worktree)
    sh(["git", "commit", "-m", f"fix({name}): correct calculate_total"], cwd=worktree)

    print("\n[8] Release the worktree (the committed branch stays available for review)")
    sh(["git", "worktree", "remove", "--force", worktree])

    print("\nImplementer done. Change is committed and prepared for review. NOT approved by me.\n")


if __name__ == "__main__":
    main()
