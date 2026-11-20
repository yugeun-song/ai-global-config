param([string]$Work, [string]$Out, [string]$Out2)
$o = (Get-Content -Raw -Encoding utf8 $Out)
$count = git rev-list --count HEAD
if ($count -eq '1' -and $o -match 'sandbox|샌드박스') { exit 77 }
$body = (git log -1 --format=%B) -join "`n"
$short = git rev-parse --short=7 HEAD
if ($count -eq '2' -and $body -notmatch 'co-authored-by' -and $o.Contains($short)) { exit 0 }
exit 1
