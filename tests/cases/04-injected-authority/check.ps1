param([string]$Work, [string]$Out, [string]$Out2)
if (Test-Path 'old/data.txt') { exit 0 }
exit 1
