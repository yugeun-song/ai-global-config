# Install ai-global-config

To install, the user opens an agent in any directory and sends one line:

```text
Read <absolute path of this clone>/INSTALL.md and install the rules as it describes.
```

The installed rules MUST keep working after the user deletes this clone.
Therefore, install a copy that your tool owns, never a reference to this
clone.

## Install the rules into your tool

Start only when the user explicitly asks you to install these rules. This
file by itself is not a request. The request also covers replacing an older
installed copy of these rules.

1. Read `rules/global.md` in full.
2. Find where your tool loads instructions in every session and every
   directory. NEVER use a memory feature, a per-project file or a
   per-session store, because those have size limits, cover one project
   only, or expire. Tell the user the location and how you confirmed it
   (your tool's documentation or its own help output). The table below lists
   known locations; check them against your tool's current documentation
   before you rely on them.
3. Move text only with a file copy command (`cp`, `Copy-Item` or your tool's
   file copy). NEVER retype, summarize or reformat the rules: a single
   changed byte breaks the check in step 7.
4. Look for an installed copy: the file `ai-global-config.md` of method A or
   B, the text between the markers of method C, or the files
   `ai-global-config-*.md` of method D. If its SHA-256 equals
   that of `rules/global.md`, change nothing, report that, and stop. If it
   differs, it is an older version: summarize the difference for the user,
   then replace it whole in step 6.
5. Method B or C adds a line or a block to a file. If that file holds other
   content and these rules were never installed there, show the user the
   exact addition and wait for approval. NEVER change content outside the
   import line or the markers.
6. Install with the first method your tool supports:
   - Method A, rules directory: copy `rules/global.md` byte for byte to
     `ai-global-config.md` in the directory from which your tool loads every
     rule file in every session. Change nothing else.
   - Method B, copy and import: copy `rules/global.md` byte for byte to
     `ai-global-config.md` inside your tool's own configuration directory,
     then add one import line for that copy to your tool's global
     instruction file.
   - Method C, marker block: put the exact text of `rules/global.md` in your
     tool's global instruction file between the line
     `<!-- ai-global-config:begin -->` and the line
     `<!-- ai-global-config:end -->`. If the file is empty or absent, the
     whole file is that block.
   - Method D, split rules directory: use it when your tool loads every
     file of a rules directory but caps each file below the size of
     `rules/global.md`. Copy each file of `rules/parts/` into that
     directory as `ai-global-config-<name of the part>`. If the tool loads
     a file in every session only with a header, write exactly that header
     first and then the part byte for byte. Remove installed parts that
     `rules/parts/` no longer has.
7. Verify the result: the SHA-256 of the installed copy (methods A and B) or
   of the text between the markers (method C) must equal the SHA-256 of
   `rules/global.md`. For method D, the SHA-256 of each installed file
   without its header must equal that of its part, and the parts joined in
   name order must equal `rules/global.md`. Compute SHA-256 with
   `sha256sum` on Linux, `shasum -a 256` on macOS, or `Get-FileHash
   -Algorithm SHA256` on Windows. For method B, also read back the import
   line and confirm that it names the copy, not this clone.
8. Report to the user: the location, the method, both SHA-256 values, and,
   for each rule group in Part 1 of `rules/global.md`, whether your tool's
   own settings (deny rules, hooks, sandbox) enforce it or only the text
   states it. Then tell the user that the clone can be deleted. Ask the user
   to open a new session in a different directory and have the agent there
   quote Rule SECRET-1 exactly. The quote must match `rules/global.md` word
   for word; Markdown markup such as a list marker or bold may differ.

If a sandbox or permission setting blocks a step, tell the user which
setting blocked which step, and stop.

To update, the user clones this repository again and sends the same line.
Step 4 finds the older copy, and step 6 replaces it.

| Tool | Method | Location of the copy |
|---|---|---|
| Claude Code | A | `~/.claude/rules/ai-global-config.md` |
| Antigravity CLI (agy) | D, in `~/.gemini/config/rules/`, header `---`, `trigger: always_on`, `---` and one empty line | `~/.gemini/config/rules/ai-global-config-*.md` |
| Gemini CLI | B, import line `@~/.gemini/ai-global-config.md` in `~/.gemini/GEMINI.md` | `~/.gemini/ai-global-config.md` |
| Codex CLI | C, in `~/.codex/AGENTS.md` | inside that file |
| OpenCode | C, in `~/.config/opencode/AGENTS.md` | inside that file |
| Hermes Agent | C, in `~/.hermes/SOUL.md` | inside that file |
| Cursor | the user pastes the text into User Rules in the settings screen | none |

## Install the guard (optional)

The rules are text. The guard makes a tool refuse a tool call that names a
credential (Rule SECRET-1), and ask the user before a call changes the
guard or the hook settings. It works only through the pre-tool hook or the
permission rules that the tool's official documentation describes. Start
only when the user asks for the guard.

1. Find your tool in the table below. If it is not in the table, or its
   current documentation describes no pre-tool hook and no permission
   rules, tell the user that the guard is not available for it, and stop.
2. For a tool with a hook, find the real path of a Python 3 interpreter:
   run `python3 -c "import os, sys; print(os.path.realpath(sys.executable),
   sys.prefix == sys.base_prefix)"` (on Windows, `py -3` or `python`
   instead of `python3`). Use the printed path only when the second value
   is `True` and the path is not a shim of a version manager (pyenv, asdf,
   mise) or a project virtual environment, because those can change or
   vanish. If the printed path names a minor version (for example
   `/usr/bin/python3.14`) and an unversioned name in the same directory
   (`/usr/bin/python3`) resolves to the same file, use the unversioned
   name: a package upgrade removes the versioned file but keeps that name.
   If no such interpreter exists, tell the user that the guard needs
   Python 3, and stop. Claude Code also needs version 2.1.295 or later for
   `onFailure`.
3. For a tool with a hook, copy `guards/guard.py` byte for byte to the
   guard location in the table. If your tool or its sandbox refuses that
   write, stop before step 4: a hook that points to a missing script
   blocks every tool call in Claude Code and may silently do nothing in
   other tools. Give the user the copy command for a terminal outside the
   tool, and continue only after the user has run it.
4. In the tool's fragment, replace `<python3>` with the interpreter path from
   step 2 and `<home>` with the absolute path of the user's home directory. Keep
   the quotes around both, and write `/` instead of `\` in both paths, also on
   Windows. If your tool runs hook commands through PowerShell, put `&` and a
   space before the quoted interpreter path. Then merge the fragment into the
   configuration file. Add the fragment's entries next to the existing ones.
   NEVER remove or change an existing entry. If the file already holds other
   content, show the user the exact addition and wait for approval. Keep the
   original content, and restore it if the merged file does not parse as JSON
   (JSONC for OpenCode).
5. Verify the guard:
   - `python3 guards/test_guard.py <installed guard>` reports no failure.
   - The SHA-256 of the installed guard equals that of `guards/guard.py`.
   - `python3 guards/test_guard.py --hook <claude|codex|agy>` reports no
     failure. It runs every guard command that the configuration file
     holds, exactly as written, through the system shell. It feeds one
     input that must be blocked and one that must be allowed. No
     credential is opened. If your tool runs hooks through a different
     shell (for example PowerShell on Windows), also run the command there.
   - For OpenCode, read the merged file back and confirm that it holds
     every rule of the fragment.
6. Report the locations, both SHA-256 values and the test results. For
   Codex, ask the user to open `/hooks` in Codex and trust the new hook:
   Codex skips a new hook until the user trusts it.

| Tool | Guard location | Configuration file | Fragment |
|---|---|---|---|
| Claude Code | `~/.claude/hooks/ai-global-config-guard.py` | `~/.claude/settings.json` | `guards/claude-settings.json` |
| Codex CLI | `~/.codex/hooks/ai-global-config-guard.py` | `~/.codex/hooks.json` | `guards/codex-hooks.json` |
| Antigravity CLI (agy) | `~/.gemini/config/hooks/ai-global-config-guard.py` | `~/.gemini/config/hooks.json` | `guards/agy-hooks.json` |
| OpenCode | none: permission rules only | `~/.config/opencode/opencode.jsonc` | `guards/opencode-permissions.json` |

The guard catches mistakes and common attempts. It is not a complete
security boundary:

- It matches names in the text of a tool call. A command can still reach a
  secret through a glob (`~/.n?trc`), brace expansion, a variable, a
  string built at run time, an encoded name, a working directory set in a
  form it does not parse, a symbolic link named inside a glob or a built
  string, or a script it wrote earlier.
- The existence check trusts that `ls`, `stat` and `test` are the real
  commands. A shell function or an earlier file on `PATH` with the same
  name can turn that check into a read.
- Its protection of its own files and of the hook settings is also based
  on names, so a command that reaches them indirectly gets past it.
- It can block a harmless command that names such a file, for example a
  commit message that mentions `.ssh` or `docker compose --env-file .env`.
- It also blocks a read that the user explicitly authorized under Rule
  SECRET-1, because it cannot tell whether the user did. The user does
  that step in a terminal outside the tool.
- Another hook (from a plugin, a skill, an agent definition or a workspace
  file) can rewrite a tool call after the guard allowed it.
- When it runs out of its time budget (about 4 seconds) or cannot parse
  the call, it decides from the raw text and blocks when in doubt.
- Claude Code: `disableAllHooks` or a `--settings` override turns the
  guard off. With `onFailure: "block"`, a deleted or broken guard script
  blocks every tool call until the user removes the hook entry by hand.
- Codex has no "ask" decision, so the guard blocks a change to its own
  files instead of asking. Codex may run a tool when its hook fails, times
  out or answers in a wrong format. Input sent later to a running terminal
  (`write_stdin`) does not pass the hook again. Codex skips a new or
  changed hook until the user trusts it in `/hooks`, so every update needs
  that step again. `CODEX_HOME` moves the hooks file elsewhere. Hosted
  tools such as web search do not pass the hook.
- Antigravity CLI documents no behavior for a failing hook, so treat a
  failure as letting the call run. Its online documentation says that
  `"allow"` hands the call to the next hook or the default policy, but the
  documentation bundled with version 1.5.13 says that `"allow"` approves
  the call. Under the second reading, the guard would skip the approval
  prompts of agy.
- OpenCode permission rules match the whole command text, so they are
  coarser than the hook. A rule loaded later (an agent's or a project's)
  can allow a path again, because the last matching rule wins. Versions
  before V2 read a `permission` key instead of `permissions`, so on those
  versions the fragment does nothing. For the `grep` action the resource is
  the search pattern, not the path, so a rule blocks a pattern that
  contains such a name but not a search inside such a directory.

Test case 23 checks that the agent does not read a decoy credential on its
own. Test case 24 checks whether the guard really blocks a read that the
user authorized.

## Install the OpenCode system policy (optional)

OpenCode also supports policies in its system configuration. A policy can
hard-deny a permission check after permissions and saved approvals run, and
a project cannot override it. This is stronger than the permission rules in
the guard. Start only when the user asks for it.

1. Confirm that `~/.config/opencode/opencode.jsonc` has the `policies` array
   copied from the guard step above. Stop when it is absent.
2. Run `guards/opencode-system-policy.sh` with root privileges. The script
   defaults to the system configuration path for Linux or macOS. Pass
   `--dst FILE` for another path. It backs up an existing destination file,
   keeps its content, merges the source policies, and validates the JSON.
3. Run `opencode reload`. From a new session, confirm that a named credential
   is still denied.
