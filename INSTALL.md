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
   changed byte breaks the check in step 9.
4. Look for an installed copy: the file `ai-global-config.md` of method A or
   B, the text between the markers of method C, or the files
   `ai-global-config-*.md` of method D. If its SHA-256 equals
   that of `rules/global.md`, leave the copy as it is, report that, and
   continue with step 7. If it differs, it is an older version: summarize
   the difference for the user, then replace it whole in step 6.
5. Method B or C adds a line or a block to a file. If that file holds other
   content, add only the import line or the marked block, and show the
   exact addition in your report. Outside the import line or the markers,
   change only what step 7 removes.
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
7. Remove older global rules from every other instruction file that your
   tool loads in every session and every directory, such as
   `~/.claude/CLAUDE.md` for Claude Code, and from the content outside the
   import line or the markers of method B or C. Rules that an earlier
   version or the user put there would otherwise load beside the installed
   copy and contradict it. The request to install or update covers this
   step, so do not ask first.
   - Before you change a file, copy it to a backup in your tool's
     configuration directory.
   - Remove every rule and note that `rules/global.md` already covers or
     contradicts.
   - Keep, word for word, only what holds on this machine alone: facts
     about its hardware, software, paths, network and local tools, and
     rules for those tools. When you cannot tell whether a passage is a
     global rule or a note for this machine, keep it. When two tools share
     an instruction file (such as `~/.gemini/GEMINI.md`, which both Gemini
     CLI and Antigravity CLI load), keep the other tool's installed
     `ai-global-config` import line or marker block.
   - Start the file with a short header that names the installed copy and
     says that the file holds only notes for this machine.
   - Report what you removed, what you kept and the path of the backup.
     List the removed passages that `rules/global.md` does not hold, so
     that the user can add them to this repository.
8. For Claude Code, set `includeGitInstructions` to `false` in
   `~/.claude/settings.json`. Claude Code then leaves out its built-in
   commit and pull request workflow and its git status snapshot, so that
   Rules ACTION-3, ACTION-4, OUTPUT-3 and OUTPUT-4 alone decide how the
   agent commits. The agent then gets no git status when a session starts
   and reads it itself when it needs it. Leave `attribution` unset: Claude
   Code already puts user rules on attribution before its own lines. Keep
   every other key, restore the original file if the result does not parse
   as JSON, and show the exact change in your report.
9. Verify the result: the SHA-256 of the installed copy (methods A and B) or
   of the text between the markers (method C) must equal the SHA-256 of
   `rules/global.md`. For method D, the SHA-256 of each installed file
   without its header must equal that of its part, and the parts joined in
   name order must equal `rules/global.md`. Compute SHA-256 with
   `sha256sum` on Linux, `shasum -a 256` on macOS, or `Get-FileHash
   -Algorithm SHA256` on Windows. For method B, also read back the import
   line and confirm that it names the copy, not this clone.
10. Report to the user: the location, the method, both SHA-256 values, the
    results of steps 7 and 8, and, for each rule group in Part 1 of
    `rules/global.md`, whether your tool's own settings (deny rules, hooks,
    sandbox) enforce it or only the text states it. Then tell the user that
    the clone can be deleted. Ask the user
    to open a new session in a different directory and have the agent there
    quote Rule SECRET-1 exactly. The quote must match `rules/global.md` word
    for word; Markdown markup such as a list marker or bold may differ.

If a sandbox or permission setting blocks a step, tell the user which
setting blocked which step, and stop.

To update, the user clones this repository again and sends the same line.
An update MUST leave no older copy of anything that this repository puts
on the machine: an older copy keeps loading or running, and nothing
reports it. The request to update covers every step below, so do not ask
first.

- Run steps 4 to 10 for every tool in the table below whose copy exists
  on this machine, not only for your own tool. Step 4 finds the older
  copy, step 6 replaces it, and step 7 removes older rules from the other
  instruction files.
