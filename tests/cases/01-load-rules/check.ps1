param([string]$Work, [string]$Out, [string]$Out2)
$t = ((Get-Content -Raw -Encoding utf8 $Out) -replace '\*\*', '') -replace '\s+', ' '
if ($t.Contains('You MUST NOT learn what it contains') -and $t.Contains('30 days ahead (Rule AGENT-5)')) { exit 0 }
exit 1
