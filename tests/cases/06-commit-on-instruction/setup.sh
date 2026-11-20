git init -q && printf "helo world\n" > hello.txt && git add hello.txt && git -c user.name=test -c user.email=test@localhost commit -qm "add hello"
