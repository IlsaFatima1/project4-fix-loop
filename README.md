# A Fix Loop with a Real Checker

A small, self-contained maker–checker fix loop in Python + Git.

Two separate roles:

```text
IMPLEMENTER                       REVIEWER / CHECKER
     |                                 |
     |-- fixes a REAL bug in           |-- independently verifies:
     |   its own branch/worktree       |      original bug, diff, tests,
     |                                 |      plus its OWN edge cases
     +---------------------->           |
                                       v
                                    PASS / FAIL
                                       |
            PASS -> Open PR           FAIL -> No PR
```

## The real bug

`src/calculator.py` defines `calculate_total(price, quantity)`:

```python
def calculate_total(price, quantity):
    return price + quantity     # BUG: should be price * quantity
```

The total cost of `quantity` items at `price` each is `price * quantity`,
but the code adds the two numbers. `tests/test_calculator.py` encodes the
expected behavior and fails on the buggy `main` branch.

## The fix skill

`skills/fix_bug.md` is a short, 7-step skill the implementer follows:
understand the bug, reproduce the failure, inspect the code, make the
smallest fix, run the tests, review the changed files, prepare the change
for review.

## The implementer role

`implementer/implementer.py` follows the skill. It works on its **own git
branch** (via a worktree), applies a fix, runs the test suite, shows its
diff, and commits the change for review. It **never approves its own work** —
it only makes the change.

## The reviewer role (the real checker)

`reviewer/reviewer.py` is the independent checker and the **source of
truth**. It does **not** trust the implementer's explanation. It:

1. Inspects the original bug on `main`.
2. Checks out the proposed change into an isolated worktree.
3. Inspects the implementation diff.
4. Runs the project's own test suite.
5. Runs its **own independent edge-case checks** against the real code.
6. Verifies the original bug is gone (not merely masked).

It returns exactly one decision:

```text
PASS
```
or
```text
FAIL
```
On `FAIL` it provides clear reasons, e.g.:

```text
Result: FAIL

Reasons:
- The project's test suite does not pass on this branch.
- My independent edge-case checks failed: calculate_total(10, 4) == 14, expected 40

Decision: FAIL
```

The reviewer will NOT approve a change merely because the code looks
reasonable, the diff is small, or the implementer says it is fixed. Actual
behavior and the tests must support the decision.

## PR rule

`pr/pr_manager.py` opens a PR **only** when the reviewer returns `PASS`.
On `FAIL` it prints `[X] No PR` and refuses. A PR record (a markdown file in
`pull_requests/`) is written only for a `PASS`.

## Demonstrations

Run them fresh with:

```text
python demo/init_repo.py    # one-time: create repo + buggy baseline
python demo/good_fix.py     # Case 1
python demo/bad_fix.py      # Case 2
```

### Case 1 — Good fix (PASS -> PR)

```text
Bug found
   |
Implementer creates branch/worktree (fix/good_fix)
   |  applies  return price * quantity
Tests run and pass
   |
Reviewer checks independently
   |  project tests pass, reviewer's edge cases pass, bug gone
   v
PASS
   |
PR opened  -> pull_requests/fix-good_fix.md
```

### Case 2 — Deliberately bad fix (FAIL -> No PR)

The bad fix (`fix/bad_fix`) hard-codes one result so the obvious test
passes, but it breaks every other valid case:

```python
if price == 3 and quantity == 2:
    return 6
return price + quantity       # still broken for everything else
```

The reviewer's project-test run fails (the hardcoded case is the only one
that "works"), and its independent edge cases fail. It returns `FAIL` with
reasons, and `pr_manager` blocks the PR:

```text
[X] No PR: reviewer verdict is FAIL, not PASS. Aborting.
```

## Example output (Case 2, reviewer)

```text
=== REVIEWER / CHECKER ===
I verify independently. I do not trust the implementer's explanation.
...
[4] Run the project's own test suite against the branch
    FAILED tests/test_calculator.py::test_multiple_items - assert 14 == 40
[5] Run my own independent edge-case checks against the real code
EDGE-FAIL: calculate_total(10, 4) == 14, expected 40
EDGE-FAIL: calculate_total(100, 3) == 103, expected 300

Result: FAIL

Reasons:
- The project's test suite does not pass on this branch.
- My independent edge-case checks failed: calculate_total(10, 4) == 14, expected 40; ...

Decision: FAIL
```

## Why it is a real loop

- The **implementer is not the source of truth**; the reviewer is.
- The reviewer gathers **objective evidence** (running tests, running its
  own checks, reading the diff) rather than accepting an explanation.
- A PR is created **iff** the reviewer independently returns `PASS`.
