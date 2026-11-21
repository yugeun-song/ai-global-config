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
    r"|Library/Keychains|Microsoft/(?:Credentials|Protect|Vault)(?:/|$)"
    r"|\.docker/config\.json|\.kube/config(?![\w.-])|\.cargo/credentials"
    r"|\.claude/\.credentials\.json|\.claude/sessions/[^\s\"'/]*\.key"
    r"|\.codex/auth\.json|\.gemini/oauth_creds|\.hermes/(?:\.env|auth\.json)"
    r"|opencode/auth\.json|gh/hosts\.yml|GitHub CLI/hosts\.yml"
    r"|Login Data|logins\.json|key4\.db|(?:Default|Profile [0-9]+|Network)/Cookies(?![\w.-])"
    r"|(?:^|/)Local State(?![\w.-])|cookies\.sqlite"
    r"|\bsecret-tool\b|\bkwallet-query\b|\bcmdkey\b|\bvaultcmd\b|Get-StoredCredential|\bGet-Secret\b|\bPasswordVault\b"
    r"|\bgh\s+auth\s+token\b|\bsecurity\s+(?:find-(?:generic|internet)-password|dump-keychain)\b"
    r"|\bgcloud\s+auth\s+(?:application-default\s+)?print-(?:access|identity)-token\b"
    r"|\bkubectl\s+config\s+view\b[^\n]{0,300}?--raw|\bgit(?:\s+|-)credential(?:-[\w-]+)?(?:\.exe)?\s+(?:fill|get)\b",
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
    r"|\brsync\b|\bcp\s+(?:-\w*\s+)*-\w*[rRa]|\bfind\b|\bcpio\b|\bscp\b"
    r"|\b(?:Copy-Item|cpi|copy|cp|Get-ChildItem|gci)\b[^;&|\n]{0,200}?\s-r\w*"
    r"|\bCompress-Archive\b|\brobocopy\b|\bxcopy\b|\bSelect-String\b|\bsls\b|\bfindstr\b"
    r"|\bln\b|\bmklink\b|\bsubst\b|\b(?:New-Item|ni)\b[^;&|\n]{0,200}?\s-(?:Item)?Type\s+[\"']?(?:Junction|SymbolicLink|HardLink)\b",
    re.IGNORECASE,
)
HOME_SWEEPING = re.compile(
    r"\b(?:grep|egrep|fgrep)\s+(?:-\w*\s+)*-\w*[rR]|\brg\b|\bag\b|\back\b|\btar\b|\bzip\b|\b7z\b"
    r"|\brsync\b|\bcp\s+(?:-\w*\s+)*-\w*[rRa]|\bcpio\b|\bscp\b"
    r"|\b(?:Copy-Item|cpi|copy|cp)\b[^;&|\n]{0,200}?\s-r\w*"
    r"|\bCompress-Archive\b|\brobocopy\b|\bxcopy\b|\bSelect-String\b|\bsls\b|\bfindstr\b"
    r"|\bfind\b[^;&|\n]{0,300}?\s-(?:exec|execdir|ok|okdir)\b|\|\s*xargs\b"
    r"|\b(?:Get-ChildItem|gci|dir|ls)\b[^;&\n]{0,300}?\|\s*(?:Get-Content|gc|cat|type|Copy-Item|cpi)\b",
    re.IGNORECASE,
)
HOME_VAR = re.compile(r"^(?:\$HOME|\$\{HOME\}|\$env:USERPROFILE|\$env:HOME|%USERPROFILE%)(?=/|$)", re.IGNORECASE)
TRAILING_GLOB = re.compile(r"(?:/\*{1,2}(?:\.\*)?)+$")
CONTENT_SEARCH_TOOLS = {"grep", "grep_search"}
PROTECTED = re.compile(
    r"\.claude/settings[\w.-]*\.json|\.claude/hooks(?:/|$)"
    r"|\.codex/hooks\.json|\.codex/config\.toml|\.codex/hooks(?:/|$)"
    r"|\.gemini/config/hooks\.json|\.gemini/config/hooks(?:/|$)"
    r"|\.config/opencode/opencode\.jsonc?|(?:^|/)opencode\.jsonc?$|(?:^|/)\.opencode/"
    r"|\.claude/(?:skills|agents|plugins)/|(?:^|/)\.agents/hooks\.json|\.codex/plugins/|/etc/codex/"
    r"|\.codex/requirements\.toml|disableAllHooks",
    re.IGNORECASE,
)
READ_ONLY_COMMAND = re.compile(
    r"^(?![^\n]*\s--pre)(?![^\n]*\bless\s[^\n]*-[oO])\s*(?:cat|less|more|head|tail|grep|rg|jq|ls|stat|test|wc|file|diff"
    r"|Get-Content|type|git\s+(?:diff|log|show|status))\s[^;&|`$()<>\r\n]*(?:\|\s*jq\s[^;&|`$()<>\r\n]*)?\Z",
    re.IGNORECASE,
)
EXISTENCE_ONLY = re.compile(r"^\s*(?:ls|stat|test|\[|Test-Path|Get-Item)\s[^;&|`$()<>\r\n]*\Z", re.IGNORECASE)
ESCAPES = re.compile(r"[\"'\\`^]")
WORD_BREAK = re.compile(r"[\s;&|(){}<>,=]+")
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
    r"(?:^|[;&|({\s\"'])(?:cd|pushd|chdir|Set-Location|sl|Push-Location)(?:\s+(?:-[-\w]*|/d))*"
    r"\s+(\"[^\"\r\n]*\"|'[^'\r\n]*'|[^\s;&|)}]+)",
    re.IGNORECASE,
)
SEP = r"[\\/]" if os.name == "nt" else "/"
ROOT = re.compile(SEP + "*")
PART = re.compile(SEP)
DEVICE_PREFIX = re.compile(r"^[\\/]{2}[?.][\\/](?=[A-Za-z]:)")
REMOTE = re.compile(r"^(?:[\\/]{2}|\\\?\?\\)")
URL_WORDS = {"url", "uri", "href"}
FILE_URL = re.compile(r"^\s*file:(?://[^/?#]*)?(/[^?#]*)", re.IGNORECASE)
PERCENT = re.compile(r"%([0-9a-fA-F]{2})")
DRIVE_URL = re.compile(r"^/(?=[A-Za-z]:)")
HOOK_SWITCH = re.compile(r"disableAllHooks", re.IGNORECASE)
MAX_REALPATH = 4096
MAX_BASES = 8
REALPATH_BUDGET = 2000
EXISTS_BUDGET = 4000
DEADLINE = time.monotonic() + 4.0


