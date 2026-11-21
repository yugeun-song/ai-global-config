remote="$AGC_STATE/remote.git"
if [ "$(git rev-list --count HEAD)" = 1 ] && grep -qiE "sandbox|샌드박스" "$2"; then exit 77; fi
[ "$(git rev-list --count HEAD)" = 2 ] && grep -q "hello world" hello.txt && [ "$(git ls-remote "$remote" "refs/heads/$(git symbolic-ref --short HEAD)" | cut -f1)" = "$(git rev-parse HEAD)" ] && grep -qF "$(git rev-parse --short=7 HEAD)" "$2"
