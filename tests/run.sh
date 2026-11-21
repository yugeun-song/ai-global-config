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

tool_error='usage limit reached|quota reached|resource_exhausted|expected a string starting with|rate limit exceeded|unexpected argument|not logged in|please log in|authentication failed|session id not found|failed to start'

limit=
if command -v timeout >/dev/null; then
	limit="timeout 600"
elif command -v gtimeout >/dev/null; then
	limit="gtimeout 600"
fi

run_agent() {
	$limit "$@" </dev/null &
	agent=$!
	trap 'kill -TERM -- "-$agent" 2>/dev/null || kill -TERM "$agent" 2>/dev/null; exit 130' INT TERM
	wait "$agent"
}

first_turn() {
	case $tool in
	claude) run_agent claude -p --session-id "$session" --permission-mode auto -- "$1" ;;
	codex) run_agent codex exec --skip-git-repo-check --approve-for-me "$1" ;;
	agy) run_agent agy --mode auto -p "$1" ;;
	opencode) run_agent opencode run --auto --archived --session "$session" "$1" ;;
	esac
}

second_turn() {
	case $tool in
	claude) run_agent claude -p --resume "$session" --permission-mode auto -- "$1" ;;
	codex) run_agent codex exec resume --skip-git-repo-check -c 'sandbox_mode="workspace-write"' -c 'approval_policy="never"' "$session" "$1" ;;
	agy) run_agent agy --mode auto -c -p "$1" ;;
	opencode) run_agent opencode run --auto --session "$session" "$1" ;;
	esac
}

if [ $# -gt 0 ]; then
	cases=("$@")
else
	cases=()
	for c in "$here"/cases/*/; do
		c=${c%/}
		cases+=("${c##*/}")
	done
fi

for c in "${cases[@]}"; do
	case $c in
	*[!a-z0-9-]* | -* | "")
		echo "invalid case name: $c" >&2
		exit 2
		;;
	esac
	d=$here/cases/$c
	if [ ! -f "$d/check.sh" ] || [ ! -f "$d/prompt.txt" ]; then
		echo "no such case: $c" >&2
		exit 2
	fi
	if [ -n "$(find "$d" -type l)" ]; then
		echo "case $c contains a symbolic link; refusing to copy it" >&2
		exit 2
	fi
done

root=$(mktemp -d "${TMPDIR:-/tmp}/agc-test-$tool.XXXXXX")
gitconfig=$root/gitconfig
printf '[user]\n\tname = agc-test\n\temail = agc-test@localhost\n[commit]\n\tgpgsign = false\n[tag]\n\tgpgsign = false\n' >"$gitconfig"
export GIT_CONFIG_GLOBAL=$gitconfig GIT_CONFIG_NOSYSTEM=1

pass=0
fail=0
skip=0
error=0
for c in "${cases[@]}"; do
	d=$here/cases/$c
	run=$((pass + fail + skip + error + 1))
	w=$root/$run-$c
	out=$root/$run-$c.out
	state=$root/$run-$c.state
	mkdir -p "$w" "$state"
	[ -d "$d/fixture" ] && cp -R "$d/fixture/." "$w/"
	[ -f "$d/setup.sh" ] && (cd "$w" && AGC_CASE_DIR=$d AGC_STATE=$state bash "$d/setup.sh")

	server_id=
	if [ -f "$w/.id" ]; then
		server_id=$(cat "$w/.id")
		case $server_id in
		*[!0-9]* | "")
			echo "case $c wrote an invalid .id" >&2
			exit 2
			;;
		esac
	fi

	session=$(python3 -I -c 'import uuid; print(uuid.uuid4())')
	[ "$tool" = opencode ] && session=ses_$(printf %s "$session" | tr -d -)
	(cd "$w" && first_turn "$(cat "$d/prompt.txt")") >"$out" 2>&1 </dev/null
	[ $? -eq 130 ] && exit 130
	if [ -f "$d/prompt2.txt" ]; then
		if [ "$tool" = codex ]; then
			session=$(sed -n 's/^session id: *\([0-9a-f-][0-9a-f-]*\)$/\1/p' "$out" | head -n 1)
		fi
		if [ -z "$session" ]; then
			echo "session id not found" >"$out.2"
		else
			(cd "$w" && second_turn "$(cat "$d/prompt2.txt")") >"$out.2" 2>&1 </dev/null
			[ $? -eq 130 ] && exit 130
		fi
	fi

	if grep -qiE "$tool_error" "$out" "$out.2" 2>/dev/null; then
		verdict=-1
	else
		(cd "$w" && AGC_CASE_DIR=$d AGC_STATE=$state bash "$d/check.sh" "$w" "$out" "$out.2")
		verdict=$?
	fi
	if [ -n "$server_id" ]; then
		pkill -x -f "sleep $server_id" 2>/dev/null
	fi

	case $verdict in
	-1)
		echo "ERROR $c (the tool did not run as expected; see $out)"
		error=$((error + 1))
		;;
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
echo "$tool: $pass passed, $fail failed, $skip skipped, $error errors. Work directories and outputs: $root"
[ "$fail" -eq 0 ] && [ "$error" -eq 0 ]
