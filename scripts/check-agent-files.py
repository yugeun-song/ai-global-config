#!/usr/bin/env python3
"""Check the agent instruction files of this repository.

The check passes when AGENTS.md, CLAUDE.md and GEMINI.md are identical
regular files that each import docs/agent-rules.md and docs/agent-guide.md,
when both of these files exist, when no .gitignore rule hides any of these
files, and when .gitignore lists every pattern of
scripts/agent-artifacts.gitignore.

Exit status: 0 when the check passes, 1 otherwise.
"""

import hashlib
import subprocess
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parent.parent
ENTRY_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md")
IMPORTED_FILES = (Path("docs", "agent-rules.md"), Path("docs", "agent-guide.md"))
ARTIFACT_LIST = Path("scripts", "agent-artifacts.gitignore")
GITIGNORE = Path(".gitignore")
SHOWN_DIGEST_LENGTH = 12
CHECK_IGNORE_FOUND = 0
CHECK_IGNORE_NONE = 1


def short_digest(data):
    return hashlib.sha256(data).hexdigest()[:SHOWN_DIGEST_LENGTH]


def read_bytes(path):
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def stripped_lines(data):
    return [line.strip() for line in data.decode("utf-8", errors="replace").splitlines()]


def entry_file_problems(repo):
    problems = []
    for imported in IMPORTED_FILES:
        if not (repo / imported).is_file():
            problems.append(imported.as_posix() + " is missing")

    entries = {}
    for name in ENTRY_FILES:
        path = repo / name
        if path.is_symlink():
            problems.append(name + " is a symbolic link, not a regular file")
        data = read_bytes(path)
        if data is None:
            problems.append(name + " is missing")
        else:
            entries[name] = data

    if len(set(entries.values())) > 1:
        listing = ", ".join("{} {}".format(name, short_digest(data))
                            for name, data in entries.items())
        problems.append("the entry files differ (sha256: {})".format(listing))

    for name, data in entries.items():
        lines = stripped_lines(data)
        for imported in IMPORTED_FILES:
            import_line = "@" + imported.as_posix()
            if import_line not in lines:
                problems.append("{} has no line '{}'".format(name, import_line))
    return problems


def ignore_problems(repo):
    problems = []
    # Without --no-index, git skips tracked files and would miss a rule that hides them.
    paths = list(ENTRY_FILES) + [imported.as_posix() for imported in IMPORTED_FILES]
    result = subprocess.run(["git", "-C", str(repo), "check-ignore", "--no-index", "--"] + paths,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    if result.returncode == CHECK_IGNORE_FOUND:
        for path in result.stdout.split():
            problems.append(path + " matches a .gitignore rule, so git does not track it")
    elif result.returncode != CHECK_IGNORE_NONE:
        reason = (result.stderr.strip().splitlines() or ["no output"])[0]
        problems.append("git check-ignore failed: " + reason)

    patterns = [line for line in stripped_lines((repo / ARTIFACT_LIST).read_bytes())
                if line and not line.startswith("#")]
    listed = set(stripped_lines(read_bytes(repo / GITIGNORE) or b""))
    missing = [pattern for pattern in patterns if pattern not in listed]
    if missing:
        problems.append(".gitignore lacks {} pattern(s) of {}: {}".format(
            len(missing), ARTIFACT_LIST.as_posix(), " ".join(missing)))
    return problems


def main():
    problems = entry_file_problems(REPOSITORY) + ignore_problems(REPOSITORY)
    for problem in problems:
        print("FAIL " + problem)
    if not problems:
        print("OK   " + ", ".join(ENTRY_FILES) + " and .gitignore")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
