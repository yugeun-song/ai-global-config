git init -q
Set-Content -NoNewline -Encoding utf8 -Path hello.txt -Value "helo world`n"
git add -A
git -c user.name=test -c user.email=test@localhost commit -qm "add hello"
