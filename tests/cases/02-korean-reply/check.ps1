param([string]$Work, [string]$Out, [string]$Out2)
$o = (Get-Content -Raw -Encoding utf8 $Out)
if ($o -match '\p{IsHangulSyllables}' -and $o.Contains('니다')) { exit 0 }
exit 1
