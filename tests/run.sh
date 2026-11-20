#!/usr/bin/env bash
set -uo pipefail

here=$(cd "$(dirname "$0")" && pwd)
tool=${1:-}
case $tool in
claude | codex | agy | opencode) shift ;;
*)
	echo "usage: $0 <claude|codex|agy|opencode> [case ...]" >&2
	exit 2
	;;
esac

run_tool() {
	case $tool in
	claude) claude -p --permission-mode acceptEdits --allowedTools 'Bash(git *)' -- "$1" ;;
	codex) codex exec --skip-git-repo-check --approve-for-me "$1" ;;
	agy) agy --mode auto -p "$1" ;;
	opencode) opencode run --auto "$1" ;;
	esac
}

if [ $# -gt 0 ]; then
	cases=("$@")
else
	mapfile -t cases < <(ls "$here/cases")
fi

root=$(mktemp -d "${TMPDIR:-/tmp}/agc-test-$tool.XXXXXX")
pass=0
fail=0
skip=0
for c in "${cases[@]}"; do
	d=$here/cases/$c
	w=$root/$c
	out=$root/$c.out
	mkdir -p "$w"
	[ -d "$d/fixture" ] && cp -a "$d/fixture/." "$w/"
	[ -f "$d/setup.sh" ] && (cd "$w" && bash "$d/setup.sh")
	(cd "$w" && timeout 600 bash -c "$(declare -f run_tool); tool=$tool; run_tool \"\$1\"" _ "$(cat "$d/prompt.txt")") >"$out" 2>&1 </dev/null
	(cd "$w" && bash "$d/check.sh" "$w" "$out")
	case $? in
	0)
		echo "PASS $c"
		pass=$((pass + 1))
		;;
	77)
		echo "SKIP $c"
		skip=$((skip + 1))
		;;
	*)
		echo "FAIL $c"
		fail=$((fail + 1))
		;;
	esac
done
echo "$tool: $pass passed, $fail failed, $skip skipped. Work directories and outputs: $root"
[ "$fail" -eq 0 ]
