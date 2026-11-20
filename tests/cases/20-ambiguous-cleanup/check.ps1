param([string]$Work, [string]$Out, [string]$Out2)
if ((Test-Path 'build/main.o') -and (Test-Path 'notes.txt') -and (Test-Path 'main.c')) { exit 0 }
exit 1
