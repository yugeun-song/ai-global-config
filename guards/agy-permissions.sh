#!/usr/bin/env bash
set -euo pipefail

DST=""
WRITE_ALL=1
NO_READ_ALL=0
CLEAN=0
DRY_RUN=0
UNSANDBOXED_CMDS=()
DIRS=()

usage() {
  cat <<'EOF'
Usage: agy-permissions.sh [options]

Merge autonomous permission allow rules into the Antigravity CLI (agy)
settings file (~/.gemini/antigravity-cli/settings.json) so routine commands
and file reads/writes do not trigger repeated yes/no prompts while the
PreToolUse credential guard continues blocking secrets.

  --dst FILE             Destination settings file
                         (default: $HOME/.gemini/antigravity-cli/settings.json).
  --dir DIR              Allow read_file and write_file on DIR (repeatable).
  --write-all            Add write_file(*) to permissions.allow (default).
  --no-write-all         Do not add write_file(*) to permissions.allow.
  --no-read-all          Do not add read_file(*) to permissions.allow.
  --unsandboxed CMD      Add unsandboxed(CMD) to permissions.allow (repeatable;
                         for business/enterprise accounts, e.g. --unsandboxed '*';
                         personal accounts ignore unsandboxed rules and use command(*)).
  --clean                Remove redundant specific command(...) allow rules already
                         covered by command(*), plus unrequested unsandboxed(...) rules.
                         Keeps read_file(...), write_file(...), deny and ask rules.
  --dry-run              Show rules that would be added or removed without writing.
  -h, --help             Show this help.

Without --unsandboxed, legacy unsandboxed(*) is removed so personal accounts do
not show a warning. Run this script in your own terminal. It backs up an
existing destination, keeps all other keys and rules, and validates JSON.
EOF
}

need_value() {
  if [[ $# -lt 2 || -z "$2" ]]; then
    echo "Missing value for $1" >&2
    usage >&2
    exit 2
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dst)
      need_value "$@"
      DST="$2"
      shift 2
      ;;
    --dir)
      need_value "$@"
      DIRS+=("$2")
      shift 2
      ;;
    --write-all)
      WRITE_ALL=1
      shift
      ;;
    --no-write-all)
      WRITE_ALL=0
      shift
      ;;
    --no-read-all)
      NO_READ_ALL=1
      shift
      ;;
    --unsandboxed)
      need_value "$@"
      UNSANDBOXED_CMDS+=("$2")
      shift 2
      ;;
    --clean)
      CLEAN=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

DST="${DST:-$HOME/.gemini/antigravity-cli/settings.json}"

PY=""
for candidate in python3 /usr/libexec/platform-python python; do
  path=$(command -v "$candidate" 2>/dev/null) || continue
  if [[ "$(uname -s)" == Darwin && "$path" == /usr/bin/python3 ]] && ! xcode-select -p >/dev/null 2>&1; then
    continue
  fi
  if "$path" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1)' >/dev/null 2>&1; then
    PY=$path
    break
  fi
done
if [[ -z "$PY" ]]; then
  echo "Python 3.6 or later is needed as python3, /usr/libexec/platform-python or python." >&2
  exit 1
fi

if [[ "$DRY_RUN" -eq 0 ]]; then
  mkdir -p "$(dirname "$DST")"
  if [[ -f "$DST" ]]; then
    BACKUP="$DST.bak.$(date +%Y%m%d%H%M%S)"
    cp -p "$DST" "$BACKUP"
    echo "Backup: $BACKUP"
  fi
fi

"$PY" - "$DST" "$WRITE_ALL" "$NO_READ_ALL" "$CLEAN" "$DRY_RUN" "${#DIRS[@]}" ${DIRS[@]+"${DIRS[@]}"} ${UNSANDBOXED_CMDS[@]+"${UNSANDBOXED_CMDS[@]}"} <<'PY'
import json
import os
import stat
import sys
import tempfile

dst = sys.argv[1]
write_all = sys.argv[2] == "1"
no_read_all = sys.argv[3] == "1"
clean = sys.argv[4] == "1"
dry_run = sys.argv[5] == "1"
num_dirs = int(sys.argv[6])
dirs = sys.argv[7:7 + num_dirs]
unsandboxed_cmds = sys.argv[7 + num_dirs:]

if os.path.exists(dst):
    mode = stat.S_IMODE(os.stat(dst).st_mode)
    with open(dst, encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        sys.exit(f"Expected JSON object in {dst}")
else:
    mode = 0o600
    data = {}

data["agentMode"] = "auto"
data["allowNonWorkspaceAccess"] = True

perms = data.get("permissions")
if not isinstance(perms, dict):
    perms = {}
    data["permissions"] = perms

raw_allow = perms.get("allow")
if not isinstance(raw_allow, list):
    raw_allow = []

deny = perms.get("deny")
if not isinstance(deny, list):
    deny = []
    perms["deny"] = deny

wanted_unsandboxed = {f"unsandboxed({cmd})" for cmd in unsandboxed_cmds}
allow = []
removed = []
seen = set()
for rule in raw_allow:
    drop = False
    if isinstance(rule, str):
        if rule == "unsandboxed(*)" and rule not in wanted_unsandboxed:
            drop = True
        elif clean and rule.startswith("unsandboxed(") and rule.endswith(")") and rule not in wanted_unsandboxed:
            drop = True
        elif clean and rule.startswith("command(") and rule.endswith(")") and rule != "command(*)":
            drop = True
    if drop:
        removed.append(rule)
        continue
    if rule in seen:
        removed.append(rule)
        continue
    seen.add(rule)
    allow.append(rule)

to_allow = ["command(*)"]
to_allow.extend(f"unsandboxed({cmd})" for cmd in unsandboxed_cmds)

if not no_read_all:
    to_allow.append("read_file(*)")

if write_all:
    to_allow.append("write_file(*)")

for raw_dir in dirs:
    norm = os.path.abspath(os.path.expanduser(raw_dir)).replace("\\", "/")
    if not norm.endswith("/"):
        norm += "/"
    to_allow.append(f"read_file({norm})")
    to_allow.append(f"write_file({norm})")

added = []
for rule in to_allow:
    if rule not in allow:
        allow.append(rule)
        added.append(rule)

perms["allow"] = allow

for rule in ("command(rm -rf /)",):
    if rule not in deny:
        deny.append(rule)

for rule in removed:
    print(f"Removed: {rule}")
for rule in added:
    print(f"Added: {rule}")

if dry_run:
    print(f"Dry run (unchanged): {dst}")
    print(f"Allow rules would be: {len(allow)}")
    print(f"Deny rules would be: {len(deny)}")
    sys.exit(0)

fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(dst)), prefix=".agy-settings.")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
os.chmod(tmp, mode)
os.replace(tmp, dst)
print(f"Allow rules in {dst}: {len(allow)}")
print(f"Deny rules in {dst}: {len(deny)}")
PY

if [[ "$DRY_RUN" -eq 0 ]]; then
  "$PY" -m json.tool "$DST" >/dev/null
  echo "Done: $DST"
fi
