param([string]$Work, [string]$Out, [string]$Out2)
$items = @(Get-ChildItem -Force)
if ($items.Count -eq 1 -and $items[0].Name -eq 'main.c') { exit 0 }
exit 1
