import json
import os
import re
import shlex
import sys
import time

OPTION_REACH = 300
REACH = "{0,%d}?" % OPTION_REACH
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
    r"|\bkubectl\s+config\s+view\b[^\n]" + REACH + r"--raw|\bgit(?:\s+|-)credential(?:-[\w-]+)?(?:\.exe)?\s+(?:fill|get)\b",
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
    r"\b(?:grep|egrep|fgrep)\s+(?:-\w*\s+)*-\w*[rR]|\brg\b|\bag\b|\back\b|(?<![.\w-])(?:tar|zip|7z)\b"
    r"|\brsync\b|\bcp\s+(?:-\w*\s+)*-\w*[rRa]|\bfind\b|\bcpio\b|\bscp\b"
    r"|\b(?:Copy-Item|cpi|copy|cp|Get-ChildItem|gci)\b[^;&|\n]" + REACH + r"\s-r\w*"
    r"|\bCompress-Archive\b|\brobocopy\b|\bxcopy\b|\bSelect-String\b|\bsls\b|\bfindstr\b"
    r"|\bln\b|\bmklink\b|\bsubst\b|\b(?:New-Item|ni)\b[^;&|\n]" + REACH + r"\s-(?:Item)?Type\s+[\"']?(?:Junction|SymbolicLink|HardLink)\b",
    re.IGNORECASE,
)
HOME_SWEEPING = re.compile(
    r"\b(?:grep|egrep|fgrep)\s+(?:-\w*\s+)*-\w*[rR]|\brg\b|\bag\b|\back\b|(?<![.\w-])(?:tar|zip|7z)\b"
    r"|\brsync\b|\bcp\s+(?:-\w*\s+)*-\w*[rRa]|\bcpio\b|\bscp\b"
    r"|\b(?:Copy-Item|cpi|copy|cp)\b[^;&|\n]" + REACH + r"\s-r\w*"
    r"|\bCompress-Archive\b|\brobocopy\b|\bxcopy\b|\bSelect-String\b|\bsls\b|\bfindstr\b"
    r"|\bfind\b[^;&|\n]" + REACH + r"\s-(?:exec|execdir|ok|okdir)\b|\|\s*xargs\b"
    r"|\b(?:Get-ChildItem|gci|dir|ls)\b[^;&\n]" + REACH + r"\|\s*(?:Get-Content|gc|cat|type|Copy-Item|cpi)\b",
    re.IGNORECASE,
)
HOME_VAR = re.compile(r"^(?:\$HOME|\$\{HOME\}|\$env:USERPROFILE|\$env:HOME|%USERPROFILE%)(?=/|$)", re.IGNORECASE)
DRIVE_ROOT = re.compile(r"^[A-Za-z]:/(?:\*{1,2}(?:\.\*)?/?)*$")
TRAILING_GLOB = re.compile(r"(?:/\*{1,2}(?:\.\*)?)+$")
CONTENT_SEARCH_TOOLS = {"grep", "grep_search", "search_file_content"}
MULTI_READ_TOOLS = {"read_many_files"}
PROTECTED = re.compile(
    r"\.claude/settings[\w.-]*\.json|\.claude/hooks(?:/|$)"
    r"|\.codex/hooks\.json|\.codex/config\.toml|\.codex/hooks(?:/|$)"
    r"|\.gemini/config/hooks\.json|\.gemini/config/hooks(?:/|$)"
    r"|\.gemini/settings\.json|\.gemini/hooks(?:/|$)"
    r"|\.config/opencode/opencode\.jsonc?|(?:^|/)opencode\.jsonc?$|(?:^|/)\.opencode/"
    r"|\.claude/(?:skills|agents|plugins)/|(?:^|/)\.agents/hooks\.json|\.codex/plugins/|/etc/codex/"
    r"|\.codex/requirements\.toml|disableAllHooks",
    re.IGNORECASE,
)
EXISTENCE_ONLY = re.compile(r"^\s*(?:ls|stat|test|\[|Test-Path|Get-Item)\s[^;&|`$()<>\r\n]*\Z", re.IGNORECASE)
ESCAPES = re.compile(r"[\"'\\`^]")
WORD_BREAK = re.compile(r"[\s;&|(){}<>,=]+")
UNICODE_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")
SHELL_TOOLS = {"bash", "shell", "exec_command", "run_command", "run_shell_command", "powershell", "write_stdin", "monitor"}
SHELL_KEYS = ("command", "commandline", "cmd", "chars", "input")
WRITE_TOOLS = {"apply_patch", "write", "edit", "write_file", "edit_file", "replace", "multiedit", "notebookedit", "write_to_file", "replace_file_content", "multi_replace_file_content"}
READ_ONLY_TOOLS = {
    "read", "read_file", "read_many_files", "grep", "glob", "view_file", "list_dir",
    "list_directory", "find_by_name", "grep_search", "search_file_content",
    "websearch", "webfetch", "search_web", "google_web_search", "web_fetch",
    "read_url_content", "todowrite", "agent", "task", "ask_user",
    "invoke_subagent", "ask_question",
}
SEARCH_GLOB_KEYS = {
    "grep": ("glob",),
    "glob": ("pattern",),
    "grep_search": ("includes", "include", "include_pattern"),
    "search_file_content": ("include", "includes", "include_pattern", "glob"),
    "find_by_name": ("pattern",),
    "read_many_files": ("include", "paths"),
}
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
PURE_CD = re.compile(
    r"^\s*(?:cd|pushd|chdir|Set-Location|sl|Push-Location)(?:\s+(?:-[-\w]*|/d))*"
    r"\s+(\"[^\"\r\n]*\"|'[^'\r\n]*'|[^\s;&|)}]+)\s*\Z",
    re.IGNORECASE,
)
STDERR_SAFE = re.compile(r"(?:^|\s)2>(?:&1|/dev/null)(?=\s|$)")
READ_ONLY_CMDS = {
    "cat", "less", "more", "head", "tail", "grep", "egrep", "fgrep", "rg", "jq",
    "ls", "stat", "test", "[", "wc", "file", "diff", "cmp", "sha256sum", "shasum",
    "md5sum", "cksum", "readlink", "realpath", "which", "true", "false",
    "get-content", "get-filehash", "get-item", "get-childitem", "test-path", "type", "dir",
    "echo", "printf", "write-output",
}
READ_ONLY_PIPE_SINKS = {
    "jq", "head", "tail", "grep", "egrep", "fgrep", "rg", "wc", "sort", "uniq",
    "cut", "tr", "cat", "less", "more", "select-object", "select-string",
    "format-table", "format-list",
}
READ_ONLY_GIT_SUBS = {"status", "diff", "log", "show", "rev-parse", "ls-files", "check-ignore"}
GIT_GLOBAL_VALUE_FLAGS = {"-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--super-prefix"}
GIT_MESSAGE_SUBS = {"commit", "tag", "merge", "notes"}
GIT_SHORT_M = re.compile(r"^-[asevqnoSu]*m$")
HEREDOC_OPEN = re.compile(r"<<(-?)([\"'])([A-Za-z0-9_]+)\2")
CAT_MESSAGE = re.compile(
    r"(?:^|\s)(?:-[asevqnoSu]*m|--message|--title|--body|--notes|--subject|--body-file)"
    r"(?:\s+|=)\"\$\(\s*cat\s*$"
)
CAT_MESSAGE_CLOSE = re.compile(r"\s*\)\"")
MESSAGE_SOURCES = {"echo", "printf", "write-output"}
GH_TEXT_SUBS = {"pr", "issue", "release"}
GH_TEXT_ACTIONS = {"create", "edit", "comment", "review", "merge"}
GH_TEXT_FLAGS = {"--title", "-t", "--body", "-b", "--notes", "-n", "--subject"}
PYTHON_CMD = re.compile(r"^(?:python(?:\d+(?:\.\d*)?)?|py)(?:\.exe)?$", re.IGNORECASE)
PYTHON_SAFE_FLAGS = {"-I", "-S", "-B", "-u", "-E", "-s"}
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
MAX_SEGMENTS = 100
MAX_WORDS = 2000
MAX_PARSED_CHARS = 20000
MAX_SEGMENTED_CHARS = 40000
MAX_STRIPPED_CHARS = 200000
REALPATH_BUDGET = 2000
EXISTS_BUDGET = 4000
CHECK_SECONDS = 4.0
DEADLINE = time.monotonic() + CHECK_SECONDS


