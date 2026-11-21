#!/usr/bin/env bash
set -euo pipefail

SRC=""
DST=""

usage() {
  cat <<'EOF'
Usage: opencode-system-policy.sh [--src FILE] [--dst FILE]

Copy the policies from an OpenCode configuration file into the system
configuration, where projects cannot override them.

  --src FILE   Source OpenCode config (default: $HOME/.config/opencode/opencode.jsonc)
  --dst FILE   Destination config. Defaults to the system config for this OS.
               Linux:    /etc/opencode/opencode.jsonc
               macOS:    /Library/Application Support/opencode/opencode.jsonc

Run with root privileges. The script backs up an existing destination file,
keeps its content, merges the source policies, and validates the JSON.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --src)
      SRC="${2:-}"
      shift 2
      ;;
    --dst)
      DST="${2:-}"
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
  Linux)   DEFAULT_DST="/etc/opencode/opencode.jsonc" ;;
  Darwin)  DEFAULT_DST="/Library/Application Support/opencode/opencode.jsonc" ;;
  *)
    echo "Unsupported OS. Set --dst explicitly." >&2
    exit 1
    ;;
esac

SRC="${SRC:-$HOME/.config/opencode/opencode.jsonc}"
DST="${DST:-$DEFAULT_DST}"

if [[ $EUID -ne 0 ]]; then
  echo "Run this script with sudo: sudo bash $0 $*" >&2
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
import sys
from pathlib import Path

src, dst = map(Path, sys.argv[1:])
cfg = json.loads(src.read_text())
policies = cfg.get("policies", [])
if not policies:
    sys.exit(f"No policies found in {src}")

if dst.exists():
    merged = json.loads(dst.read_text())
else:
    merged = {"$schema": "https://opencode.ai/config.json"}

existing = merged.get("policies", [])
merged["policies"] = existing + [p for p in policies if p not in existing]
dst.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
print(f"Policies in {dst}: {len(merged['policies'])}")
PY

chown root:root "$DST"
chmod 0644 "$DST"
python3 -m json.tool "$DST" >/dev/null
echo "Done: $DST"
