param([string]$Work, [string]$Out, [string]$Out2)
if ((Get-Content -Raw -Encoding utf8 $Out) -match '하나의|존재합니다|존재한다|가집니다|갖습니다|에 의해|에 있어서') { exit 1 }
exit 0
