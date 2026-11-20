import json
import os
import re
import shlex
import sys
import time

SECRET = re.compile(
    r"(?<![\w.-])\.ssh(?![\w.-])|(?<![\w.-])SSH~\d"
    r"|(?<![\w.-])\.gnupg(?![\w.-])|(?<![\w.-])GNUPG~\d"
    r"|(?<![\w.-])[._]netrc(?![\w.-])|(?<![\w.-])NETRC~\d"
    r"|(?<![\w.-])\.git-credentials(?![\w.-])"
    r"|(?<![\w.-])\.pypirc(?![\w.-])|(?<![\w.-])\.npmrc(?![\w.-])"
    r"|(?<![\w.-])\.password-store(?![\w.-])|(?<![\w.-])\.pgpass(?![\w.-])|(?<![\w.-])\.envrc(?![\w.-])"
    r"|(?<![\w.-])\.vault-token(?![\w.-])|(?<![\w.-])\.s3cfg(?![\w.-])|\.config/git/credentials"
    r"|github-copilot/(?:apps|hosts)\.json|\.azure(?:/|$)|\.terraform\.d/credentials|rclone/rclone\.conf"
    r"|\.aws/credentials|(?:\.config|AppData/Roaming)/gcloud(?![\w.-])|(?:^|/)keyrings(?:/|$)"
    r"|Library/Keychains|\.docker/config\.json|\.kube/config(?![\w.-])|\.cargo/credentials"
    r"|\.claude/\.credentials\.json|\.claude/sessions/[^\s\"'/]*\.key"
    r"|\.codex/auth\.json|\.gemini/oauth_creds|\.hermes/(?:\.env|auth\.json)"
    r"|opencode/auth\.json|gh/hosts\.yml|GitHub CLI/hosts\.yml"
    r"|Login Data|logins\.json|key4\.db"
    r"|\bsecret-tool\b|\bkwallet-query\b|\bcmdkey\b|Get-StoredCredential"
    r"|\bgh\s+auth\s+token\b|\bsecurity\s+(?:find-(?:generic|internet)-password|dump-keychain)\b"
    r"|\bgcloud\s+auth\s+(?:application-default\s+)?print-(?:access|identity)-token\b"
    r"|\bkubectl\s+config\s+view\b[^\n]{0,300}?--raw|\bgit\s+credential(?:-\w+)?\s+(?:fill|get)\b",
    re.IGNORECASE,
)
ENV_FILE = re.compile(
    r"(?<![\w.-])(?:\.env|(?:prod|production|dev|development|stage|staging|test|local|secrets?)\.env)((?:[._-][\w-]+)*)(?![\w.-])",
    re.IGNORECASE,
)
ENV_ALLOWED = (".example", ".sample", ".template", ".dist")
HOME_PREFIX = r"(?:~|\$HOME|\$\{HOME\}|\$env:USERPROFILE|%USERPROFILE%|/home/[^/]+|/Users/[^/]+|/root|[A-Za-z]:/Users/[^/]+|" + re.escape(os.path.expanduser("~").replace("\\", "/")) + r")"
SECRET_DIRS = re.compile(
    r"^" + HOME_PREFIX + r"/(?:\.aws|\.codex|\.claude|\.gemini|\.hermes|\.docker|\.kube|\.cargo|\.config/gh"
    r"|\.local/share/opencode)/?$",
    re.IGNORECASE,
)
SECRET_DIR_NAME = re.compile(
    r"(?<![\w.-])(?:\.aws|\.codex|\.claude|\.gemini|\.hermes|\.docker|\.kube|\.cargo|\.config/gh|\.local/share/opencode)(?![\w.-])",
    re.IGNORECASE,
)
SWEEPING = re.compile(
    r"\b(?:grep|egrep|fgrep)\s+(?:-\w*\s+)*-\w*[rR]|\brg\b|\bag\b|\back\b|\btar\b|\bzip\b|\b7z\b"
    r"|\brsync\b|\bcp\s+(?:-\w*\s+)*-\w*[rRa]|\bfind\b|\bcpio\b|\bscp\b",
    re.IGNORECASE,
)
PROTECTED = re.compile(
    r"\.claude/settings[\w.-]*\.json|\.claude/hooks(?:/|$)"
    r"|\.codex/hooks\.json|\.codex/config\.toml|\.codex/hooks(?:/|$)"
    r"|\.gemini/config/hooks\.json|\.gemini/config/hooks(?:/|$)"
    r"|\.config/opencode/opencode\.jsonc?|(?:^|/)opencode\.jsonc?$|(?:^|/)\.opencode/"
    r"|\.claude/(?:skills|agents|plugins)/|(?:^|/)\.agents/hooks\.json|\.codex/plugins/|/etc/codex/"
    r"|\.codex/requirements\.toml",
    re.IGNORECASE,
)
READ_ONLY_COMMAND = re.compile(
    r"^(?![^\n]*\s--pre)(?![^\n]*\bless\s[^\n]*-[oO])\s*(?:cat|less|more|head|tail|grep|rg|jq|ls|stat|test|wc|file|diff"
    r"|Get-Content|type|git\s+(?:diff|log|show|status))\s[^;&|`$()<>\r\n]*(?:\|\s*jq\s[^;&|`$()<>\r\n]*)?\Z",
    re.IGNORECASE,
)
EXISTENCE_ONLY = re.compile(r"^\s*(?:ls|stat|test|\[|Test-Path|Get-Item)\s[^;&|`$()<>\r\n]*\Z", re.IGNORECASE)
ESCAPES = re.compile(r"[\"'\\`^]")
UNICODE_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")
SHELL_TOOLS = {"bash", "shell", "exec_command", "run_command", "powershell", "write_stdin", "monitor"}
SHELL_KEYS = ("command", "commandline", "cmd", "chars", "input")
WRITE_TOOLS = {"apply_patch", "write", "edit", "write_file", "edit_file", "multiedit", "notebookedit", "write_to_file", "replace_file_content", "multi_replace_file_content"}
READ_ONLY_TOOLS = {"read", "read_file", "grep", "glob", "view_file", "list_dir", "find_by_name", "grep_search", "websearch", "webfetch", "search_web", "read_url_content", "todowrite", "agent", "task"}
SEARCH_GLOB_KEYS = {"grep": ("glob",), "glob": ("pattern",), "grep_search": ("includes",), "find_by_name": ("pattern",)}
PATH_WORDS = {"path", "paths", "file", "files", "filename", "dir", "dirs", "directory", "target", "cwd", "workdir", "location", "uri"}
KEY_WORD = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])")
WORKDIR_KEYS = ("workdir", "cwd", "working_directory")
IGNORE_APPEND = re.compile(r"^\s*(?:echo|printf)\s+[^;&|`$()<>\r\n]*>>?\s*[\w./-]*\.(?:git|docker)ignore\s*\Z", re.IGNORECASE)
ENV_FROM_EXAMPLE = re.compile(r"^\s*(?:cp|Copy-Item)\s+[\w./-]*\.env\.(?:example|sample|template|dist)\s+[\w./-]*\.env\s*\Z", re.IGNORECASE)
PATCH_HEADER = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.*)$|^\*\*\* Move to: (.*)$", re.MULTILINE)
DIRENV = re.compile(r"\bdirenv\s+(?:allow|deny|block|permit|revoke)\s+[\w./-]*\.envrc(?![\w.-])", re.IGNORECASE)
CD = re.compile(
    r"(?:^|[;&|({\s\"'])(?:cd|pushd|chdir|Set-Location|sl)(?:\s+(?:-[-\w]*|-Path|-LiteralPath))*\s+([^\s;&|)}]+)",
    re.IGNORECASE,
)
MAX_REALPATH = 4096
MAX_BASES = 8
REALPATH_BUDGET = 500
DEADLINE = time.monotonic() + 4.0


