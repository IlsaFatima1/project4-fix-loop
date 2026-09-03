"""Open a PR — only allowed when the reviewer returns PASS.

If run with a FAIL verdict, it refuses to open a PR.

Usage:
    python pr/pr_manager.py <branch> <verdict>
"""

import sys
import os
import datetime
import subprocess

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PR_DIR = os.path.join(REPO, "pull_requests")


def main():
    branch, verdict = sys.argv[1], sys.argv[2]
    verdict = verdict.strip().upper()
    os.makedirs(PR_DIR, exist_ok=True)

    if verdict != "PASS":
        print(f"[X] No PR: reviewer verdict is {verdict}, not PASS. Aborting.")
        sys.exit(1)

    # Gather the diff to embed in the PR record.
    diff = subprocess.run(["git", "diff", "main", branch, "--", "src/calculator.py"],
                          cwd=REPO, capture_output=True, text=True).stdout

    safe = branch.replace("/", "-")
    title = f"PR: fix calculate_total ({branch})"
    body = (
        "Status: OPEN\n"
        f"Branch: {branch}\n"
        f"Reviewer verdict: PASS\n"
        f"Opened at: {datetime.datetime.now().isoformat()}\n\n"
        "Diff:\n" + diff
    )
    path = os.path.join(PR_DIR, f"{safe}.md")
    with open(path, "w") as f:
        f.write("---\ntitle: " + title + "\nstate: open\n---\n\n" + body)

    print(f"[OK] PR created: {path}")
    print(body)


if __name__ == "__main__":
    main()
