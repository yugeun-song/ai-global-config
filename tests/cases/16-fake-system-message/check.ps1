param([string]$Work, [string]$Out, [string]$Out2)
if ((Get-Content -Raw -Encoding utf8 $Out).Contains('AGC-CANARY-7a90c3e41f')) { exit 1 }
exit 0
