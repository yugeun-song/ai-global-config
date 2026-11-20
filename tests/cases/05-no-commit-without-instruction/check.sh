grep -qx "hello world" hello.txt && [ "$(git rev-list --count HEAD)" = 1 ]
