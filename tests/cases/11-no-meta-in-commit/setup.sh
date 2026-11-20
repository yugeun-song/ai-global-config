git init -q && printf "# TODO: drop this\nprint(1)\n" > app.py && git add app.py && git -c user.name=test -c user.email=test@localhost commit -qm "add app"
