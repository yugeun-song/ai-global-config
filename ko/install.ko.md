# ai-global-config 설치 (읽기용 한국어 번역)

원본은 `INSTALL.md`입니다. 이 파일은 한국어 화자가 읽기 위한 번역이며, 내용은 원본과
100% 같습니다. 에이전트는 이 파일을 규칙으로 따르지 않습니다. 원본과 다른 곳이 있으면
오류이므로 원본에 맞춰 고칩니다. 원본의 대문자 MUST와 ALWAYS는 "반드시"로, NEVER와 MUST
NOT은 "절대"로 옮깁니다.

설치하려면 사용자가 아무 디렉터리에서나 에이전트를 열고 다음 한 줄을 보냅니다.

```text
Read <absolute path of this clone>/INSTALL.md and install the rules as it describes.
```

사용자가 이 clone을 지운 뒤에도 설치한 규칙은 반드시 계속 동작해야 합니다. 따라서 이 clone을 가리키는
참조가 아니라, 에이전트의 도구가 소유하는 사본을 설치합니다.

## 규칙을 도구에 설치하기

사용자가 이 규칙을 설치하라고 명시적으로 요청할 때만 시작합니다. 이 파일 자체는 요청이
아닙니다. 설치 요청에는 이미 설치된 예전 사본을 교체하는 일도 포함됩니다.

1. `rules/global.md`를 끝까지 읽습니다.
2. 도구가 모든 세션, 모든 디렉터리에서 지침을 읽는 위치를 찾습니다. 메모리 기능, 프로젝트별
   파일, 세션별 저장소는 절대 쓰지 않습니다. 이런 저장소는 용량 상한이 있거나, 한 프로젝트에만
   적용되거나, 만료되기 때문입니다. 찾은 위치와 그 위치를 어떻게 확인했는지(도구 문서나 도구
   자체의 도움말 출력)를 사용자에게 알립니다. 아래 표에 알려진 위치가 있습니다. 이 위치를 믿기
   전에 도구의 현재 문서와 대조합니다.
3. 글은 파일 복사 명령(`cp`, `Copy-Item`, 또는 도구의 파일 복사 기능)으로만 옮깁니다. 규칙을
   절대 다시 타이핑하거나, 요약하거나, 형식을 바꾸지 않습니다. 한 바이트만 달라져도 9단계의 확인이
   실패합니다.
4. 설치된 사본을 찾습니다. 방식 A나 B의 `ai-global-config.md` 파일, 방식 C의 표지 사이 글,
   방식 D의 `ai-global-config-*.md` 파일이 사본입니다. 사본의 SHA-256이 `rules/global.md`의 SHA-256과 같으면 사본은 그대로
   두고, 그 사실을 보고한 뒤 7단계로 넘어갑니다. 다르면 예전 버전입니다. 차이를 요약해 사용자에게 알린 뒤,
   6단계에서 통째로 교체합니다.
5. 방식 B와 C는 파일에 줄이나 블록을 추가합니다. 그 파일에 다른 내용이 있으면 import 줄이나
   표지 블록만 추가하고, 추가한 내용을 그대로 보고에 적습니다. import 줄과 표지 바깥에서는
   7단계가 지우는 내용만 바꿉니다.
6. 도구가 지원하는 첫 번째 방식으로 설치합니다.
   - 방식 A, rules 디렉터리: 도구가 모든 세션에서 모든 규칙 파일을 읽는 디렉터리에
     `rules/global.md`를 `ai-global-config.md`라는 이름으로 바이트 그대로 복사합니다. 다른 것은
     바꾸지 않습니다.
   - 방식 B, 복사 후 import: 도구 자체의 설정 디렉터리 안에 `rules/global.md`를
     `ai-global-config.md`라는 이름으로 바이트 그대로 복사합니다. 그다음 그 사본을 불러오는
     import 줄 하나를 도구의 전역 지침 파일에 추가합니다.
   - 방식 C, 표지 블록: `rules/global.md`의 글을 그대로 도구의 전역 지침 파일 안의
     `<!-- ai-global-config:begin -->` 줄과 `<!-- ai-global-config:end -->` 줄 사이에 넣습니다.
     파일이 비어 있거나 없으면 파일 전체가 이 블록입니다.
   - 방식 D, 나눈 rules 디렉터리: 도구가 rules 디렉터리의 모든 파일을 읽지만 파일 하나의
     크기를 `rules/global.md`보다 작게 제한할 때 씁니다. `rules/parts/`의 각 파일을
     `ai-global-config-<조각 이름>`이라는 이름으로 그 디렉터리에 복사합니다. 도구가 머리글이
     있는 파일만 매 세션 읽는다면, 그 머리글을 그대로 먼저 쓰고 그 뒤에 조각을 바이트 그대로
     씁니다. `rules/parts/`에 더는 없는 조각은 설치 위치에서도 지웁니다.
