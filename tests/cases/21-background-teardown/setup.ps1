$id = Get-Random -Minimum 40000 -Maximum 80000
Set-Content -Encoding utf8 -Path .id -Value $id
Set-Content -Encoding utf8 -Path "server-$id.ps1" -Value "New-Item -ItemType File -Force .started | Out-Null`nStart-Sleep -Seconds $id"
