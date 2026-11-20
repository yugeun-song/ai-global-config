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