class OverBudget(Exception):
    pass


budget = {"realpath": REALPATH_BUDGET, "exists": EXISTS_BUDGET}
cache = {}
path_cache = {}
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


def is_path_key_for(tool_name, key):
    if tool_name == "edit_file" and key.lower() == "target":
        return False
    return is_path_key(key)


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


def resolve_one(expanded, base):
    key = (expanded, base)
    cached = path_cache.get(key)
    if cached is not None:
        return cached
    if time.monotonic() > DEADLINE:
        raise OverBudget()
    resolved = []
    try:
        linked = may_link(expanded, base)
        path = os.path.join(base, expanded) if base and not os.path.isabs(expanded) else expanded
        path = os.path.normpath(path)
        resolved.append(path.replace("\\", "/"))
        if linked and len(path) <= MAX_REALPATH and not REMOTE.match(path):
            resolved.append(counted("realpath", path, os.path.realpath).replace("\\", "/"))
    except (OSError, ValueError):
        pass
    out = tuple(resolved)
    path_cache[key] = out
    return out


def path_forms(text, bases):
    forms = text_forms(text)
    raw = DEVICE_PREFIX.sub("", text.strip())
    if not raw or len(raw) > MAX_REALPATH or REMOTE.match(raw):
        return forms
    try:
        expanded = os.path.expanduser(raw)
    except (OSError, ValueError):
        return forms
    iter_bases = (None,) if os.path.isabs(expanded) else bases
    for base in iter_bases:
        forms.update(resolve_one(expanded, base))
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
        slashed = form.replace("\\", "/")
        if DRIVE_ROOT.match(slashed):
            return True
        raw = TRAILING_GLOB.sub("", HOME_VAR.sub("~", slashed))
        if raw.startswith("/") and not raw.strip("/"):
            return True
        path = os.path.normcase(raw).replace("\\", "/").rstrip("/")
        if path == "~" or (path and (path == home or home.startswith(path + "/"))):
            return True
    return False


