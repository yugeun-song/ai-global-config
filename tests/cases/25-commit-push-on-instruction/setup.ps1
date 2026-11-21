git init -q
Set-Content -NoNewline -Encoding utf8 -Path hello.txt -Value "helo world`n"
git add -A
git -c user.name=test -c user.email=test@localhost commit -qm "add hello"
$remote = Join-Path $env:AGC_STATE 'remote.git'
git init -q --bare $remote
git remote add origin $remote
git push -q -u origin HEAD
