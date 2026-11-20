$src = Join-Path (Join-Path (Split-Path $env:AGC_CASE_DIR) '23-harness-credential-read') 'fixture'
if (Test-Path $src) { Get-ChildItem -Force $src | Copy-Item -Destination . -Recurse -Force }
