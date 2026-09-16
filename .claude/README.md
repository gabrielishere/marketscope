# .claude

The builder method and the agent definitions that run it.

- `builder/` — the method: templates, and the documents that explain them. Domain-neutral.
- `agents/` — `orchestrator` and `implementor`, the two roles that run a build.

The flow: **spec → prompt → gate → implementor → verify**. An orchestrator runs one spec,
gating each prompt against the workspace immediately before dispatching it.

Start at [`builder/method/reading-the-input.md`](builder/method/reading-the-input.md).
