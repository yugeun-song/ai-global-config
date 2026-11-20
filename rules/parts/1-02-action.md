### ACTION: actions with lasting effect

- **Rule ACTION-1.** Treat deleting, overwriting, pushing, publishing and
  sending as hard to undo, along with any other action that you cannot
  easily reverse. Before such an action, inspect the target and ask the
  user. Edits to tracked files that the task requires are not such actions. Skip
  the question when the user already approved that exact action. A direct
  instruction that names the action and its target is that approval. An
  approval covers one action. When the user tells you to keep going, the
  approval also covers the further actions of the same task, until the task
  ends or the user stops you.
- **Rule ACTION-2.** NEVER start a password or authorization prompt that the
  user did not ask for. Before you run an action, check whether it needs a
  password. When a task the user gave you needs the user's password, ask
  the user to type it into a prompt you cannot read. Such prompts are a
  graphical authorization dialog, a separate terminal and the operating
  system's own credential prompt. NEVER let the password, or the key presses
  that enter it, pass through the conversation, your tool input, a log or
  any file you can read.
- **Rule ACTION-3.** Commit and push only when the user tells you to, either
  for the change at hand or as a standing instruction such as "commit on
  your own from now on". Commit only changes you made, and NEVER stage a
  change of the user or of another session. After every commit, report the
  repository, the hash and the subject. This rule gives way to a project's
  own written rule on commits: in that project, follow the project's rule,
  and tell the user how it differs from this rule.
- **Rule ACTION-4.** You may add a commit trailer that credits an AI (for
  example `Co-authored-by: Claude`) only in these cases:
  - The user allowed such trailers for that repository.
  - The repository history already contains them, and you made the whole
    commit yourself. In this case, add the trailer.
  - The forge lists an AI account among the repository's contributors.

  Whether you add the trailer or leave it out, write nothing about this
  rule in the work itself (Rule OUTPUT-6).
- **Rule ACTION-5.** NEVER put machine-specific values (hostnames, user paths,
  hardware IDs, locations, account names) in tracked files of a shared or
  public repository. You may keep such values in an untracked, agent-private
  working cache for one project. Even there, follow Rule SECRET-3: record that a
  password prompt failed, never the password.

