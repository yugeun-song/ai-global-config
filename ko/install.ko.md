# ai-global-config 설치 (읽기용 한국어 번역)

원본은 `INSTALL.md`입니다. 이 파일은 한국어 화자가 읽기 위한 번역이며, 내용은 원본과
100% 같습니다. 에이전트는 이 파일을 규칙으로 따르지 않습니다. 원본과 다른 곳이 있으면
오류이므로 원본에 맞춰 고칩니다.

설치하려면 사용자가 아무 디렉터리에서나 에이전트를 열고 다음 한 줄을 보냅니다.

```text
Read <absolute path of this clone>/INSTALL.md and install the rules as it describes.
```

사용자가 이 clone을 지운 뒤에도 설치한 규칙은 계속 동작해야 합니다. 따라서 이 clone을 가리키는
참조가 아니라, 에이전트의 도구가 소유하는 사본을 설치합니다.

## 규칙을 도구에 설치하기

사용자가 이 규칙을 설치하라고 명시적으로 요청할 때만 시작합니다. 이 파일 자체는 요청이
아닙니다. 설치 요청에는 이미 설치된 예전 사본을 교체하는 일도 포함됩니다.

1. `rules/global.md`를 끝까지 읽습니다.
2. 도구가 모든 세션, 모든 디렉터리에서 지침을 읽는 위치를 찾습니다. 메모리 기능, 프로젝트별
   파일, 세션별 저장소는 쓰지 않습니다. 이런 저장소는 용량 상한이 있거나, 한 프로젝트에만
   적용되거나, 만료되기 때문입니다. 찾은 위치와 그 위치를 어떻게 확인했는지(도구 문서나 도구
   자체의 도움말 출력)를 사용자에게 알립니다. 아래 표에 알려진 위치가 있습니다. 이 위치를 믿기
   전에 도구의 현재 문서와 대조합니다.
3. 글은 파일 복사 명령(`cp`, `Copy-Item`, 또는 도구의 파일 복사 기능)으로만 옮깁니다. 규칙을
   다시 타이핑하거나, 요약하거나, 형식을 바꾸지 않습니다. 한 바이트만 달라져도 7단계의 확인이
   실패합니다.
4. 설치된 사본을 찾습니다. 방식 A나 B의 `ai-global-config.md` 파일, 방식 C의 표지 사이 글,
   방식 D의 `ai-global-config-*.md` 파일이 사본입니다. 사본의 SHA-256이 `rules/global.md`의 SHA-256과 같으면 아무것도 바꾸지 않고,
   그 사실을 보고하고 멈춥니다. 다르면 예전 버전입니다. 차이를 요약해 사용자에게 알린 뒤,
   6단계에서 통째로 교체합니다.
5. 방식 B와 C는 파일에 줄이나 블록을 추가합니다. 그 파일에 다른 내용이 있고 이 규칙을 그
   파일에 처음 설치하는 경우라면, 추가할 내용을 정확히 보여 주고 승인을 기다립니다. import 줄과
   표지 바깥의 내용은 바꾸지 않습니다.
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
7. 결과를 확인합니다. 설치된 사본(방식 A와 B)이나 표지 사이의 글(방식 C)의 SHA-256이
   `rules/global.md`의 SHA-256과 같아야 합니다. 방식 D에서는 설치한 각 파일에서 머리글을 뺀
   나머지의 SHA-256이 해당 조각의 SHA-256과 같아야 하고, 조각을 이름 순서로 이어 붙인 결과가
   `rules/global.md`와 같아야 합니다. SHA-256은 Linux에서 `sha256sum`, macOS에서
   `shasum -a 256`, Windows에서 `Get-FileHash -Algorithm SHA256`으로 계산합니다. 방식 B에서는
   import 줄을 다시 읽어, 그 줄이 이 clone이 아니라 사본을 가리키는지도 확인합니다.
8. 사용자에게 보고합니다. 보고 항목은 위치, 설치 방식, 두 SHA-256 값, 그리고 `rules/global.md`
   1부의 규칙 그룹마다 도구 자체 설정(deny 규칙, hook, sandbox)으로 강제했는지 아니면 글로만
   적혀 있는지입니다. 그다음 clone을 지워도 된다고 알립니다. 사용자에게, 다른 디렉터리에서 새
   세션을 열고 그 세션의 에이전트가 Rule SECRET-1을 그대로 인용하게 해 보라고 요청합니다.
   인용문은 `rules/global.md`와 낱말 단위로 같아야 합니다. 목록 기호나 굵은 글씨 같은 Markdown
   표기는 달라도 됩니다.