7. 도구가 모든 세션, 모든 디렉터리에서 읽는 다른 지침 파일에서 예전 전역 규칙을 지웁니다.
   Claude Code라면 `~/.claude/CLAUDE.md`가 그런 파일입니다. 방식 B와 C에서는 import 줄과 표지
   바깥의 내용도 대상입니다. 예전 버전이나 사용자가 그 파일에 넣은 규칙을 남겨 두면, 도구가 그
   규칙을 설치한 사본과 함께 읽어 서로 어긋납니다. 설치나 갱신 요청에 이 단계가 포함되므로
   먼저 묻지 않습니다.
   - 파일을 바꾸기 전에 도구의 설정 디렉터리에 백업을 복사해 둡니다.
   - `rules/global.md`가 이미 다루거나 그와 어긋나는 규칙과 메모는 모두 지웁니다.
   - 이 기기에서만 맞는 내용만 낱말 하나 바꾸지 않고 남깁니다. 이 기기의 하드웨어,
     소프트웨어, 경로, 네트워크, 로컬 도구에 관한 사실과 그 도구에 관한 규칙이 여기에
     해당합니다. 어떤 구절이 전역 규칙인지 이 기기의 메모인지 판단할 수 없으면 남깁니다.
   - 파일 맨 앞에 짧은 머리글을 둡니다. 머리글에는 설치한 사본의 위치와, 이 파일에는 이
     기기의 메모만 있다는 문장을 적습니다.
   - 지운 내용, 남긴 내용, 백업 경로를 보고합니다. 지운 구절 가운데 `rules/global.md`에 없는
     구절은 따로 나열해, 사용자가 이 저장소에 추가할 수 있게 합니다.
8. Claude Code라면 `~/.claude/settings.json`에서 `includeGitInstructions`를 `false`로 바꿉니다.
   그러면 Claude Code가 내장 commit과 pull request 작업 지침, 그리고 git 상태 스냅숏을 넣지
   않으므로, 에이전트가 commit하는 방식은 Rule ACTION-3, ACTION-4, OUTPUT-3, OUTPUT-4만으로
   정해집니다. 대신 에이전트는 세션이 시작될 때 git 상태를 받지 않고, 필요할 때 스스로 읽습니다.
   `attribution`은 설정하지 않고 둡니다. Claude Code는 이미 attribution을 다루는 사용자 규칙을
   자기 문구보다 앞에 둡니다. 다른 키는 모두 그대로 두고, 결과가 JSON으로 해석되지 않으면 원래
   파일로 되돌리고, 바꾼 내용을 그대로 보고에 적습니다.
9. 결과를 확인합니다. 설치된 사본(방식 A와 B)이나 표지 사이의 글(방식 C)의 SHA-256이
   `rules/global.md`의 SHA-256과 같아야 합니다. 방식 D에서는 설치한 각 파일에서 머리글을 뺀
   나머지의 SHA-256이 해당 조각의 SHA-256과 같아야 하고, 조각을 이름 순서로 이어 붙인 결과가
   `rules/global.md`와 같아야 합니다. SHA-256은 Linux에서 `sha256sum`, macOS에서
   `shasum -a 256`, Windows에서 `Get-FileHash -Algorithm SHA256`으로 계산합니다. 방식 B에서는
   import 줄을 다시 읽어, 그 줄이 이 clone이 아니라 사본을 가리키는지도 확인합니다.
