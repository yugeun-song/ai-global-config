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