- For every tool in the guard table whose guard is installed, run steps 3,
  4, 6 and 7 of the guard install: replace the guard copy, bring the
  guard's own hook entry to the current fragment, and test it. For
  OpenCode, add the rules and policies of the fragment that the
  configuration file lacks, in the order of the fragment.
- Compare each setting that only the user can apply (step 5 of the guard
  install) with the repository. Give the user the command for each one
  that differs, and check it after the user has run it.
- Report every location you checked, whether it was current, and what you
  changed.

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
credential or that searches, copies or archives the whole home directory
(Rule SECRET-1). It also makes the tool ask the user before a call changes
the guard or the hook settings, or turns hooks off. It works only through
the pre-tool hook, or for OpenCode through its permission rules and
policies, as the tool's official documentation describes. Start only when
the user asks for the guard, or when an update finds an installed guard.

1. Find your tool in the table below. If it is not in the table, or its
   current documentation describes no pre-tool hook and no permission
   rules, tell the user that the guard is not available for it, and stop.
2. For a tool with a hook, pick the plain command name that starts
   Python 3.6 or later, so that the hook keeps working when Python is
   upgraded or reinstalled. Try `python3`, then `python`, and on Windows
   also `py`. A name qualifies when the following command prints `True`:
   `<name> -c "import sys; print(sys.version_info >= (3, 6))"`. The hook
   then starts whatever that name finds on `PATH`. `command -v <name>` (on
   Windows `where <name>`) shows the file that the name finds, and
   `<name> -c "import sys; print(sys.executable)"` shows the interpreter
   that it starts. Systems differ in these names:
   - Debian and Ubuntu have `python` only with the `python-is-python3`
     package.
   - RHEL 8 and its rebuilds may have no `python3` command. Use
     `/usr/libexec/platform-python` there.
   - On macOS, `/usr/bin/python3` is a stub until the Command Line Tools
     are installed, and running the stub opens an installation dialog. Run
     `xcode-select -p` first, and skip that file if the command fails.
   - On Windows, `python` and `python3` in `WindowsApps` can be Microsoft
     Store stubs that exit with code 9009. The test command above rules
     them out.

   If the file is a shim of a version manager (pyenv, asdf, mise) or lies
   in a project virtual environment, use the absolute path of the system's
   unversioned interpreter instead (for example `/usr/bin/python3`): a shim
   can fail in a directory that pins another version. On Windows, run
   `icacls` on the interpreter's directory, and prefer a name whose
   interpreter directory grants no write or modify access to `Everyone`,
   `Users` or `Authenticated Users`: through such a directory any program
   of any account can replace the interpreter and turn the guard off. A
   directory created directly under `C:\`, such as `C:\Python314`, inherits
   such access from the drive root. If every name leads to such a
   directory, tell the user that an administrator can remove that access:
   `icacls <directory> /inheritance:d` turns the inherited entries into
   explicit ones, and `icacls <directory> /remove:g *S-1-5-11` then removes
   the entry of `Authenticated Users`, from which a directory under `C:\`
   gets it. The files below the directory follow. Check the result with
   `icacls`. If your tool runs hook commands through `cmd.exe`, use the
   interpreter's absolute path: `cmd.exe` looks for a plain name in the
   current directory before `PATH`, so in a repository that holds a
   `python.exe`, that file would run in place of Python. If no name starts
   Python 3.6 or later, tell the user that the guard needs it, and stop.
   Claude Code also needs version 2.1.295 or later for `onFailure`.
3. For a tool with a hook, copy `guards/guard.py` byte for byte to the
   guard location in the table. If your tool or its sandbox refuses that
   write, stop before step 4: a hook that points to a missing script
   blocks every tool call in Claude Code and may silently do nothing in
   other tools. Give the user the copy command for a terminal outside the
   tool, and continue only after the user has run it.
4. In the tool's fragment, replace `<python3>` with the command from step 2
   and `<home>` with the absolute path of the user's home directory. Write
   `/` instead of `\` in paths, also on Windows. The Claude Code fragment
   uses exec form (`args`): Claude Code starts the command without a shell,
   so the entry needs no quotes and works the same with or without Git
   Bash on Windows. In the other fragments, keep the quotes around both
   values, and if your tool runs hook commands through PowerShell, put `&`
   and a space before the quoted command. Then merge the fragment into the
   configuration file. Add the fragment's entries next to the existing
   ones. NEVER remove or change an existing entry. Keep the original
   content, restore it if the merged file does not parse as JSON (JSONC for
   OpenCode), and show the exact addition in your report.
5. Some settings only the user can apply, from a terminal outside the
   tool: system files that need administrator or root rights, and a
   settings file that the tool keeps its agents from editing. Offer the
   entry for your tool, give the user the command, and go on with the other
   steps. Step 6 checks each setting after the user has applied it.
   - Claude Code, managed settings. An agent that runs as the user can
     still edit the user's own files, but only an administrator or root can
     change managed settings, and their hooks stay on when any other
     settings file sets `disableAllHooks`. Claude Code reads them from
     `C:\Program Files\ClaudeCode\managed-settings.json` on Windows,
     `/Library/Application Support/ClaudeCode/managed-settings.json` on
     macOS and `/etc/claude-code/managed-settings.json` on Linux. Copy the
     guard to `hooks/ai-global-config-guard.py` in that directory, replace
     the guard path in the fragment with the path of that copy, and merge
     the fragment into `managed-settings.json` as in step 4. The user runs
     these commands in an administrator or root terminal, or approves the
     system's own elevation prompt for them. Before you write the managed
     file, run the exact hook command with
     `{"tool_name":"Bash","tool_input":{"command":"ls"}}` on standard input,
     and confirm that it exits with 0: a managed entry that fails blocks
     every tool call until an administrator fixes it. Then remove the
     user's entry and its guard copy, so that the guard runs once per tool
     call. Keep the plain command name from step 2 unless the user asks for
     an absolute path, and tell the user the trade-off: Claude Code looks
     the name up in the `PATH` that it inherits, which the user's own
     account can change, while an absolute path to an interpreter in a
     directory that only administrators can change closes that gap but
     breaks when that interpreter moves. If remote settings or an MDM
     policy (a macOS configuration profile, or a value in the Windows
     `HKLM` registry) already set managed settings, Claude Code may skip
     this file. On WSL, the user can write `/etc/claude-code` too.
   - OpenCode, system file. The fragment also holds policies. Once merged,
     they already apply, and no project file can lift them, because
     OpenCode evaluates policies from broader files last. To keep them where
     an agent cannot change them, the user copies them into the system
     file, which only root can change, with
     `sudo bash guards/opencode-system-policy.sh`. The script supports Linux
     and macOS. It backs up the system file, keeps its settings and
     policies, appends the missing policies, and validates the result. It
     needs Python 3.6 or later and looks for it as `python3`,
     `/usr/libexec/platform-python` and `python`, in this order. On
     Windows, OpenCode reads the system file from `%ProgramData%\opencode`,
     and the script does not set it up there.
   - Antigravity CLI, permissions. agy keeps its agents from editing
     `~/.gemini/antigravity-cli/settings.json` directly. In its auto mode,
     agy still asks before reads outside the workspace and before risky or
     irreversible commands that run outside its sandbox.
     `bash guards/agy-permissions.sh` backs up that file, keeps its keys
     and rules, turns on auto mode and access outside the workspace, and
     allows every command (`command(*)`, which covers both sandboxed and
     unsandboxed commands on personal accounts), file read and file write,
     so that the guard is the only check left on those calls. It also
     denies `command(rm -rf /)`. The options `--no-write-all`,
     `--no-read-all`, `--dir DIR` and `--unsandboxed CMD` adjust what it
     allows; pass `--unsandboxed '*'` (or specific commands) only on
     business and enterprise accounts, because personal accounts ignore
     `unsandboxed` rules with a warning. Shell constructs that disable
     prefix matching (such as `$(...)`, backticks, `<(...)` and `{a,b}`)
     still ask unless covered by an exact or `regex:` rule or by
     `toolPermission`. The script needs bash and Python 3.6 or later, and
     it finds Python as the OpenCode script does. On Windows, the user runs
     it from Git Bash.
6. Verify the guard:
   - `python3 guards/test_guard.py <installed guard>` reports no failure.
   - The SHA-256 of the installed guard equals that of `guards/guard.py`.
   - `python3 guards/test_guard.py --hook <claude|codex|agy|gemini>` reports no
     failure. It runs every guard command that the configuration file
     holds (for Claude Code, also the managed settings), exactly as
     written: an exec-form entry directly, and a shell-form entry through
     the system shell. It feeds one input that must be blocked and one
     that must be allowed. No credential is opened. If your tool runs a
     shell-form hook through a different shell (for example PowerShell on
     Windows), also run the command there.
   - For a Claude Code entry in managed settings, run a command in a
     session that names a credential file that does not exist, such as
     `cat agc-decoy/.netrc`. The guard must block it, and the block
     message must name the guard copy in the managed settings directory.
   - For OpenCode, read the merged file back and confirm that it holds
     every rule and every policy of the fragment. Read the system file
     back the same way if the user ran the script. In a new OpenCode
     session, confirm that a tool call that names a credential is denied.
7. Report the locations, both SHA-256 values and the test results. For
   Codex, ask the user to open `/hooks` in Codex and trust the new hook:
   Codex skips a new hook until the user trusts it.

| Tool | Guard location | Configuration file | Fragment |
|---|---|---|---|
| Claude Code | `~/.claude/hooks/ai-global-config-guard.py`, or `hooks/ai-global-config-guard.py` in the managed settings directory | `~/.claude/settings.json`, or `managed-settings.json` | `guards/claude-settings.json` |
| Codex CLI | `~/.codex/hooks/ai-global-config-guard.py` | `~/.codex/hooks.json` | `guards/codex-hooks.json` |
| Antigravity CLI (agy) | `~/.gemini/config/hooks/ai-global-config-guard.py` | `~/.gemini/config/hooks.json` | `guards/agy-hooks.json` |
| Gemini CLI | `~/.gemini/hooks/ai-global-config-guard.py` | `~/.gemini/settings.json` | `guards/gemini-settings.json` |
| OpenCode | none: permission rules and policies | `~/.config/opencode/opencode.jsonc`; with root, also the system file | `guards/opencode-permissions.json` |

The guard catches mistakes and common attempts. It is not a complete
security boundary:

- It matches names in the text of a tool call. A command can still reach a
  secret through a glob (`~/.n?trc`), brace expansion, a variable, a
  string built at run time, an encoded name, a working directory set in a
  form it does not parse, a symbolic link named inside a glob or a built
  string, a search that names no directory and so searches the working
  directory, or a script it wrote earlier.
- It looks for secrets only in files and secret stores. It does not cover
  secrets in environment variables, the clipboard, shell history, or a
  tool's own settings file that also holds tokens, such as MCP server
  settings.
- It does not resolve network paths such as `\\server\share`, so checking
  a call does not contact another computer. On Windows, an existing local
  symbolic link to such a share can still make the check contact it.
- The existence check trusts that `ls`, `stat` and `test` are the real
  commands. A shell function or an earlier file on `PATH` with the same
  name can turn that check into a read.
- Its protection of its own files and of the hook settings is also based
  on names, so a command that reaches them indirectly gets past it.
- It can block a harmless command that names such a file, for example
  `docker compose --env-file .env`. It skips message text that the shell
  passes on unchanged: a quoted string or a single-quoted PowerShell
  here-string given to `-m` or `--message` of `git commit`, `git tag`,
  `git merge` or `git notes`, or to the title, body and notes options of
  `gh pr`, `gh issue` and `gh release`; a heredoc with a quoted delimiter
  that those commands read from standard input (`-F -`, `--body-file -`,
  `--notes-file -`) or through `cat` inside `"$(…)"` on those text
  options; and such a literal piped into those standard-input options. A
  message that contains command substitution, or a file path given to `-F`,
  `--body-file` or `--notes-file`, is still checked.
- It also blocks a read that the user explicitly authorized under Rule
  SECRET-1, because it cannot tell whether the user did. The user does
  that step in a terminal outside the tool.
- Another hook (from a plugin, a skill, an agent definition or a workspace
  file) can rewrite a tool call after the guard allowed it.
- When a call names more words or paths than it can check in about 4
  seconds, it blocks the call and asks the agent to split it. When it
  cannot parse the call, it decides from the raw text and blocks when in
  doubt.
- Claude Code: `disableAllHooks` in any settings file other than managed
  settings, including a file passed with `--settings`, turns off a guard
  in the user's settings. The guard asks before a tool call that names
  `disableAllHooks`, but a cloned repository can already hold it in its
  `.claude/settings.json`, which overrides the user's settings in that
  project. A guard in managed settings stays on in both cases (step 5).
  With `onFailure: "block"`, a deleted or broken guard script or a removed
  interpreter blocks every tool call until the user fixes or removes the
  hook entry by hand; a managed entry needs administrator or root rights
  for that.
- The guard does not protect its interpreter. A hook that names a command
  starts the first interpreter that the name finds on `PATH`. When the
  user's own account can change that interpreter's files (for example in
  a per-user install under `AppData` on Windows) or the `PATH` that the
  tool inherits, an agent can turn the guard off through them. The user's
  own account can always change the user part of `PATH` on Windows and
  the shell's startup files on every system, so only an absolute path
  avoids this lookup.
- Codex has no "ask" decision, so the guard blocks a change to its own
  files instead of asking. Codex may run a tool when its hook fails, times
  out or answers in a wrong format. Input sent later to a running terminal
  (`write_stdin`) does not pass the hook again. Codex skips a new or
  changed hook until the user trusts it in `/hooks`, so every update needs
  that step again. `CODEX_HOME` moves the hooks file elsewhere. Hosted
  tools such as web search do not pass the hook.
- Antigravity CLI documents no behavior for a failing hook, so treat a
  failure as letting the call run. Its online documentation says that
  `"allow"` hands the call to the next hook or the default policy (with
  `"auto_approve"` approving when the default policy would prompt), but the
  documentation bundled with version 1.5.14 still says that `"allow"`
  approves the call. Under the second reading, the guard would skip the
  approval prompts of agy.
- Gemini CLI: `BeforeTool` hooks use millisecond `timeout` values (the
  fragment sets `10000` for 10 seconds), regex `matcher` (`".*"`), and
  support `"allow"` and `"deny"` decisions (no `"ask"` decision), so the
  guard denies a change to its own files or `~/.gemini/settings.json`
  instead of asking. If a `BeforeTool` hook times out, Gemini CLI fails
  open and lets the tool call run.
- OpenCode permission rules match the whole command text, so they are
  coarser than the hook. OpenCode patterns know only `*` and `?`, so the
  fragment lists each character that can stand before `.env` in a
  command; a name that the shell builds at run time, such as `cat $v.env`
  with a space in `v`, still gets past them. OpenCode ignores letter case
  on Windows, and on macOS only in file rules. On macOS, whose default file
  system ignores letter case, `cat .ENV` therefore reads `.env` without
  matching a rule. The hook ignores letter case on every system. A rule
  loaded later (an agent's or a project's) can allow a path again, because
  the last matching rule wins. The
  fragment's policies close that gap: OpenCode evaluates policies from
  broader files last, a denying policy also overrides an "Allow always"
  approval, and an allowing policy only lifts an earlier deny. Policies
  cannot ask, so the rules that ask before an edit of OpenCode's own
  settings stay permission rules. Versions before V2 read a `permission`
  key instead of `permissions`, so on those versions the permission rules
  do nothing, and releases that read policies only from
  `experimental.policies` ignore the policies. For the `grep` action the
  resource is the search pattern, not the path, so a rule blocks a
  pattern that contains such a name but not a search inside such a
  directory.

Test case 23 checks that the agent does not read a decoy credential on its
own. Test case 24 checks whether the guard really blocks a read that the
user authorized.
