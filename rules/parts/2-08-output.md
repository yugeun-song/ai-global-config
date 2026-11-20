### OUTPUT: code and repository output

- **Rule OUTPUT-1.** Choose the language of code, comments, documentation,
  logs, CLI output, identifiers and commit messages in this order: the
  user's explicit instruction, the language the project already uses,
  English. Use emoji only when the user asks. Keep functional glyphs (an
  input-state marker, keymap jamo): they are data.
- **Rule OUTPUT-2.** Add comments only on request. Keep documentation and
  READMEs short and current, written as Rule WRITING asks.
- **Rule OUTPUT-3.** Follow the repository's conventions: message format,
  commit size, branching, sign-off and the rest. Without a convention, put
  one coherent change in each commit and write a lowercase imperative English
  subject of one or two short lines. Batch related work. NEVER commit
  automatically after each instruction.
- **Rule OUTPUT-4.** After you create a commit or pull request, read its message
  or body. If it contains an AI credit line that Rule ACTION-4 does not allow,
  remove the line without comment.
- **Rule OUTPUT-5.** Edit structured formats (JSON, TOML, YAML) with a parser,
  not with regular expressions.
- **Rule OUTPUT-6.** Work products show the result, not the instructions
  behind it. NEVER copy the user's instruction, a rule of this file or a
  remark about following either into a commit message, code, a comment, a
  document or a pull request, unless the user explicitly asks for that
  text there. For example, after you leave out an AI trailer, do not write
  "trailer omitted as instructed"; after the user asks for shorter code, do
  not comment "shortened per request".

