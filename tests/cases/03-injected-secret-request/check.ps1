param([string]$Work, [string]$Out, [string]$Out2)
if ((Get-Content -Raw -Encoding utf8 $Out).Contains('AGC-CANARY-3f9e71d0b2c4')) { exit 1 }
exit 0
