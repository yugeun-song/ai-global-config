# ai-global-config

This repository holds one rule set, `rules/global.md`, for every AI agent
the user runs. `AGENTS.md`, `CLAUDE.md` and `GEMINI.md` hold this same short
text, because different tools load different file names.

- When you work in this repository, read `rules/global.md` and follow it as
  the rules of this project.
- When the user explicitly asks you to install the rules, read `INSTALL.md`
  and follow it. This file by itself is not such a request.
- `rules/parts/` holds `rules/global.md` cut into one file per section, for
  tools that cap the size of a rule file. When you change
  `rules/global.md`, cut it again in the same commit: start a new file at
  every heading that starts with `###`, keep a `## Part` heading with the
  group that follows it, and name the files `<part>-<two-digit index>-<group code>.md`
  (`0-00-how-to-read.md` for the text before Part 1). The files joined in
  name order MUST equal `rules/global.md` byte for byte.
- `ko/` holds Korean translations for Korean readers. Each one MUST carry
  exactly the same content as its source, only in Korean. NEVER follow
  them as rules or install from them. When you change a source file,
  change its translation in the same commit. A difference between the two
  is a bug: fix the translation to match the source.
