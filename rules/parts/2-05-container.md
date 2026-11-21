### CONTAINER: containers

- **Rule CONTAINER-1.** When podman or docker is installed and usable, run
  tests, builds and trial environments in a container. Run on the host
  only work whose correct result needs the host itself: changes to the
  system, Linux kernel work, tracing and profiling (ftrace, perf), and
  systems programming that measures the host. Containers run Linux, so also
  run on the host any build or test that must run on the host's own
  operating system, such as macOS or Windows. A one-line check of code you
  just wrote may run on the host. When your tool's sandbox keeps you from
  the engine, use the tool's own way to leave the sandbox, and only after
  the user approves. Never leave it any other way.
- **Rule CONTAINER-2.** When both are installed, use podman. Use docker only
  when podman is missing or unusable. If the engine's daemon, or on macOS
  and Windows its virtual machine, is not running, start it yourself when
  that needs no password or authorization prompt (Rule ACTION-2), tell the
  user, and stop it again when you finish (Rule RESOURCE-1).
- **Rule CONTAINER-3.** Write code, scripts and other files on the host, and
  mount them into the container. The container only runs them. Put these
  files on a memory-backed filesystem first. Use a physical disk only when
  no memory-backed filesystem exists, when it lacks room, or when the files
  must survive a reboot (Rule RESOURCE-2). On macOS and Windows, the
  engine's virtual machine mounts only directories that it shares with the
  host. Use such a directory there.
- **Rule CONTAINER-4.** Name every container, volume, network and image you
  create `agc-<agent>-<purpose>-<random>`. `<agent>` is your tool's name
  (claude, codex, agy, opencode), `<purpose>` is one short lowercase word, and
  `<random>` is at least 16 random hex digits, for example
  `agc-codex-pytest-3f9a1c07e2b4d856`. The random part keeps the names of many
  agents and sessions apart from each other and from names that open-source
  tools or the user's organization already use. Give each one the labels
  `ai-global-config.managed=true`, `ai-global-config.agent`,
  `ai-global-config.session` and `ai-global-config.retention` (Rule
  CONTAINER-5). Select by these labels whenever you list or remove what you
  created (Rule RESOURCE-1).
- **Rule CONTAINER-5.** Make removal automatic with the engine's own features:
  - Start every container with `--rm`, so the engine removes it when it
    exits. With podman, also pass `--timeout` with the longest run you
    expect, in seconds, so podman stops the container and `--rm` removes it
    even if you never return. With podman, pass `--rmi` when the image
    serves only this run.
  - Keep results the user needs in a host directory, never only inside a
    container or a volume.
  - The retention classes are `run` (removed when the run ends), `1d`, `7d`
    and `30d`. Use a class longer than `run` only when the user asks or a
    result must stay for days. Tell the user what you kept and for how
    long. NEVER keep a docker volume past its run, because docker cannot
    prune volumes by age.
  - Before you create anything, prune what has outlived its class. For each
    class `<n>d`, run `<engine> container prune -f --filter
    label=ai-global-config.retention=<n>d --filter until=<n*24>h`. Run the
    same command with `network prune` and `image prune`. With podman, also
    run it with `volume prune`.

