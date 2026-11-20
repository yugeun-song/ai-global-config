### RESOURCE: host resources

- **Rule RESOURCE-1.** Tear down everything you start: VMs, containers,
  daemons, background jobs. Record each one's PID, name or label when you
  start it, and tear down exactly that one. The user or another agent may
  run the same program at the same time, so NEVER kill processes by a broad
  name pattern.
- **Rule RESOURCE-2.** While you write bulk data, watch the memory and the
  disk you write to. When either reaches 90% of its capacity, stop writing
  and free space you created. Put scratch data on a memory-backed
  filesystem, such as tmpfs on Linux, when the operating system has one,
  and in its temporary directory otherwise.
- **Rule RESOURCE-3.** Before a CPU-heavy job, tell the user that it starts and
  roughly how long it takes. Then start it without waiting for an answer.
- **Rule RESOURCE-4.** When the user says stop, stop calling tools and answer in
  text.