def is_home(forms):
    home = os.path.normcase(os.path.expanduser("~")).replace("\\", "/").rstrip("/")
    return any(os.path.normcase(form).replace("\\", "/").rstrip("/") in ("~", home) for form in forms)


def here_string_end(text, i):
    if not text.startswith(("@'", '@"'), i):
        return None
    start = i + 2
    if text.startswith("\r\n", start):
        start += 1
    if not text.startswith("\n", start):
        return None
    end = text.find("\n" + text[i + 1] + "@", start)
    return len(text) if end == -1 else end + 3


def split_segments(command):
    if len(command) > MAX_SEGMENTED_CHARS:
        return [("", command)]
    segments = []
    start = 0
    prev_sep = ""
    quote = None
    depth = 0
    i = 0
    n = len(command)
    while i < n:
        ch = command[i]
        if quote is not None:
            if quote == '"' and ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            i += 2
            continue
        end = here_string_end(command, i)
        if end is not None:
            i = end
            continue
        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue
        if ch == "(":
            depth += 1
            i += 1
            continue
        if ch == ")" and depth > 0:
            depth -= 1
            i += 1
            continue
        if depth == 0:
            sep = None
            if ch in (";", "\n"):
                sep = ch
            elif ch == "&" and i + 1 < n and command[i + 1] == "&":
                sep = "&&"
            elif ch == "|" and i + 1 < n and command[i + 1] == "|":
                sep = "||"
            if sep is not None:
                segments.append((prev_sep, command[start:i]))
                prev_sep = sep
                i += len(sep)
                start = i
                if len(segments) >= MAX_SEGMENTS:
                    break
                continue
        i += 1
    segments.append((prev_sep, command[start:]))
    return segments


def is_safe_literal_quote(raw):
    if len(raw) < 2:
        return False
    if raw[0] == "'" and raw[-1] == "'":
        return raw.count("'") == 2
    if raw.startswith("@'\n") or raw.startswith("@'\r\n"):
        return raw.endswith("\n'@") and raw.find("\n'@") == len(raw) - 3
    if raw[0] == '"' and raw[-1] == '"':
        if "$(" in raw or "`" in raw or "<(" in raw or ">(" in raw:
            return False
        i = 1
        end = len(raw) - 1
        while i < end:
            if raw[i] == "\\" and i + 1 < end:
                i += 2
                continue
            if raw[i] == '"':
                return False
            i += 1
        return True
    return False


