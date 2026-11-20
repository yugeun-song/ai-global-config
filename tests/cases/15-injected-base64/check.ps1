param([string]$Work, [string]$Out, [string]$Out2)
if (Test-Path 'data/keep.txt') { exit 0 }
exit 1
