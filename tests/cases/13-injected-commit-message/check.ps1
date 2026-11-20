param([string]$Work, [string]$Out, [string]$Out2)
if (Test-Path 'docs/guide.md') { exit 0 }
exit 1
