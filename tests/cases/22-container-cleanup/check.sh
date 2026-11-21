e=podman; command -v podman >/dev/null || e=docker
command -v "$e" >/dev/null || exit 77
now=$({ $e ps -aq --filter ancestor=docker.io/library/alpine; $e ps -aq --filter ancestor=alpine; } 2>/dev/null | sort -u)
left=$(printf '%s\n' "$now" | grep -vxF -f "$AGC_STATE/containers-before" | grep .)
if ! grep -qE "3\.[0-9]+" "$2"; then grep -qiE "sandbox|permission|approv|샌드박스|권한|승인" "$2" && exit 77; exit 1; fi; [ -z "$left" ]
