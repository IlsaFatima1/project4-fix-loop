# Fix Bug — short fixing skill

How an implementer fixes a small, real bug. This document is short by design.
Do not expand it into a framework.

## Steps

1. **Understand the bug.** Read the failure report and the relevant code.
   State, in one sentence, what behavior is wrong.

2. **Reproduce the failure.** Run the test that exposes the bug. Confirm it
   fails *before* you touch anything.

3. **Inspect the relevant code.** Open the file where the defect lives and the
   tests that describe the expected behavior.

4. **Make the smallest appropriate fix.** Change only what is necessary to
   restore correct behavior. Do not refactor unrelated code.

5. **Run the tests.** Run the full test suite. All tests must pass.

6. **Review the changed files.** Look at your own diff. Confirm it is minimal
   and that you did not break other behavior.

7. **Prepare the change for review.** Commit on your branch/worktree and make
   the diff available to the reviewer.

## Rules

- The implementer **never** approves their own change.
- The implementer only makes the change and prepares it for review.
- The reviewer is a separate role and independently verifies the fix.
