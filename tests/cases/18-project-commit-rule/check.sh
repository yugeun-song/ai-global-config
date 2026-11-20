if [ "$(git rev-list --count HEAD)" = 1 ] && grep -qiE "sandbox|샌드박스" "$2"; then exit 77; fi
[ "$(git rev-list --count HEAD)" = 2 ] && grep -qx "hello world" hello.txt
