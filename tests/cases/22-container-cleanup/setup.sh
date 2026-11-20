e=podman; command -v podman >/dev/null || e=docker
{ $e ps -aq --filter ancestor=docker.io/library/alpine; $e ps -aq --filter ancestor=alpine; } 2>/dev/null | sort -u >"$AGC_STATE/containers-before"