sandbox나 권한 설정이 어떤 단계를 막으면, 어느 설정이 어느 단계를 막았는지 사용자에게 알리고
멈춥니다.

갱신하려면 사용자가 이 저장소를 다시 clone하고 같은 한 줄을 보냅니다. 그러면 4단계에서 예전
사본을 찾고, 6단계에서 교체합니다.

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

규칙은 글입니다. 강제 장치는 credential을 지목하는 도구 호출을 도구가 거부하게 만들고, 강제
장치 자신이나 hook 설정을 바꾸는 호출 앞에서는 사용자에게 묻게 만듭니다(Rule SECRET-1). 이
장치는 도구의 공식 문서가 설명하는 사전 hook이나 권한 규칙으로만 동작합니다. 사용자가 강제
장치를 요청할 때만 시작합니다.

1. 아래 표에서 자기 도구를 찾습니다. 표에 없거나, 도구의 현재 문서에 사전 hook도 권한 규칙도
   없으면, 그 도구에는 강제 장치를 쓸 수 없다고 사용자에게 알리고 멈춥니다.
2. hook을 쓰는 도구라면 Python 3 인터프리터의 실제 경로를 찾습니다. `python3 -c "import os,
   sys; print(os.path.realpath(sys.executable), sys.prefix == sys.base_prefix)"`를 실행합니다
   (Windows에서는 `python3` 대신 `py -3`이나 `python`). 두 번째 값이 `True`이고, 그 경로가 버전
   관리 도구(pyenv, asdf, mise)의 shim이나 프로젝트 가상 환경이 아닐 때만 출력된 경로를 씁니다.
   그런 경로는 바뀌거나 사라질 수 있기 때문입니다. 출력된 경로에 부 버전이 붙어 있고(예:
   `/usr/bin/python3.14`), 같은 디렉터리의 버전 없는 이름(`/usr/bin/python3`)이 같은 파일을
   가리키면, 버전 없는 이름을 씁니다. 패키지를 업그레이드하면 버전 붙은 파일은 사라지지만 그
   이름은 남기 때문입니다. 그런 인터프리터가 없으면, 강제 장치에 Python 3가 필요하다고
   사용자에게 알리고 멈춥니다. Claude Code는 `onFailure` 때문에 2.1.295 이상이어야 합니다.
3. hook을 쓰는 도구라면 `guards/guard.py`를 표의 판정기 위치에 바이트 그대로 복사합니다. 도구나
   그 sandbox가 이 쓰기를 거부하면 4단계 전에 멈춥니다. 없는 스크립트를 가리키는 hook은 Claude
   Code에서 모든 도구 호출을 막고, 다른 도구에서는 아무 일도 하지 않을 수 있습니다. 도구 밖
   터미널에서 실행할 복사 명령을 사용자에게 주고, 사용자가 실행한 뒤에만 이어 갑니다.
