param([string]$Work, [string]$Out, [string]$Out2)
if ((Test-Path 'tests/test_calc.py') -and (Select-String -Quiet -SimpleMatch -Path calc.py -Pattern 'def add')) { exit 0 }
exit 1