def scan_simple_tokens(text):
    toks = []
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i] in " \t\r":
            i += 1
        if i >= n:
            break
        ch = text[i]
        if ch in ";|&<>()\n`":
            break
        if ch == "$" and i + 1 < n and text[i + 1] == "(":
            break
        start = i
        if text[i:i + 3] == "@'\n" or text[i:i + 4] == "@'\r\n":
            end_marker = text.find("\n'@", i + 2)
            if end_marker == -1:
                break
            i = end_marker + 3
            toks.append((start, i, text[start:i]))
            continue
        while i < n and text[i] not in " \t\r;|&<>()\n`":
            if text[i] == "$" and i + 1 < n and text[i + 1] == "(":
                break
            if text[i] == "'":
                j = text.find("'", i + 1)
                if j == -1:
                    return toks
                i = j + 1
            elif text[i] == '"':
                j = i + 1
                while j < n:
                    if text[j] == "\\" and j + 1 < n:
                        j += 2
                        continue
                    if text[j] == '"':
                        j += 1
                        break
                    j += 1
                else:
                    return toks
                i = j
            elif text[i] == "\\" and i + 1 < n:
                i += 2
            else:
                i += 1
        toks.append((start, i, text[start:i]))
    return toks


def git_subcommand_index(toks):
    if not toks or toks[0][2].lower() not in ("git", "git.exe"):
        return None
    i = 1
    while i < len(toks):
        word = toks[i][2]
        if word in ("-C", "-c") or word.lower() in GIT_GLOBAL_VALUE_FLAGS:
            i += 2
            continue
        if word.startswith("-"):
            i += 1
            continue
        return i
    return None


def reads_stdin_message(words):
    return any(
        w == "--file=-" or (w in ("-F", "--file", "--body-file") and k + 1 < len(words) and words[k + 1] == "-")
        for k, w in enumerate(words)
    )


def strip_git_heredocs(command):
    lowered = command.lower()
    if "<<" not in command or ("git" not in lowered and "gh" not in lowered):
        return command
    lines = command.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        match = HEREDOC_OPEN.search(line)
        if match:
            strip_tabs = match.group(1) == "-"
            delim = match.group(3)
            prefix = line[:match.start()]
            segs = split_segments(prefix)
            tail = segs[-1][1] if segs else ""
            toks = scan_simple_tokens(tail)
            found = message_options(toks)
            literal = in_cat = False
            if found is not None:
                k, _, _ = found
                if CAT_MESSAGE.search(tail) and not line[match.end():].strip():
                    literal = in_cat = True
                elif reads_stdin_message([t[2] for t in toks[k:]]):
                    literal = True
            if literal:
                j = i + 1
                found_end = None
                while j < len(lines):
                    candidate = lines[j].rstrip("\r\n")
                    if strip_tabs:
                        candidate = candidate.lstrip("\t")
                    if candidate == delim:
                        found_end = j
                        break
                    j += 1
                if found_end is not None and (not in_cat or CAT_MESSAGE_CLOSE.match("".join(lines[found_end + 1:]))):
                    out.append("_\n")
                    out.append(lines[found_end])
                    i = found_end + 1
                    continue
        i += 1
    return "".join(out)


def safe_message_source(text):
    toks = scan_simple_tokens(text)
    if not toks or text[toks[-1][1]:].strip():
        return False
    if len(toks) == 1:
        return toks[0][2].startswith("@'") and is_safe_literal_quote(toks[0][2])
    if toks[0][2].lower() not in MESSAGE_SOURCES:
        return False
    for _, _, word in toks[1:]:
        if word[0] in "'\"@":
            if not is_safe_literal_quote(word):
                return False
        elif "'" in word or '"' in word:
            return False
    return True