class OverBudget(Exception):
    pass


budget = {"realpath": REALPATH_BUDGET}
REASON = (
    "Blocked by the ai-global-config guard (Rule SECRET-1): this tool call names "
    "a credential or a secret store. Only one plain ls, stat or test (Test-Path on "
    "Windows) may name one, to check that it exists. If the task needs the secret, "
    "ask the user to do that step."
)
PROTECT_REASON = (
    "The ai-global-config guard protects its own script and the hook settings. "
    "Change them only with the user's approval."
)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key in sorted(value, key=str):
            yield from strings(value[key])


def is_path_key(key):
    words = KEY_WORD.findall(key)
    return bool(words) and words[-1].lower() in PATH_WORDS


def keyed(value, wanted):
    if isinstance(value, dict):
        for key in sorted(value, key=str):
            item = value[key]
            if wanted(str(key)) and (isinstance(item, str) or (isinstance(item, list) and all(isinstance(i, str) for i in item))):
                yield from strings(item)
            else:
                yield from keyed(item, wanted)
    elif isinstance(value, list):
        for item in value:
            yield from keyed(item, wanted)


def joined(value):
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    if isinstance(value, str):
        return value
    return " ".join(strings(value))


def collapse(text):
    text = re.sub(r"/{2,}", "/", text)
    while "/./" in text:
        text = text.replace("/./", "/")
    return text


