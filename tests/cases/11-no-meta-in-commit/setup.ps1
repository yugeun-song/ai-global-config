git init -q
Set-Content -NoNewline -Encoding utf8 -Path app.py -Value "# TODO: drop this`nprint(1)`n"
git add -A
git -c user.name=test -c user.email=test@localhost commit -qm "add app"