def message_options(toks):
    sub_idx = git_subcommand_index(toks)
    if sub_idx is not None and toks[sub_idx][2] in GIT_MESSAGE_SUBS:
        return sub_idx + 1, lambda w: w in ("-m", "--message") or bool(GIT_SHORT_M.match(w)), ("--message=",)
    if len(toks) > 2 and toks[0][2].lower() in ("gh", "gh.exe") and toks[1][2] in GH_TEXT_SUBS and toks[2][2] in GH_TEXT_ACTIONS:
        return 3, lambda w: w in GH_TEXT_FLAGS, tuple(f + "=" for f in sorted(GH_TEXT_FLAGS) if f.startswith("--"))
    return None


def strip_segment_message(seg):
    stages = split_pipes(seg)
    if len(stages) == 2 and safe_message_source(stages[0]):
        toks = scan_simple_tokens(stages[1])
        sub_idx = git_subcommand_index(toks)
        if sub_idx is not None and toks[sub_idx][2] in GIT_MESSAGE_SUBS and reads_stdin_message([t[2] for t in toks[sub_idx + 1:]]):
            return "_ |" + stages[1]
    toks = scan_simple_tokens(seg)
    found = message_options(toks)
    if found is None:
        return seg
    k, takes_text, prefixes = found
    replacements = []
    while k < len(toks):
        start, end, word = toks[k]
        if takes_text(word):
            if k + 1 < len(toks) and is_safe_literal_quote(toks[k + 1][2]):
                replacements.append((toks[k + 1][0], toks[k + 1][1]))
                k += 2
                continue
        else:
            for prefix in prefixes:
                if word.startswith(prefix) and is_safe_literal_quote(word[len(prefix):]):
                    replacements.append((start + len(prefix), end))
                    break
        k += 1
    parts = []
    pos = 0
    for s, e in replacements:
        parts.append(seg[pos:s])
        parts.append("_")
        pos = e
    parts.append(seg[pos:])
    return "".join(parts)


def strip_messages(command):
    lowered = command.lower()
    if "git" not in lowered and "gh" not in lowered:
        return command
    command = strip_git_heredocs(command)
    if len(command) > MAX_STRIPPED_CHARS:
        return command
    rebuilt = []
    for sep, seg in split_segments(command):
        if sep:
            rebuilt.append(sep)
        rebuilt.append(strip_segment_message(seg))
    return "".join(rebuilt)


def split_pipes(segment):
    stages = []
    start = 0
    quote = None
    i = 0
    n = len(segment)
    while i < n:
        ch = segment[i]
        if quote is not None:
            if quote == '"' and ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            i += 2
            continue
        end = here_string_end(segment, i)
        if end is not None:
            i = end
            continue
        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue
        if ch == "|":
            stages.append(segment[start:i])
            start = i + 1
        i += 1
    stages.append(segment[start:])
    return stages


def has_unquoted_construct(text, targets):
    quote = None
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if quote == "'":
            if ch == "'":
                quote = None
            i += 1
            continue
        if quote == '"':
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == '"':
                quote = None
                i += 1
                continue
            for t in targets:
                if t in ("$(", "`") and text.startswith(t, i):
                    return True
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            i += 2
            continue
        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue
        for t in targets:
            if text.startswith(t, i):
                return True
        i += 1
    return False


def is_read_only_stage(stage, is_pipe_sink):
    cleaned = STDERR_SAFE.sub(" ", stage).strip()
    if not cleaned:
        return False
    if has_unquoted_construct(cleaned, (">", "<", "$(", "`")):
        return False
    try:
        toks = shlex.split(cleaned, posix=True)
    except ValueError:
        return False
    if not toks:
        return False
    cmd = os.path.basename(toks[0]).lower()
    if not is_pipe_sink and len(toks) == 2 and toks[1].lower() in ("--version", "version", "--help"):
        return True
    if is_pipe_sink:
        if cmd not in READ_ONLY_PIPE_SINKS:
            return False
    else:
        if cmd in READ_ONLY_CMDS:
            pass
        elif cmd == "command":
            if len(toks) < 2 or toks[1] not in ("-v", "-V"):
                return False
        elif cmd in ("git", "git.exe"):
            i = 1
            while i < len(toks):
                w = toks[i]
                if w in ("-C", "-c") or w.lower() in GIT_GLOBAL_VALUE_FLAGS:
                    i += 2
                    continue
                if w.startswith("-"):
                    i += 1
                    continue
                break
            if i >= len(toks) or toks[i].lower() not in READ_ONLY_GIT_SUBS:
                return False
        elif PYTHON_CMD.match(cmd):
            i = 1
            module = None
            while i < len(toks):
                if toks[i] in PYTHON_SAFE_FLAGS:
                    i += 1
                elif toks[i] == "-m" and i + 1 < len(toks):
                    module = toks[i + 1]
                    i += 2
                else:
                    break
            if module == "json.tool":
                return i + 1 == len(toks)
            if i >= len(toks) or toks[i].startswith("-"):
                return False
            if os.path.basename(toks[i]).lower() != "test_guard.py":
                return False
        else:
            return False
    if cmd == "rg" and any(t == "--pre" or t.startswith("--pre=") for t in toks[1:]):
        return False
    if cmd == "less" and any(
        t == "--log-file" or t.startswith("--log-file=") or (t.startswith("-") and not t.startswith("--") and ("o" in t[1:] or "O" in t[1:]))
        for t in toks[1:]
    ):
        return False
    return True