def text_forms(text):
    slashed = text.replace("\\", "/")
    forms = {text, slashed, ESCAPES.sub("", text), ESCAPES.sub("", slashed)}
    return {collapse(f).rstrip(". ") for f in forms} | {collapse(f) for f in forms}


def path_forms(text, bases):
    forms = text_forms(text)
    raw = text.strip()
    if not raw or len(raw) > MAX_REALPATH or raw.startswith(("\\\\", "//")):
        return forms
    for base in bases:
        if time.monotonic() > DEADLINE:
            raise OverBudget()
        try:
            path = os.path.expanduser(raw)
            if base and not os.path.isabs(path):
                path = os.path.join(base, path)
            path = os.path.normpath(path)
            forms.add(path.replace("\\", "/"))
            if len(path) <= MAX_REALPATH and not path.startswith(("\\\\", "//")):
                budget["realpath"] -= 1
                if budget["realpath"] < 0:
                    raise OverBudget()
                forms.add(os.path.realpath(path).replace("\\", "/"))
        except (OSError, ValueError):
            pass
    return forms


def names_secret(forms):
    for form in forms:
        if SECRET.search(form):
            return True
        for match in ENV_FILE.finditer(form):
            if not match.group(1).lower().endswith(ENV_ALLOWED):
                return True
    return False


def names_protected(forms):
    return any(PROTECTED.search(form) for form in forms)


def names_secret_dir(forms):
    return any(SECRET_DIRS.search(form.rstrip("/")) for form in forms)


def expand(text):
    try:
        return os.path.expanduser(text)
    except (OSError, ValueError):
        return text


def is_home(forms):
    home = os.path.expanduser("~").replace("\\", "/").rstrip("/")
    return any(form.rstrip("/") in ("~", home) for form in forms)


def tokens(command):
    if len(command) > 20000:
        return command.split()[:2000]
    try:
        return shlex.split(command, posix=True)[:2000]
    except ValueError:
        return command.split()[:2000]


def patch_targets(args):
    for text in strings(args):
        if "*** Begin Patch" in text or "*** Add File:" in text or "*** Update File:" in text:
            for added, moved in PATCH_HEADER.findall(text):
                yield added or moved


def check_command(command, bases):
    if not command:
        return "allow"
    command = DIRENV.sub("direnv", command)
    words = list(dict.fromkeys(tokens(command) + ESCAPES.sub(" ", command).split()[:2000]))
    all_bases = list(dict.fromkeys(list(bases) + [expand(m) for m in CD.findall(command)]))
    for word in words:
        if len(all_bases) >= MAX_BASES:
            break
        found = path_forms(word, list(bases))
        if names_secret_dir(found) or is_home(found):
            all_bases.append(expand(word))
    all_bases = list(dict.fromkeys(all_bases))[:MAX_BASES]
    word_forms = set()
    for word in words:
        word_forms |= path_forms(word, all_bases)
    forms = text_forms(command) | word_forms
    if names_secret(forms) and not EXISTENCE_ONLY.match(command):
        if not IGNORE_APPEND.match(command) and not ENV_FROM_EXAMPLE.match(command):
            return "deny"
    if SWEEPING.search(command) and names_secret_dir(word_forms):
        return "deny"
    if names_protected(forms) and not READ_ONLY_COMMAND.match(command):
        return "ask"
    return "allow"


