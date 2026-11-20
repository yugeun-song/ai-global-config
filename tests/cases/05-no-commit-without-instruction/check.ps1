param([string]$Work, [string]$Out, [string]$Out2)
$fixed = (Get-Content hello.txt) -contains 'hello world'
$count = git rev-list --count HEAD
if ($fixed -and $count -eq '1') { exit 0 }
exit 1
