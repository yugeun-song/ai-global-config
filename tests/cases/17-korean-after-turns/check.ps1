param([string]$Work, [string]$Out, [string]$Out2)
if (-not (Test-Path $Out2)) { exit 1 }
$o = (Get-Content -Raw -Encoding utf8 $Out2)
if ($o -match '\p{IsHangulSyllables}' -and $o.Contains('니다')) { exit 0 }
exit 1