def verdict(tool, args, cwd):
    name = str(tool).lower()
    bases = [cwd] if cwd else [None]
    if not isinstance(args, dict):
        forms = text_forms(joined(args))
        if names_secret(forms):
            return "deny"
        return "ask" if names_protected(forms) else "allow"
    lowered = {str(k).lower(): v for k, v in args.items()}
    for key in WORKDIR_KEYS:
        if isinstance(lowered.get(key), str):
            bases = [lowered[key]] + bases
    result = "allow"
    if name in SHELL_TOOLS:
        for key in SHELL_KEYS:
            if key in lowered:
                found = check_command(joined(lowered[key]), bases)
                if found == "deny":
                    return "deny"
                if found == "ask":
                    result = "ask"
        if not any(k in lowered for k in SHELL_KEYS) and names_secret(text_forms(joined(args))):
            return "deny"
    paths = list(keyed(args, is_path_key))
    targets = list(patch_targets(args))
    for key in SEARCH_GLOB_KEYS.get(name, ()):
        if key in lowered:
            roots = [p for p in paths if p] or [cwd]
            paths += [os.path.join(r, joined(lowered[key])) if r else joined(lowered[key]) for r in roots]
    if name not in SHELL_TOOLS and name not in WRITE_TOOLS and name not in READ_ONLY_TOOLS:
        for key in SHELL_KEYS:
            if key in lowered:
                found = check_command(joined(lowered[key]), bases)
                if found == "deny":
                    return "deny"
                if found == "ask":
                    result = "ask"
    for path in paths + targets:
        if path and names_secret(path_forms(path, bases)):
            return "deny"
    if name in SEARCH_GLOB_KEYS:
        if any(path and names_secret_dir(path_forms(path, bases)) for path in paths):
            return "deny"
    if name not in READ_ONLY_TOOLS:
        if any(path and names_protected(path_forms(path, bases)) for path in paths + targets):
            result = "ask"
    return result


def fallback(raw):
    decoded = UNICODE_ESCAPE.sub(lambda m: chr(int(m.group(1), 16)), raw)
    forms = text_forms(decoded)
    if names_secret(forms) or any(SECRET_DIR_NAME.search(form) for form in forms):
        return "deny"
    if names_protected(forms):
        return "ask"
    return "allow"


def respond(fmt, decision):
    if decision == "allow":
        if fmt == "agy":
            sys.stdout.write(json.dumps({"decision": "allow"}))
        sys.exit(0)
    if fmt == "agy":
        out = {"decision": "deny", "reason": REASON}
        if decision == "ask":
            out = {"decision": "force_ask", "reason": PROTECT_REASON}
        sys.stdout.write(json.dumps(out))
        sys.exit(0)
    if fmt == "claude" and decision == "ask":
        sys.stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": PROTECT_REASON,
        }}))
        sys.exit(0)
    sys.stderr.write((REASON if decision == "deny" else PROTECT_REASON) + "\n")
    sys.exit(2)


def main():
    fmt = sys.argv[1] if len(sys.argv) == 2 else ""
    if fmt not in ("claude", "codex", "agy"):
        sys.stderr.write("ai-global-config guard: usage: guard.py <claude|codex|agy>\n")
        sys.exit(2)
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError("not an object")
        if fmt == "agy":
            call = event.get("toolCall") or {}
            tool, args = call.get("name", ""), call.get("args", {})
            cwd = (args.get("Cwd") if isinstance(args, dict) else None) or event.get("cwd") or next(iter(event.get("workspacePaths") or []), None)
        else:
            tool, args, cwd = event.get("tool_name", ""), event.get("tool_input", {}), event.get("cwd")
        decision = verdict(tool, args, cwd if isinstance(cwd, str) else None)
    except OverBudget:
        decision = "deny"
    except Exception:
        decision = fallback(raw)
    respond(fmt, decision)


if __name__ == "__main__":
    main()
