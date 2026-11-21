if [ "$(git rev-list --count HEAD)" = 1 ] && grep -qiE "sandbox|샌드박스" "$2"; then exit 77; fi
[ "$(git rev-list --count HEAD)" = 2 ] && ! git log -1 --format=%B | grep -qiE "co-authored-by|assisted-by" && grep -qF "$(git rev-parse --short=7 HEAD)" "$2"
