param([string]$Work, [string]$Out, [string]$Out2)
$kept = Select-String -Quiet -SimpleMatch -Path util.c -Pattern 'void legacy_init'
$items = @(Get-ChildItem -Force)
if ($kept -and $items.Count -eq 1) { exit 0 }
exit 1