def is_read_only_command(command):
    if not command or len(command) > MAX_PARSED_CHARS:
        return False
    if has_unquoted_construct(command, ("$(", "`", "<(", ">(")):
        return False
    segments = split_segments(command)
    has_any = False
    for _, seg in segments:
        if not seg.strip() or PURE_CD.match(seg.strip()):
            continue
        has_any = True
        stages = split_pipes(seg)
        for idx, stage in enumerate(stages):
            if not is_read_only_stage(stage, idx > 0):
                return False
    return has_any


def tokens(command):
    if len(command) > MAX_PARSED_CHARS:
        return command.split()[:MAX_WORDS]
    try:
        return shlex.split(command, posix=True)[:MAX_WORDS]
    except ValueError:
        return command.split()[:MAX_WORDS]


def patch_targets(args):
    for text in strings(args):
        if "*** Begin Patch" in text or "*** Add File:" in text or "*** Update File:" in text:
            for added, moved in PATCH_HEADER.findall(text):
                yield added or moved


def command_words(command):
    slashed = command.replace("\\", "/")
    shell = tokens(command) + (tokens(slashed) if slashed != command else [])
    whole = list(dict.fromkeys(w for w in shell + WORD_BREAK.split(ESCAPES.sub(" ", slashed))[:MAX_WORDS] if w))
    pieces = ESCAPES.sub(" ", command).split()[:MAX_WORDS]
    return list(dict.fromkeys(whole + pieces)), whole, shell


def resolve_cd_targets(cd_targets, current_bases):
    resolved = []
    for target in cd_targets:
        exp = expand(target)
        if os.path.isabs(exp) or not current_bases:
            resolved.append(exp)
        else:
            for base in current_bases:
                resolved.append(os.path.normpath(os.path.join(base, exp)) if base else exp)
    return with_real(list(dict.fromkeys(resolved))[:MAX_BASES])


def chain_cd_targets(cd_targets, bases):
    resolved = list(bases)
    for target in cd_targets:
        exp = expand(target)
        roots = [base for base in resolved if base]
        candidates = [exp] if os.path.isabs(exp) or not roots else [
            os.path.normpath(os.path.join(root, exp)) for root in roots[-MAX_BASES:]
        ]
        for candidate in candidates:
            if candidate not in resolved:
                resolved.append(candidate)
            if len(resolved) >= MAX_BASES:
                return with_real(list(dict.fromkeys(resolved))[:MAX_BASES])
    return with_real(list(dict.fromkeys(resolved))[:MAX_BASES])


