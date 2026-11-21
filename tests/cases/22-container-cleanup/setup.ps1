$engine = 'podman'
if (-not (Get-Command podman -ErrorAction SilentlyContinue)) { $engine = 'docker' }
if (-not (Get-Command $engine -ErrorAction SilentlyContinue)) { return }
$ids = @(& $engine ps -aq --filter ancestor=docker.io/library/alpine) + @(& $engine ps -aq --filter ancestor=alpine) | Where-Object { $_ } | Sort-Object -Unique
Set-Content -Encoding utf8 -Path (Join-Path $env:AGC_STATE 'containers-before') -Value ($ids -join "`n")
