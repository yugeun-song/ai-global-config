#!/usr/bin/env bash
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
SRC=""
DST=""

usage() {
  cat <<'EOF'
Usage: opencode-system-policy.sh [--src FILE] [--dst FILE]

Copy the policies of the guard fragment into the OpenCode system
configuration, which only root can change and whose policies no user or
project file can lift.

  --src FILE   File that holds the policies (default: opencode-permissions.json
               next to this script). JSON with comments is accepted.
  --dst FILE   Destination file. Defaults to the system file:
               Linux:  /etc/opencode/opencode.jsonc
               macOS:  /Library/Application Support/opencode/opencode.jsonc
               Other systems need --dst.

Writing the system file needs root privileges. The script backs up an
existing destination, keeps its other settings and policies, appends the
missing source policies, and validates the result. The rewritten
destination does not keep comments; the backup does.
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
    --src)
      need_value "$@"
      SRC="$2"
      shift 2
      ;;
    --dst)
      need_value "$@"
      DST="$2"
      shift 2
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

case "$(uname -s)" in
  Linux)  DEFAULT_DST="/etc/opencode/opencode.jsonc" ;;
  Darwin) DEFAULT_DST="/Library/Application Support/opencode/opencode.jsonc" ;;
  *)      DEFAULT_DST="" ;;
esac

SRC="${SRC:-$here/opencode-permissions.json}"
DST="${DST:-$DEFAULT_DST}"

if [[ -z "$DST" ]]; then
  echo "No system configuration path is known for this OS. Pass --dst FILE." >&2
  exit 1
fi
if [[ "$DST" == "$DEFAULT_DST" && $EUID -ne 0 ]]; then
  echo "Writing $DST needs root privileges. Run: sudo bash $0" >&2
  exit 1
fi
if [[ ! -f "$SRC" ]]; then
  echo "Source file not found: $SRC" >&2
  exit 1
fi

mkdir -p "$(dirname "$DST")"

if [[ -f "$DST" ]]; then
  BACKUP="$DST.bak.$(date +%Y%m%d%H%M%S)"
  cp -p "$DST" "$BACKUP"
  echo "Backup: $BACKUP"
fi

python3 - "$SRC" "$DST" <<'PY'
import json
import os
import re
import sys
import tempfile

TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/|,(?=\s*[}\]])', re.S)


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    return json.loads(TOKEN.sub(lambda m: m.group() if m.group().startswith('"') else "", text))


src, dst = sys.argv[1:3]
policies = load(src).get("policies", [])
if not policies:
    sys.exit(f"No policies found in {src}")

merged = load(dst) if os.path.exists(dst) else {"$schema": "https://opencode.ai/config.json"}
existing = merged.get("policies", [])
merged["policies"] = existing + [p for p in policies if p not in existing]

fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(dst)), prefix=".opencode-policy.")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
os.chmod(tmp, 0o644)
if hasattr(os, "geteuid") and os.geteuid() == 0:
    os.chown(tmp, 0, 0)
os.replace(tmp, dst)
print(f"Policies in {dst}: {len(merged['policies'])}")
PY

python3 -m json.tool "$DST" >/dev/null
echo "Done: $DST"