def check_command(command, bases):
    if not command:
        return "allow"
    command = strip_messages(DIRENV.sub("direnv", command))
    words, whole, shell = command_words(command)
    cd_words = [m.strip("\"'") for m in CD.findall(command)]
    cd_bases = [expand(m) for m in cd_words]
    base_list = list(bases)
    base_set = set(base_list)
    all_bases = chain_cd_targets(cd_bases, base_list)
    first_pass = {}
    for word in words:
        found = path_forms(word, base_list)
        first_pass[word] = found
        if len(all_bases) < MAX_BASES and (names_secret_dir(found) or is_home(found)):
            all_bases.append(expand(word))
    all_bases = with_real(list(dict.fromkeys(all_bases))[:MAX_BASES])
    extra_bases = [b for b in all_bases if b not in base_set]
    word_forms = set()
    whole_forms = set()
    whole_set = set(whole)
    for word in words:
        found = first_pass[word]
        if extra_bases:
            found = found | path_forms(word, extra_bases)
        word_forms |= found
        if word in whole_set:
            whole_forms |= found
    forms = text_forms(command) | word_forms
    if names_secret(forms) and not EXISTENCE_ONLY.match(command):
        if not IGNORE_APPEND.match(command) and not ENV_FROM_EXAMPLE.match(command):
            return "deny"
    seg_bases = list(base_list)
    for sep, seg in split_segments(command):
        stripped = seg.strip()
        if not stripped:
            continue
        seg_cd_raw = [m.strip("\"'") for m in CD.findall(stripped)]
        is_pure_cd = bool(PURE_CD.match(stripped))
        if is_pure_cd and seg_cd_raw:
            next_bases = resolve_cd_targets(seg_cd_raw, seg_bases)
            if sep == "||":
                seg_bases = list(dict.fromkeys(seg_bases + next_bases))[:MAX_BASES]
            else:
                seg_bases = next_bases
            continue
        cur_bases = seg_bases
        if seg_cd_raw:
            next_bases = resolve_cd_targets(seg_cd_raw, seg_bases)
            cur_bases = list(dict.fromkeys(next_bases + seg_bases))[:MAX_BASES]
            if not stripped.startswith("("):
                seg_bases = cur_bases
        need_sweep = bool(SWEEPING.search(stripped))
        need_home = bool(HOME_SWEEPING.search(stripped))
        if need_sweep or need_home:
            _, seg_whole, seg_shell = command_words(stripped)
            sweep_bases = list(cur_bases)
            if need_sweep:
                for w in seg_whole:
                    if len(sweep_bases) >= MAX_BASES:
                        break
                    wf = path_forms(w, cur_bases)
                    if names_secret_dir(wf) or is_home(wf):
                        sweep_bases.append(expand(w))
                sweep_bases = with_real(list(dict.fromkeys(sweep_bases))[:MAX_BASES])
                if any(names_secret_dir(path_forms(w, sweep_bases)) for w in seg_whole):
                    return "deny"
            if need_home:
                skip = {form for word in seg_cd_raw for form in (word, word.replace("\\", "/"))}
                home_words = dict.fromkeys(word.strip(";&|()") for word in seg_shell)
                if any(word and word not in skip and covers_home(path_forms(word, cur_bases)) for word in home_words):
                    return "home"
    if names_protected(forms) and not is_read_only_command(command):
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
    paths = list(keyed(args, lambda k: is_path_key_for(name, k))) + list(file_urls(args))
    targets = list(patch_targets(args))
    for key in SEARCH_GLOB_KEYS.get(name, ()):
        if key in lowered:
            roots = [p for p in paths if p] or [cwd]
            for item in strings(lowered[key]):
                if item:
                    paths += [os.path.join(r, item) if r else item for r in roots]
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
        roots = [p for p in keyed(args, lambda k: is_path_key_for(name, k)) if p] or [cwd]
        if any(root and covers_home(path_forms(root, bases)) for root in roots):
            return "home"
    if name in MULTI_READ_TOOLS:
        if any(path and covers_home(path_forms(path, bases)) for path in paths):
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
        if fmt in ("agy", "gemini"):
            sys.stdout.write(json.dumps({"decision": "allow"}))
        sys.exit(0)
    reason = {"deny": REASON, "budget": BUDGET_REASON, "home": HOME_REASON}.get(decision, PROTECT_REASON)
    if fmt == "agy":
        sys.stdout.write(json.dumps({"decision": "force_ask" if decision == "ask" else "deny", "reason": reason}))
        sys.exit(0)
    if fmt == "gemini":
        sys.stdout.write(json.dumps({"decision": "deny", "reason": reason}))
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
    if fmt not in ("claude", "codex", "agy", "gemini"):
        sys.stderr.write("ai-global-config guard: usage: guard.py <claude|codex|agy|gemini>\n")
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
