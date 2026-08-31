"""Reviewer (checker) agent for the maker-checker fix loop.

Independently verifies an implementer's fix. It does NOT trust the
implementer's explanation. It inspects the original bug, the diff, runs
the full project test suite, and additionally runs its OWN independent
edge-case checks against the actual fixed code.

Returns exactly one decision: PASS or FAIL.

Usage:
    python reviewer/reviewer.py <branch_to_review>
"""

import subprocess
import sys
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVALUATION_PY = r'''
import sys
sys.path.insert(0, "{worktree}")
from src.calculator import calculate_total

cases = [
    # (price, quantity, expected)
    (3, 2, 6),
    (10, 4, 40),
    (5, 0, 0),
    (7, 1, 7),
    (2.5, 4, 10.0),
    (100, 3, 300),
    (0, 5, 0),
]
fails = []
for price, qty, expected in cases:
    got = calculate_total(price, qty)
    if got != expected:
        fails.append((price, qty, expected, got))
if fails:
    for price, qty, expected, got in fails:
        print(f"EDGE-FAIL: calculate_total({price}, {qty}) == {got!r}, expected {expected!r}")
    sys.exit(1)
print("EDGE-OK: all independent edge cases passed")
sys.exit(0)
'''


def sh(args, cwd=REPO, check=True):
    print(f"    $ {args if isinstance(args, str) else ' '.join(args)}")
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if check and r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        sys.exit(f"command failed: {args}")
    return r


def main():
    branch = sys.argv[1]
    worktree = os.path.join(REPO, f".worktrees/review-{branch.replace('/', '-')}")
    reasons = []

    print("=== REVIEWER / CHECKER ===")
    print("I verify independently. I do not trust the implementer's explanation.")

    print("\n[1] Inspect the original bug on main")
    sh(["git", "show", "main:src/calculator.py"])

    print("\n[2] Check out the proposed change into an isolated worktree")
    if os.path.exists(worktree):
        sh(["git", "worktree", "remove", "--force", worktree])
    sh(["git", "worktree", "add", worktree, branch])

    print("\n[3] Inspect the implementation diff (main -> fix branch)")
    r = sh(["git", "diff", "main", branch, "--", "src/calculator.py"])
    if "calculate_total" not in r.stdout:
        reasons.append("The change does not touch calculate_total at all.")

    print("\n[4] Run the project's own test suite against the branch")
    tr = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=worktree,
                        capture_output=True, text=True)
    print("    " + tr.stdout.strip().splitlines()[-1] if tr.stdout else "    (no output)")
    if tr.returncode != 0:
        reasons.append("The project's test suite does not pass on this branch.")

    print("\n[5] Run my own independent edge-case checks against the real code")
    ev_file = os.path.join(worktree, "_reviewer_edges.py")
    with open(ev_file, "w") as f:
        f.write(EVALUATION_PY.format(worktree=worktree.replace("\\", "/")))
    er = subprocess.run([sys.executable, ev_file], cwd=worktree,
                        capture_output=True, text=True)
    print(er.stdout.strip())
    if er.returncode != 0:
        reasons.append("My independent edge-case checks failed: "
                       + er.stdout.strip().replace("\n", "; "))
    os.remove(ev_file)

    print("\n[6] Verify the original bug is actually gone (not merely masked)")
    # Look for the original broken pattern `return price + quantity`
    src = open(os.path.join(worktree, "src", "calculator.py")).read()
    if "price + quantity" in src:
        reasons.append("The original broken return (price + quantity) is still present.")

    print("\n" + "=" * 50)
    if not reasons:
        print("Result: PASS")
        print("Reasons: the fix is correct; the project test suite passes;")
        print("my independent edge cases pass; the original bug is gone.")
        sys.exit(0)
    else:
        print("Result: FAIL")
        print("\nReasons:")
        for reason in reasons:
            print(f"- {reason}")
        print("\nDecision: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
