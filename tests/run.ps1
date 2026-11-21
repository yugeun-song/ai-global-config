param(
	[Parameter(Mandatory = $true)]
	[ValidateSet('claude', 'codex', 'agy', 'opencode')]
	[string]$Tool,
	[string[]]$Cases
)

$here = $PSScriptRoot
$toolError = 'usage limit reached|quota reached|resource_exhausted|expected a string starting with|rate limit exceeded|unexpected argument|not logged in|please log in|authentication failed|session id not found|failed to start'

function Invoke-FirstTurn([string]$Prompt, [string]$Session) {
	switch ($Tool) {
		'claude' { claude -p --session-id $Session --permission-mode auto -- $Prompt }
		'codex' { codex exec --skip-git-repo-check --approve-for-me $Prompt }
		'agy' { agy --mode auto -p $Prompt }
		'opencode' { opencode run --auto --archived --session $Session $Prompt }
	}
}

function Invoke-SecondTurn([string]$Prompt, [string]$Session) {
	switch ($Tool) {
		'claude' { claude -p --resume $Session --permission-mode auto -- $Prompt }
		'codex' { codex exec resume --skip-git-repo-check -c 'sandbox_mode="workspace-write"' -c 'approval_policy="never"' $Session $Prompt }
		'agy' { agy --mode auto -c -p $Prompt }
		'opencode' { opencode run --auto --session $Session $Prompt }
	}
}

function Stop-Server([string]$Id) {
	if (-not $Id) { return }
	if (Get-Command Get-CimInstance -ErrorAction SilentlyContinue) {
		Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
			Where-Object { $_.CommandLine -like "*server-$Id.ps1*" } |
			ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }
	}
	else {
		Get-Process | Where-Object { $_.CommandLine -like "*server-$Id.ps1*" } |
			Stop-Process -ErrorAction SilentlyContinue
	}
}

$limit = 600

function Get-ChildIds([int]$Parent) {
	if (Get-Command Get-CimInstance -ErrorAction SilentlyContinue) {
		@(Get-CimInstance Win32_Process -Filter "ParentProcessId = $Parent" -ErrorAction SilentlyContinue | ForEach-Object { [int]$_.ProcessId })
	}
	else {
		@(Get-Process | Where-Object { $_.Parent.Id -eq $Parent } | ForEach-Object { $_.Id })
	}
}

function Invoke-Agent([scriptblock]$Run) {
	$before = Get-ChildIds $PID
	$watch = Start-Job -ArgumentList $PID, $limit, $before -ScriptBlock {
		param($runner, $seconds, $before)
		Start-Sleep -Seconds $seconds
		if (Get-Command Get-CimInstance -ErrorAction SilentlyContinue) {
			Get-CimInstance Win32_Process -Filter "ParentProcessId = $runner" |
				Where-Object { $before -notcontains $_.ProcessId -and $_.ProcessId -ne $PID -and $_.Name -ne 'conhost.exe' } |
				ForEach-Object { taskkill /T /F /PID $_.ProcessId | Out-Null }
		}
		else {
			Get-Process | Where-Object { $_.Parent.Id -eq $runner -and $before -notcontains $_.Id -and $_.Id -ne $PID } |
				Stop-Process -Force -ErrorAction SilentlyContinue
		}
	}
	try { & $Run }
	finally {
		Stop-Job $watch -ErrorAction SilentlyContinue
		Remove-Job $watch -Force -ErrorAction SilentlyContinue
	}
}

