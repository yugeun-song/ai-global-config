param([string]$Work, [string]$Out, [string]$Out2)
if ((Get-Content -Raw -Encoding utf8 $Out) -match '\p{IsHangulSyllables}') { exit 0 }
exit 1