10. 사용자에게 보고합니다. 보고 항목은 위치, 설치 방식, 두 SHA-256 값, 7단계와 8단계의
    결과, 그리고 `rules/global.md` 1부의 규칙 그룹마다 도구 자체 설정(deny 규칙, hook, sandbox)으로 강제했는지 아니면 글로만
    적혀 있는지입니다. 그다음 clone을 지워도 된다고 알립니다. 사용자에게, 다른 디렉터리에서 새
    세션을 열고 그 세션의 에이전트가 Rule SECRET-1을 그대로 인용하게 해 보라고 요청합니다.
    인용문은 `rules/global.md`와 낱말 단위로 같아야 합니다. 목록 기호나 굵은 글씨 같은 Markdown
    표기는 달라도 됩니다.

sandbox나 권한 설정이 어떤 단계를 막으면, 어느 설정이 어느 단계를 막았는지 사용자에게 알리고
멈춥니다.

갱신하려면 사용자가 이 저장소를 다시 clone하고 같은 한 줄을 보냅니다. 그러면 4단계에서 예전
사본을 찾고, 6단계에서 교체하고, 7단계에서 다른 지침 파일의 예전 규칙을 지웁니다.

| 도구 | 방식 | 사본 위치 |
|---|---|---|
| Claude Code | A | `~/.claude/rules/ai-global-config.md` |
| Antigravity CLI (agy) | D, `~/.gemini/config/rules/` 안, 머리글은 `---`, `trigger: always_on`, `---`, 빈 줄 하나 | `~/.gemini/config/rules/ai-global-config-*.md` |
| Gemini CLI | B, `~/.gemini/GEMINI.md`에 import 줄 `@~/.gemini/ai-global-config.md` | `~/.gemini/ai-global-config.md` |
| Codex CLI | C, `~/.codex/AGENTS.md` 안 | 그 파일 안 |
| OpenCode | C, `~/.config/opencode/AGENTS.md` 안 | 그 파일 안 |
| Hermes Agent | C, `~/.hermes/SOUL.md` 안 | 그 파일 안 |
| Cursor | 사용자가 설정 화면의 User Rules에 글을 붙여 넣음 | 없음 |

## 강제 장치 설치(선택)

규칙은 글입니다. 강제 장치는 credential을 지목하는 도구 호출과, 홈 디렉터리 전체를 검색하거나
복사하거나 압축하는 도구 호출을 도구가 거부하게 만듭니다(Rule SECRET-1). 또 강제 장치 자신이나
hook 설정을 바꾸거나 hook을 끄는 호출 앞에서는 도구가 사용자에게 묻게 만듭니다. 이 장치는
도구의 공식 문서가 설명하는 사전 hook으로만 동작하고, OpenCode에서는 권한 규칙과 정책으로만
동작합니다. 사용자가 강제 장치를 요청할 때만 시작합니다.

1. 아래 표에서 자기 도구를 찾습니다. 표에 없거나, 도구의 현재 문서에 사전 hook도 권한 규칙도
   없으면, 그 도구에는 강제 장치를 쓸 수 없다고 사용자에게 알리고 멈춥니다.