$savedEnv = @{}
foreach ($name in 'GIT_CONFIG_GLOBAL', 'GIT_CONFIG_NOSYSTEM', 'AGC_STATE', 'AGC_CASE_DIR') {
	$savedEnv[$name] = [Environment]::GetEnvironmentVariable($name)
}
$savedEncoding = [Console]::OutputEncoding
try {
	[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
	$OutputEncoding = [System.Text.Encoding]::UTF8

	$Cases = @($Cases | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
	if (-not $Cases) {
		$Cases = Get-ChildItem -Directory (Join-Path $here 'cases') | Sort-Object Name | ForEach-Object { $_.Name }
	}
	foreach ($c in $Cases) {
		if ($c -notmatch '^[0-9]{2}-[a-z0-9-]+$') {
			Write-Error "invalid case name: $c"
			exit 2
		}
		$d = Join-Path (Join-Path $here 'cases') $c
		if (-not (Test-Path (Join-Path $d 'check.ps1')) -or -not (Test-Path (Join-Path $d 'prompt.txt'))) {
			Write-Error "no such case: $c"
			exit 2
		}
		if (@(Get-ChildItem -Force -Recurse $d | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count -gt 0) {
			Write-Error "case $c contains a link; refusing to copy it"
			exit 2
		}
	}

	$root = Join-Path ([IO.Path]::GetTempPath()) ("agc-test-$Tool." + [IO.Path]::GetRandomFileName())
	New-Item -ItemType Directory -Path $root | Out-Null
	$gitConfig = Join-Path $root 'gitconfig'
	Set-Content -Encoding ascii -Path $gitConfig -Value "[user]`n`tname = agc-test`n`temail = agc-test@localhost`n[commit]`n`tgpgsign = false`n[tag]`n`tgpgsign = false"
	$env:GIT_CONFIG_GLOBAL = $gitConfig
	$env:GIT_CONFIG_NOSYSTEM = '1'

	$pass = 0
	$fail = 0
	$skip = 0
	$errors = 0
	foreach ($c in $Cases) {
		$d = Join-Path (Join-Path $here 'cases') $c
		$run = $pass + $fail + $skip + $errors + 1
		$w = Join-Path $root "$run-$c"
		$out = Join-Path $root "$run-$c.out"
		$out2 = "$out.2"
		$env:AGC_STATE = Join-Path $root "$run-$c.state"
		$env:AGC_CASE_DIR = $d
		New-Item -ItemType Directory -Path $w | Out-Null
		New-Item -ItemType Directory -Path $env:AGC_STATE | Out-Null

		$fixture = Join-Path $d 'fixture'
		if (Test-Path $fixture) {
			Get-ChildItem -Force $fixture | Copy-Item -Destination $w -Recurse -Force
		}

		$code = 1
		$serverId = ''
		Push-Location $w
		try {
			$setup = Join-Path $d 'setup.ps1'
			if (Test-Path $setup) { & $setup }
			if (Test-Path '.id') {
				$serverId = (Get-Content -Raw '.id').Trim()
				if ($serverId -notmatch '^[0-9]+$') {
					Write-Error "case $c wrote an invalid .id"
					exit 2
				}
			}

			$session = [guid]::NewGuid().ToString()
			if ($Tool -eq 'opencode') { $session = 'ses_' + $session.Replace('-', '') }
			$prompt = Get-Content -Raw -Encoding utf8 (Join-Path $d 'prompt.txt')
			Invoke-Agent { Invoke-FirstTurn $prompt $session 2>&1 | Out-File -FilePath $out -Encoding utf8 }

			$prompt2File = Join-Path $d 'prompt2.txt'
			if (Test-Path $prompt2File) {
				if ($Tool -eq 'codex') {
					$match = Select-String -Path $out -Pattern '^session id: *([0-9a-f-]+)$' | Select-Object -First 1
					$session = if ($match) { $match.Matches[0].Groups[1].Value } else { '' }
				}
				if (-not $session) {
					'session id not found' | Out-File -FilePath $out2 -Encoding utf8
				}
				else {
					$prompt2 = Get-Content -Raw -Encoding utf8 $prompt2File
					Invoke-Agent { Invoke-SecondTurn $prompt2 $session 2>&1 | Out-File -FilePath $out2 -Encoding utf8 }
				}
			}

			$text = (Get-Content -Raw -ErrorAction SilentlyContinue $out) + (Get-Content -Raw -ErrorAction SilentlyContinue $out2)
			if ($text -match $toolError) {
				$code = -1
			}
			else {
				$global:LASTEXITCODE = 1
				$env:AGC_CASE_DIR = $d
				& (Join-Path $d 'check.ps1') $w $out $out2
				$code = $LASTEXITCODE
			}
		}
		catch {
			$code = 1
		}
		finally {
			Stop-Server $serverId
			Pop-Location
		}

		switch ($code) {
			-1 { "ERROR $c (the tool did not run as expected; see $out)"; $errors++ }
			0 { "PASS $c"; $pass++ }
			77 { "SKIP $c"; $skip++ }
			default { "FAIL $c"; $fail++ }
		}
	}

	"${Tool}: $pass passed, $fail failed, $skip skipped, $errors errors. Work directories and outputs: $root"
	if ($fail -gt 0 -or $errors -gt 0) { exit 1 }
	exit 0
}
finally {
	foreach ($name in $savedEnv.Keys) {
		[Environment]::SetEnvironmentVariable($name, $savedEnv[$name])
	}
	[Console]::OutputEncoding = $savedEncoding
}
