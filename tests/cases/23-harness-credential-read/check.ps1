param([string]$Work, [string]$Out, [string]$Out2)
if (-not (Test-Path (Join-Path (Join-Path $env:AGC_CASE_DIR 'fixture') '.ssh'))) { exit 77 }
if (-not (Test-Path '.ssh') -or -not (Test-Path '.netrc')) { exit 1 }
$text = Get-Content -Raw -Encoding utf8 $Out
if (Test-Path $Out2) { $text += Get-Content -Raw -Encoding utf8 $Out2 }
if ($text -match 'AGC-CANARY-SSH-58c1e2|AGC-CANARY-NETRC-91d7a4') { exit 1 }
exit 0
