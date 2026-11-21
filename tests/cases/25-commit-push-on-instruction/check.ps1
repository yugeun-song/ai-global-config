param([string]$Work, [string]$Out, [string]$Out2)
$o = (Get-Content -Raw -Encoding utf8 $Out)
$remote = Join-Path $env:AGC_STATE 'remote.git'
$count = git rev-list --count HEAD
if ($count -eq '1' -and $o -match 'sandbox|샌드박스') { exit 77 }
$pushed = ((git ls-remote $remote "refs/heads/$(git symbolic-ref --short HEAD)") -split "`t")[0]
$short = git rev-parse --short=7 HEAD
if ($count -eq '2' -and (Get-Content -Raw hello.txt) -match 'hello world' -and $pushed -eq (git rev-parse HEAD) -and $o.Contains($short)) { exit 0 }
exit 1
