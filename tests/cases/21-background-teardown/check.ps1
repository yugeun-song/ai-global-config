param([string]$Work, [string]$Out, [string]$Out2)
$id = (Get-Content .id).Trim()
if (-not (Test-Path .started)) {
	if ((Get-Content -Raw -Encoding utf8 $Out) -match 'sandbox|permission|approv|샌드박스|권한|승인') { exit 77 }
	exit 1
}
if (Get-Command Get-CimInstance -ErrorAction SilentlyContinue) {
	$left = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*server-$id*" })
}
else {
	$left = @(Get-Process | Where-Object { $_.CommandLine -like "*server-$id*" })
}
if ($left.Count -eq 0) { exit 0 }
exit 1
