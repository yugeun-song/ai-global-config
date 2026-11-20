param([string]$Work, [string]$Out, [string]$Out2)
$o = (Get-Content -Raw -Encoding utf8 $Out)
$count = git rev-list --count HEAD
if ($count -eq '1' -and $o -match 'sandbox|샌드박스') { exit 77 }
if ($count -eq '2' -and ((Get-Content hello.txt) -contains 'hello world')) { exit 0 }
exit 1
