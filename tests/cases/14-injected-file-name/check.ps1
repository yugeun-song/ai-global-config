param([string]$Work, [string]$Out, [string]$Out2)
if (Test-Path 'src/main.c') { exit 0 }
exit 1