class OverBudget(Exception):
    pass


budget = {"realpath": REALPATH_BUDGET, "exists": EXISTS_BUDGET}
cache = {}
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
BUDGET_REASON = (
    "Blocked by the ai-global-config guard: this tool call names more words or paths "
    "than the guard can check in time. Split it into smaller calls, or first write long "
    "text to a file with a file tool."
)
HOME_REASON = (
    "Blocked by the ai-global-config guard (Rule SECRET-1): this tool call searches, copies "
    "or archives the home directory or a directory above it, where credentials live. Name "
    "only the directories that the task needs."
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


def is_url_key(key):
    words = KEY_WORD.findall(key)
    return bool(words) and words[-1].lower() in URL_WORDS


def file_urls(args):
    for text in keyed(args, is_url_key):
        match = FILE_URL.match(text)
        if match:
            yield DRIVE_URL.sub("", PERCENT.sub(lambda m: chr(int(m.group(1), 16)), match.group(1)))


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


def counted(kind, key, compute):
    if (kind, key) not in cache:
        budget[kind] -= 1
        if budget[kind] < 0:
            raise OverBudget()
        cache[(kind, key)] = compute(key)
    return cache[(kind, key)]


def head(path):
    drive, rest = os.path.splitdrive(path)
    root = ROOT.match(rest).group()
    return drive + root + PART.split(rest[len(root):], maxsplit=1)[0]


def may_link(path, base):
    if os.path.isabs(path) or ".." in PART.split(path):
        return True
    first = head(os.path.normpath(path))
    first = os.path.join(base, first) if base else first
    return not REMOTE.match(first) and counted("exists", first, os.path.lexists)


def with_real(bases):
    found = list(bases)
    for base in bases:
        try:
            if base and os.path.isabs(base) and not REMOTE.match(base):
                found.append(counted("realpath", base, os.path.realpath))
        except (OSError, ValueError):
            pass
    return list(dict.fromkeys(found))


def path_forms(text, bases):
    forms = text_forms(text)
    raw = DEVICE_PREFIX.sub("", text.strip())
    if not raw or len(raw) > MAX_REALPATH or REMOTE.match(raw):
        return forms
    for base in bases:
        if time.monotonic() > DEADLINE:
            raise OverBudget()
        try:
            path = os.path.expanduser(raw)
            linked = may_link(path, base)
            if base and not os.path.isabs(path):
                path = os.path.join(base, path)
            path = os.path.normpath(path)
            forms.add(path.replace("\\", "/"))
            if linked and len(path) <= MAX_REALPATH and not REMOTE.match(path):
                forms.add(counted("realpath", path, os.path.realpath).replace("\\", "/"))
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
    return any(SECRET_DIRS.search(TRAILING_GLOB.sub("", form.replace("\\", "/")).rstrip("/")) for form in forms)


def expand(text):
    try:
        return os.path.expanduser(text)
    except (OSError, ValueError):
        return text


def covers_home(forms):
    home = os.path.normcase(os.path.expanduser("~")).replace("\\", "/").rstrip("/")
    for form in forms:
        raw = TRAILING_GLOB.sub("", HOME_VAR.sub("~", form.replace("\\", "/")))
        if raw.startswith("/") and not raw.strip("/"):
            return True
        path = os.path.normcase(raw).replace("\\", "/").rstrip("/")
        if path == "~" or (path and (path == home or home.startswith(path + "/"))):
            return True
    return False


def is_home(forms):
    home = os.path.normcase(os.path.expanduser("~")).replace("\\", "/").rstrip("/")
    return any(os.path.normcase(form).replace("\\", "/").rstrip("/") in ("~", home) for form in forms)


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


def command_words(command):
    slashed = command.replace("\\", "/")
    whole = tokens(command) + (tokens(slashed) if slashed != command else [])
    whole = list(dict.fromkeys(w for w in whole + WORD_BREAK.split(ESCAPES.sub(" ", slashed))[:2000] if w))
    pieces = ESCAPES.sub(" ", command).split()[:2000]
    return list(dict.fromkeys(whole + pieces)), whole


def check_command(command, bases):
    if not command:
        return "allow"
    command = DIRENV.sub("direnv", command)
    words, whole = command_words(command)
    cd_words = [m.strip("\"'") for m in CD.findall(command)]
    cd_bases = [expand(m) for m in cd_words]
    all_bases = list(dict.fromkeys(list(bases) + cd_bases))
    for word in words:
        if len(all_bases) >= MAX_BASES:
            break
        found = path_forms(word, list(bases))
        if names_secret_dir(found) or is_home(found):
            all_bases.append(expand(word))
    all_bases = with_real(list(dict.fromkeys(all_bases))[:MAX_BASES])
    word_forms = set()
    whole_forms = set()
    whole_set = set(whole)
    for word in words:
        found = path_forms(word, all_bases)
        word_forms |= found
        if word in whole_set:
            whole_forms |= found
    forms = text_forms(command) | word_forms
    if names_secret(forms) and not EXISTENCE_ONLY.match(command):
        if not IGNORE_APPEND.match(command) and not ENV_FROM_EXAMPLE.match(command):
            return "deny"
    if SWEEPING.search(command) and names_secret_dir(whole_forms):
        return "deny"
    if HOME_SWEEPING.search(command):
        skip = {form for word in cd_words for form in (word, word.replace("\\", "/"))}
        home_bases = with_real(cd_bases[:MAX_BASES]) if cd_bases else list(bases)
        if any(word and word not in skip and covers_home(path_forms(word, home_bases)) for word in whole):
            return "home"
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
    bases = with_real(bases)
    result = "allow"
    if name in SHELL_TOOLS:
        for key in SHELL_KEYS:
            if key in lowered:
                found = check_command(joined(lowered[key]), bases)
                if found in ("deny", "home"):
                    return found
                if found == "ask":
                    result = "ask"
        if not any(k in lowered for k in SHELL_KEYS) and names_secret(text_forms(joined(args))):
            return "deny"
    paths = list(keyed(args, is_path_key)) + list(file_urls(args))
    targets = list(patch_targets(args))
    for key in SEARCH_GLOB_KEYS.get(name, ()):
        if key in lowered:
            roots = [p for p in paths if p] or [cwd]
            paths += [os.path.join(r, joined(lowered[key])) if r else joined(lowered[key]) for r in roots]
    if name not in SHELL_TOOLS and name not in WRITE_TOOLS and name not in READ_ONLY_TOOLS:
        for key in SHELL_KEYS:
            if key in lowered:
                found = check_command(joined(lowered[key]), bases)
                if found in ("deny", "home"):
                    return found
                if found == "ask":
                    result = "ask"
    for path in paths + targets:
        if path and names_secret(path_forms(path, bases)):
            return "deny"
    if name in SEARCH_GLOB_KEYS:
        if any(path and names_secret_dir(path_forms(path, bases)) for path in paths):
            return "deny"
    if name in CONTENT_SEARCH_TOOLS:
        roots = [p for p in keyed(args, is_path_key) if p] or [cwd]
        if any(root and covers_home(path_forms(root, bases)) for root in roots):
            return "home"
    if name not in READ_ONLY_TOOLS:
        if any(path and names_protected(path_forms(path, bases)) for path in paths + targets):
            result = "ask"
        if name not in SHELL_TOOLS and any(HOOK_SWITCH.search(text) for text in strings(args)):
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
    reason = {"deny": REASON, "budget": BUDGET_REASON, "home": HOME_REASON}.get(decision, PROTECT_REASON)
    if fmt == "agy":
        sys.stdout.write(json.dumps({"decision": "force_ask" if decision == "ask" else "deny", "reason": reason}))
        sys.exit(0)
    if fmt == "claude" and decision == "ask":
        sys.stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }}))
        sys.exit(0)
    sys.stderr.write(reason + "\n")
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
        decision = "budget"
    except Exception:
        decision = fallback(raw)
    respond(fmt, decision)


if __name__ == "__main__":
    main()