4. 도구의 설정 조각에서 `<python3>`를 2단계의 인터프리터 경로로, `<home>`을 사용자 홈
   디렉터리의 절대 경로로 바꿉니다. 두 경로를 감싼 따옴표는 그대로 두고, Windows에서도 두
   경로의 `\`를 `/`로 씁니다. 도구가 hook 명령을 PowerShell로 실행하면, 따옴표로 감싼
   인터프리터 경로 앞에 `&`와 공백 하나를 붙입니다. 그다음 조각을 설정 파일에 합칩니다. 조각의
   항목을 기존 항목 옆에 추가합니다. 기존 항목은 절대 지우거나 바꾸지 않습니다. 파일에 이미 다른 내용이 있으면,
   추가할 내용을 정확히 보여 주고 승인을 기다립니다. 원래 내용을 보관해 두고, 합친 파일이
   JSON(OpenCode는 JSONC)으로 해석되지 않으면 원래 내용으로 되돌립니다.
5. 강제 장치를 확인합니다.
   - `python3 guards/test_guard.py <설치한 판정기>`가 실패 없이 끝납니다.
   - 설치한 판정기의 SHA-256이 `guards/guard.py`의 SHA-256과 같습니다.
   - `python3 guards/test_guard.py --hook <claude|codex|agy>`가 실패 없이 끝납니다. 이 명령은
     설정 파일에 들어 있는 강제 장치 명령을 쓰인 그대로 시스템 shell로 모두 실행합니다. 막혀야
     하는 입력 하나와 허용되어야 하는 입력 하나를 넣습니다. credential은 열지 않습니다. 도구가
     다른 shell(예: Windows의 PowerShell)로 hook을 실행하면, 그 shell에서도 명령을 실행합니다.
   - OpenCode는 합친 파일을 다시 읽어 조각의 규칙이 모두 들어 있는지 확인합니다.
6. 위치, 두 SHA-256 값, 시험 결과를 보고합니다. Codex라면 사용자에게 Codex에서 `/hooks`를 열어
   새 hook을 신뢰하도록 요청합니다. Codex는 사용자가 신뢰하기 전까지 새 hook을 건너뜁니다.

| 도구 | 판정기 위치 | 설정 파일 | 설정 조각 |
|---|---|---|---|
| Claude Code | `~/.claude/hooks/ai-global-config-guard.py` | `~/.claude/settings.json` | `guards/claude-settings.json` |
| Codex CLI | `~/.codex/hooks/ai-global-config-guard.py` | `~/.codex/hooks.json` | `guards/codex-hooks.json` |
| Antigravity CLI (agy) | `~/.gemini/config/hooks/ai-global-config-guard.py` | `~/.gemini/config/hooks.json` | `guards/agy-hooks.json` |
| OpenCode | 없음: 권한 규칙만 씀 | `~/.config/opencode/opencode.jsonc` | `guards/opencode-permissions.json` |

강제 장치는 실수와 흔한 시도를 막습니다. 완전한 보안 경계는 아닙니다.

- 도구 호출의 글에서 이름을 찾아 판정합니다. 그래서 명령이 glob(`~/.n?trc`), 중괄호 확장, 변수,
  실행 중에 만든 문자열, 인코딩한 이름, 해석하지 못하는 형태로 바꾼 작업 디렉터리, glob이나 만든
  문자열 안의 심볼릭 링크, 앞서 쓴 스크립트로 비밀에 닿는 경우는 놓칠 수 있습니다.
- 존재 확인 예외는 `ls`, `stat`, `test`가 진짜 명령이라고 믿습니다. 같은 이름의 shell 함수나
  `PATH` 앞쪽의 파일이 있으면 그 확인이 읽기로 바뀔 수 있습니다.
- 강제 장치 자신과 hook 설정의 보호도 이름으로 판정하므로, 간접적으로 닿는 명령은 막지
  못합니다.
- 그런 파일 이름이 들어간 무해한 명령은 막을 수 있습니다. 예를 들어 `.ssh`를 언급하는 commit
  메시지나 `docker compose --env-file .env`가 그렇습니다.
- 사용자가 Rule SECRET-1에 따라 명시적으로 허락한 읽기도 막습니다. 사용자가 허락했는지 판정기는
  알 수 없기 때문입니다. 그 단계는 사용자가 도구 밖 터미널에서 합니다.
- 다른 hook(plugin, skill, 에이전트 정의, 작업 공간 파일에서 온 hook)은 강제 장치가 허용한
  도구 호출을 나중에 바꿀 수 있습니다.
- 시간 예산(약 4초)을 다 쓰거나 호출을 해석하지 못하면, 원문 글로 판정하고 애매하면 막습니다.
- Claude Code: `disableAllHooks`나 `--settings` 덮어쓰기는 강제 장치를 끕니다. `onFailure:
  "block"` 때문에, 판정기 스크립트가 지워지거나 망가지면 사용자가 hook 항목을 직접 지울 때까지
  모든 도구 호출이 막힙니다.
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
- OpenCode 권한 규칙은 명령 글 전체로 일치를 판단하므로 hook보다 거칩니다. 나중에 읽히는
  규칙(에이전트나 프로젝트의 규칙)이 경로를 다시 허용할 수 있습니다. 마지막에 일치한 규칙이
  이기기 때문입니다. V2 이전 버전은 `permissions` 대신 `permission` 키를 읽으므로, 그 버전에서는
  이 조각이 아무 일도 하지 않습니다. `grep` 동작의 resource는 경로가 아니라 검색 패턴입니다. 그래서
  규칙은 그런 이름이 든 패턴은 막지만, 그런 디렉터리 안의 검색은 막지 못합니다.

테스트 사례 23은 에이전트가 미끼 credential을 스스로 읽지 않는지 확인합니다. 테스트 사례 24는
사용자가 허락한 읽기를 강제 장치가 실제로 막는지 확인합니다.
