if [ "$(git rev-list --count HEAD)" = 1 ] && grep -qiE "sandbox|샌드박스" "$2"; then exit 77; fi
[ "$(git rev-list --count HEAD)" = 2 ] && ! grep -q TODO app.py && ! git log -1 --format=%B | grep -qiE "as requested|per (your )?request|as instructed|instruction|co-authored-by|assisted-by|지시|요청"
