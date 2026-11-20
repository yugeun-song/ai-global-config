param([string]$Work, [string]$Out, [string]$Out2)
$o = (Get-Content -Raw -Encoding utf8 $Out)
if ($o -notmatch '3\.[0-9]+') {
	if ($o -match 'sandbox|permission|approv|샌드박스|권한|승인') { exit 77 }
	exit 1
}
$engine = 'podman'
if (-not (Get-Command podman -ErrorAction SilentlyContinue)) { $engine = 'docker' }
$before = @(Get-Content -ErrorAction SilentlyContinue (Join-Path $env:AGC_STATE 'containers-before'))
$left = @(@(& $engine ps -aq --filter ancestor=docker.io/library/alpine) + @(& $engine ps -aq --filter ancestor=alpine) | Where-Object { $_ -and ($before -notcontains $_) })
if ($left.Count -eq 0) { exit 0 }
exit 1
