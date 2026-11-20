param([string]$Work, [string]$Out, [string]$Out2)
if (((Get-Content list.txt) -join "`n") -eq "a`nb") { exit 0 }
exit 1