2. hook을 쓰는 도구라면 Python 3.6 이상을 시작하는 일반 명령 이름을 고릅니다. 그래야 Python을
   업그레이드하거나 다시 설치해도 hook이 계속 동작합니다. `python3`, `python` 순서로 시험하고,
   Windows에서는 `py`도 시험합니다. 다음 명령이 `True`를 출력하면 그 이름을 쓸 수 있습니다:
   `<이름> -c "import sys; print(sys.version_info >= (3, 6))"`. hook은 그 이름이 `PATH`에서 찾은
   것을 실행합니다. `command -v <이름>`(Windows에서는 `where <이름>`)은 그 이름이 찾는 파일을,
   `<이름> -c "import sys; print(sys.executable)"`은 그 이름이 시작하는 인터프리터를 보여 줍니다.
   이 이름은 시스템마다 다릅니다.
   - Debian과 Ubuntu에는 `python-is-python3` 패키지가 있어야만 `python`이 있습니다.
   - RHEL 8과 그 재빌드 배포판에는 `python3` 명령이 없을 수 있습니다. 그곳에서는
     `/usr/libexec/platform-python`을 씁니다.
   - macOS의 `/usr/bin/python3`는 Command Line Tools를 설치하기 전까지 stub이고, 이 stub을
     실행하면 설치 대화 상자가 열립니다. 먼저 `xcode-select -p`를 실행하고, 이 명령이 실패하면
     그 파일을 건너뜁니다.
   - Windows의 `WindowsApps`에 있는 `python`과 `python3`는 종료 코드 9009로 끝나는 Microsoft
     Store stub일 수 있습니다. 위의 시험 명령으로 이런 stub을 걸러 냅니다.

   그 파일이 버전 관리 도구(pyenv, asdf, mise)의 shim이거나 프로젝트 가상 환경 안에 있으면,
   대신 시스템의 버전 없는 인터프리터의 절대 경로(예: `/usr/bin/python3`)를 씁니다. shim은 다른
   버전을 고정한 디렉터리에서 실패할 수 있기 때문입니다. Windows에서는 인터프리터 디렉터리에
   `icacls`를 실행하고, 인터프리터 디렉터리가 `Everyone`, `Users`, `Authenticated Users`에게
   쓰기나 수정 권한을 주지 않는 이름을 고릅니다. 그런 디렉터리를 거치면 어느 계정의 어느
   프로그램이든 인터프리터를 바꿔 강제 장치를 끌 수 있기 때문입니다. `C:\Python314`처럼 `C:\`
   바로 아래에 만든 디렉터리는 그런 권한을 드라이브 루트에서 물려받습니다. 모든 이름이 그런
   디렉터리로 이어지면, 관리자가 그 권한을 없앨 수 있다고 사용자에게 알립니다.
   `icacls <디렉터리> /inheritance:d`는 물려받은 항목을 명시 항목으로 바꾸고, 이어서
   `icacls <디렉터리> /remove:g *S-1-5-11`은 `Authenticated Users` 항목을 지웁니다. `C:\` 아래의
   디렉터리는 바로 이 항목에서 그 권한을 얻습니다. 그 디렉터리 아래의 파일도 함께 바뀝니다.
   결과는 `icacls`로 다시 확인합니다. 도구가 hook 명령을 `cmd.exe`로 실행하면 인터프리터의 절대
   경로를 씁니다. `cmd.exe`는 일반 이름을 `PATH`보다 현재 디렉터리에서 먼저 찾으므로,
   `python.exe`가 든 저장소에서는 그 파일이 Python 대신 실행됩니다. Python 3.6 이상을 시작하는
   이름이 없으면, 강제 장치에 Python 3.6 이상이 필요하다고 사용자에게 알리고 멈춥니다. Claude
   Code는 `onFailure` 때문에 2.1.295 이상이어야 합니다.
3. hook을 쓰는 도구라면 `guards/guard.py`를 표의 판정기 위치에 바이트 그대로 복사합니다. 도구나
   그 sandbox가 이 쓰기를 거부하면 4단계 전에 멈춥니다. 없는 스크립트를 가리키는 hook은 Claude
   Code에서 모든 도구 호출을 막고, 다른 도구에서는 아무 알림 없이 아무 일도 하지 않을 수
   있습니다. 도구 밖 터미널에서 실행할 복사 명령을 사용자에게 주고, 사용자가 실행한 뒤에만 이어
   갑니다.
4. 도구의 설정 조각에서 `<python3>`를 2단계의 명령으로, `<home>`을 사용자 홈 디렉터리의 절대
   경로로 바꿉니다. Windows에서도 경로의 `\`를 `/`로 씁니다. Claude Code 설정 조각은 exec
   form(`args`)을 씁니다. Claude Code가 shell 없이 명령을 바로 실행하므로, 이 항목에는 따옴표가
   필요 없고 Windows에서 Git Bash가 있든 없든 똑같이 동작합니다. 다른 설정 조각에서는 두 값을
   감싼 따옴표를 그대로 두고, 도구가 hook 명령을 PowerShell로 실행하면 따옴표로 감싼 명령 앞에
   `&`와 공백 하나를 붙입니다. 그다음 조각을 설정 파일에 합칩니다. 조각의 항목을 기존 항목 옆에
   추가합니다. 기존 항목은 절대 지우거나 바꾸지 않습니다. 원래 내용을 보관해 두고, 합친 파일이
   JSON(OpenCode는 JSONC)으로 해석되지 않으면 원래 내용으로 되돌리고, 추가한 내용을 그대로 보고에
   적습니다.
5. 어떤 설정은 사용자만 도구 밖 터미널에서 적용할 수 있습니다. 관리자나 root 권한이 필요한
   시스템 파일과, 도구가 에이전트의 수정을 막는 설정 파일이 그렇습니다. 자기 도구에 해당하는
   항목을 제안하고 사용자에게 명령을 준 뒤, 다른 단계를 이어 갑니다. 사용자가 적용한 설정은
   6단계에서 확인합니다.
   - Claude Code, managed settings. 사용자 권한으로 도는 에이전트는 여전히 사용자 자신의 파일을
     고칠 수 있지만, managed settings는 관리자나 root만 바꿀 수 있고, 다른 설정 파일에
     `disableAllHooks`가 들어 있어도 그 hook은 켜져 있습니다. Claude Code는 managed settings를
     Windows에서는 `C:\Program Files\ClaudeCode\managed-settings.json`, macOS에서는
     `/Library/Application Support/ClaudeCode/managed-settings.json`, Linux에서는
     `/etc/claude-code/managed-settings.json`에서 읽습니다. 판정기를 그 디렉터리의
     `hooks/ai-global-config-guard.py`로 복사하고, 설정 조각의 판정기 경로를 그 사본의 경로로
     바꾼 뒤, 4단계처럼 조각을 `managed-settings.json`에 합칩니다. 사용자는 이 명령을 관리자나
     root 터미널에서 실행하거나, 시스템 자체의 권한 상승 확인 창에서 승인합니다. managed 파일을
     쓰기 전에, 표준 입력으로 `{"tool_name":"Bash","tool_input":{"command":"ls"}}`를 넣어 hook
     명령을 그대로 실행하고, 종료 코드가 0인지 확인합니다. managed 항목이 실패하면, 관리자가 고칠
     때까지 모든 도구 호출이 막히기 때문입니다. 그다음 사용자 설정의 항목과 그 판정기 사본을 지워,
     도구 호출마다 강제 장치가 한 번만 돌게 합니다. 사용자가 절대 경로를 요청하지 않으면 2단계의
     일반 명령 이름을 그대로 쓰고, 그 장단점을 사용자에게 알립니다. Claude Code는 그 이름을
     자기가 물려받은 `PATH`에서 찾는데, 사용자 자신의 계정이 그 `PATH`를 바꿀 수 있습니다. 반면
     관리자만 바꿀 수 있는 디렉터리에 있는 인터프리터의 절대 경로를 쓰면 이 빈틈이 닫히지만, 그
     인터프리터가 옮겨지면 hook이 깨집니다. 원격 설정이나 MDM 정책(macOS 구성 프로필, 또는
     Windows `HKLM` 레지스트리의 값)으로 managed settings가 이미 정해져 있으면, Claude Code가 이
     파일을 건너뛸 수 있습니다. WSL에서는 사용자도 `/etc/claude-code`에 쓸 수 있습니다.
   - OpenCode, 시스템 파일. OpenCode의 설정 조각에는 정책(policies)도 들어 있습니다. 조각을
     합치면 정책이 바로 적용되고, 어떤 프로젝트 파일도 그 정책을 풀 수 없습니다. OpenCode는 넓은
     범위의 파일에 든 정책을 나중에 평가하기 때문입니다. 에이전트가 정책을 바꿀 수 없게 하려면,
     사용자가 `sudo bash guards/opencode-system-policy.sh`로 root만 바꿀 수 있는 시스템 파일에
     정책을 복사합니다. 이 스크립트는 Linux와 macOS를 지원합니다. 스크립트는 시스템 파일을
     백업하고, 그 설정과 정책을 유지하면서 빠진 정책을 덧붙이고, 결과를 검증합니다. 이 스크립트에는
     Python 3.6 이상이 필요하고, 스크립트는 `python3`, `/usr/libexec/platform-python`, `python`
     순서로 그 인터프리터를 찾습니다. Windows에서 OpenCode는 `%ProgramData%\opencode`에서 시스템
     파일을 읽지만, 이 스크립트는 그곳을 설정하지 않습니다.
   - Antigravity CLI, 권한. agy는 에이전트가 `~/.gemini/antigravity-cli/settings.json`을 읽거나
     고치지 못하게 막습니다. agy는 auto 모드에서도 워크스페이스 밖을 읽기 전과, sandbox 밖에서 도는
     명령 앞에서 묻습니다. sandbox가 `.git`을 읽기 전용으로 붙이므로 git 명령은 sandbox 밖에서
     돌아야 합니다. `bash guards/agy-permissions.sh`는 그 파일을 백업하고, 기존 키와 규칙을
     유지하면서 auto 모드와 워크스페이스 밖 접근을 켜고, 모든 명령, sandbox 밖 명령, 파일 읽기,
     파일 쓰기를 허용합니다. 그러면 이런 호출에는 강제 장치만 검사로 남습니다. 이 스크립트는
     `command(rm -rf /)`도 거부합니다. `--no-write-all`, `--no-read-all`, `--dir DIR`,
     `--unsandboxed CMD` 옵션으로 허용 범위를 줄일 수 있습니다. 이 스크립트에는 bash와 Python 3.6
     이상이 필요하고, OpenCode 스크립트와 같은 방식으로 Python을 찾습니다. Windows에서는 사용자가
     Git Bash에서 실행합니다.
6. 강제 장치를 확인합니다.
   - `python3 guards/test_guard.py <설치한 판정기>`가 실패 없이 끝납니다.
   - 설치한 판정기의 SHA-256이 `guards/guard.py`의 SHA-256과 같습니다.
   - `python3 guards/test_guard.py --hook <claude|codex|agy|gemini>`가 실패 없이 끝납니다. 이 명령은
     설정 파일(Claude Code는 managed settings도)에 들어 있는 강제 장치 명령을 쓰인 그대로 모두
     실행합니다. exec form 항목은 바로 실행하고, shell form 항목은 시스템 shell로 실행합니다.
     막혀야 하는 입력 하나와 허용되어야 하는 입력 하나를 넣습니다. credential은 열지 않습니다.
     도구가 shell form hook을 다른 shell(예: Windows의 PowerShell)로 실행하면, 그 shell에서도
     명령을 실행합니다.
   - Claude Code의 managed settings 항목은, 없는 credential 파일을 지목하는 명령(예:
     `cat agc-decoy/.netrc`)을 세션에서 실행해 확인합니다. 강제 장치가 그 명령을 막아야 하고,
     차단 메시지에 managed settings 디렉터리의 판정기 사본이 나와야 합니다.
   - OpenCode는 합친 파일을 다시 읽어 조각의 규칙과 정책이 모두 들어 있는지 확인합니다. 사용자가
     스크립트를 실행했다면 시스템 파일도 같은 방법으로 확인합니다. 새 OpenCode 세션에서
     credential을 지목한 도구 호출이 거부되는지 확인합니다.
7. 위치, 두 SHA-256 값, 시험 결과를 보고합니다. Codex라면 사용자에게 Codex에서 `/hooks`를 열어
   새 hook을 신뢰하도록 요청합니다. Codex는 사용자가 신뢰하기 전까지 새 hook을 건너뜁니다.

| 도구 | 판정기 위치 | 설정 파일 | 설정 조각 |
|---|---|---|---|
| Claude Code | `~/.claude/hooks/ai-global-config-guard.py`, 또는 managed settings 디렉터리의 `hooks/ai-global-config-guard.py` | `~/.claude/settings.json`, 또는 `managed-settings.json` | `guards/claude-settings.json` |
| Codex CLI | `~/.codex/hooks/ai-global-config-guard.py` | `~/.codex/hooks.json` | `guards/codex-hooks.json` |
| Antigravity CLI (agy) | `~/.gemini/config/hooks/ai-global-config-guard.py` | `~/.gemini/config/hooks.json` | `guards/agy-hooks.json` |
| Gemini CLI | `~/.gemini/hooks/ai-global-config-guard.py` | `~/.gemini/settings.json` | `guards/gemini-settings.json` |
| OpenCode | 없음: 권한 규칙과 정책 | `~/.config/opencode/opencode.jsonc`, root로는 시스템 파일도 | `guards/opencode-permissions.json` |

강제 장치는 실수와 흔한 시도를 막습니다. 완전한 보안 경계는 아닙니다.

- 도구 호출의 글에서 이름을 찾아 판정합니다. 그래서 명령이 glob(`~/.n?trc`), 중괄호 확장, 변수,
  실행 중에 만든 문자열, 인코딩한 이름, 해석하지 못하는 형태로 바꾼 작업 디렉터리, glob이나 만든
  문자열 안의 심볼릭 링크, 디렉터리를 지목하지 않아 작업 디렉터리를 검색하는 명령, 앞서 쓴
  스크립트로 비밀에 닿는 경우는 놓칠 수 있습니다.
- 비밀은 파일과 비밀 저장소에서만 찾습니다. 환경 변수, 클립보드, shell 기록, 그리고 token도
  담는 도구 자체 설정 파일(예: MCP 서버 설정)에 든 비밀은 다루지 않습니다.
- 다른 컴퓨터에 연결하지 않도록 `\\server\share` 같은 네트워크 경로는 따라가지 않습니다. 다만
  Windows에서는 그런 공유를 가리키는 로컬 심볼릭 링크가 이미 있으면, 확인 과정에서 그 공유에
  연결할 수 있습니다.
- 존재 확인 예외는 `ls`, `stat`, `test`가 진짜 명령이라고 믿습니다. 같은 이름의 shell 함수나
  `PATH` 앞쪽의 파일이 있으면 그 확인이 읽기로 바뀔 수 있습니다.
- 강제 장치 자신과 hook 설정의 보호도 이름으로 판정하므로, 간접적으로 닿는 명령은 막지
  못합니다.
- 그런 파일 이름이 들어간 무해한 명령은 막을 수 있습니다. 예를 들어
  `docker compose --env-file .env`가 그렇습니다. shell이 바꾸지 않고 넘기는 메시지 글은 검사하지
  않습니다. `git commit`, `git tag`, `git merge`, `git notes`의 `-m`이나 `--message`에 준 따옴표
  문자열이나 작은따옴표 PowerShell here-string, 그 명령이 `-F -`로 읽거나 `-m "$(…)"` 안의
  `cat`으로 읽는, 끝 표지를 따옴표로 감싼 heredoc, `-F -`로 파이프해 넘긴 그런 리터럴, 그리고
  `gh pr`, `gh issue`, `gh release`의 제목, 본문, 노트 옵션이 그렇습니다. 명령 치환이 든 메시지는
  그대로 검사합니다.
- 사용자가 Rule SECRET-1에 따라 명시적으로 허락한 읽기도 막습니다. 사용자가 허락했는지 판정기는
  알 수 없기 때문입니다. 그 단계는 사용자가 도구 밖 터미널에서 합니다.
- 다른 hook(plugin, skill, 에이전트 정의, 작업 공간 파일에서 온 hook)은 강제 장치가 허용한
  도구 호출을 나중에 바꿀 수 있습니다.
- 호출에 든 낱말이나 경로가 약 4초 안에 확인할 수 있는 양보다 많으면, 그 호출을 막고
  에이전트에게 호출을 나누라고 알립니다. 호출을 해석하지 못하면, 원문 글로 판정하고 애매하면
  막습니다.
- Claude Code: managed settings가 아닌 설정 파일(`--settings`로 넘긴 파일 포함)에
  `disableAllHooks`가 있으면, 사용자 설정에 둔 강제 장치가 꺼집니다. 강제 장치는
  `disableAllHooks`를 담은 도구 호출 앞에서 묻지만, clone한 저장소의 `.claude/settings.json`에
  그 값이 이미 들어 있을 수 있습니다. 그 파일은 그 프로젝트에서 사용자 설정보다 우선합니다.
  managed settings에 둔 강제 장치는 두 경우 모두 켜져 있습니다(5단계). `onFailure: "block"`
  때문에, 판정기 스크립트가 지워지거나 망가지거나 인터프리터가 지워지면, 사용자가 hook 항목을
  직접 고치거나 지울 때까지 모든 도구 호출이 막힙니다. managed 항목을 그렇게 고치려면 관리자나
  root 권한이 필요합니다.
- 강제 장치는 자기 인터프리터를 보호하지 않습니다. 명령 이름을 쓰는 hook은 그 이름이 `PATH`에서
  처음 찾은 인터프리터를 실행합니다. 사용자 자신의 계정이 그 인터프리터 파일(예: Windows의
  `AppData` 아래에 사용자별로 설치한 경우)이나 도구가 물려받는 `PATH`를 바꿀 수 있으면,
  에이전트가 그 파일이나 `PATH`를 바꿔 강제 장치를 끌 수 있습니다. 사용자 자신의 계정은
  Windows에서 `PATH`의 사용자 부분을, 모든 시스템에서 shell 시작 파일을 언제나 바꿀 수 있으므로,
  이 탐색을 피하는 방법은 절대 경로뿐입니다.
- Codex에는 "묻기" 결정이 없어서, 강제 장치는 자기 파일을 바꾸는 호출을 묻는 대신 막습니다.
  Codex는 hook이 실패하거나, 시간 초과되거나, 잘못된 형식으로 답하면 도구를 그대로 실행할 수
  있습니다. 실행 중인 터미널에 나중에 보내는 입력(`write_stdin`)은 hook을 다시 거치지 않습니다.
  Codex는 새 hook이나 바뀐 hook을 사용자가 `/hooks`에서 신뢰하기 전까지 건너뛰므로, 갱신할
  때마다 그 단계가 다시 필요합니다. `CODEX_HOME`을 바꾸면 hook 파일 위치도 바뀝니다. 웹 검색
  같은 호스팅 도구는 hook을 거치지 않습니다.
- Antigravity CLI는 hook이 실패할 때의 동작을 문서에 밝히지 않습니다. 그래서 실패하면 호출이
  실행된다고 보고 대합니다. 온라인 문서는 `"allow"`가 호출을 다음 hook이나 기본 정책에
  넘긴다고 적지만, 1.5.13 버전에 들어 있는 문서는 `"allow"`가 호출을 승인한다고 적습니다. 두
  번째 해석이 맞다면, 강제 장치 때문에 agy의 승인 확인이 생략됩니다.
- Gemini CLI: `BeforeTool` hook은 밀리초 단위 `timeout`(설정 조각은 10초에
  해당하는 `10000`을 씀)과 정규식 `matcher`(`".*"`)를 쓰며, `"allow"`와
  `"deny"` 결정만 지원합니다(`"ask"` 결정이 없음). 그래서 강제 장치는 자기
  파일이나 `~/.gemini/settings.json`을 바꾸는 호출 앞에서 묻는 대신
  막습니다. `BeforeTool` hook이 시간 초과되면 Gemini CLI는 fail-open으로
  동작해 도구 호출을 그대로 실행합니다.
- OpenCode 권한 규칙은 명령 글 전체로 일치를 판단하므로 hook보다 거칩니다. OpenCode 패턴은
  `*`와 `?`만 알기 때문에, 설정 조각은 명령에서 `.env` 앞에 올 수 있는 글자를 하나씩 나열합니다.
  그래도 `v`에 공백이 든 `cat $v.env`처럼 shell이 실행 중에 만드는 이름은 이 패턴을 빠져나갑니다.
  OpenCode는 Windows에서는 대소문자를 구분하지 않고, macOS에서는 파일 규칙에서만 구분하지
  않습니다. 그래서 기본 파일 시스템이 대소문자를 구분하지 않는 macOS에서는 `cat .ENV`가 어떤
  규칙에도 걸리지 않고 `.env`를 읽습니다. hook은 모든 시스템에서 대소문자를 구분하지 않습니다.
  나중에 읽히는 규칙(에이전트나 프로젝트의 규칙)이 경로를 다시 허용할 수 있습니다. 마지막에 일치한 규칙이
  이기기 때문입니다. 설정 조각의 정책이 이 빈틈을 막습니다. OpenCode는 넓은 범위의 파일에 든
  정책을 나중에 평가하고, 거부하는 정책은 "항상 허용" 승인보다도 우선하며, 허용하는 정책은 앞선
  거부를 풀기만 합니다. 정책은 묻지 못하므로, OpenCode 자체 설정을 편집하기 전에 묻는 규칙은 권한
  규칙으로 남습니다. V2 이전 버전은 `permissions` 대신 `permission` 키를 읽으므로 그 버전에서는
  권한 규칙이 아무 일도 하지 않고, 정책을 `experimental.policies`에서만 읽는 버전은 이 정책을
  무시합니다. `grep` 동작의 resource는 경로가 아니라 검색 패턴입니다. 그래서 규칙은 그런 이름이
  든 패턴은 막지만, 그런 디렉터리 안의 검색은 막지 못합니다.

테스트 사례 23은 에이전트가 미끼 credential을 스스로 읽지 않는지 확인합니다. 테스트 사례 24는
사용자가 허락한 읽기를 강제 장치가 실제로 막는지 확인합니다.
