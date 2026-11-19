# Yielded home

Use this repo to find the owner of a change and coordinate work across the public Yielded stack. Start with the component guide below. Read the target checkout’s `AGENTS.md` and relevant implementation before changing it. Each component owns its code, toolchain, tests, package versions and releases.

| Task | Start here |
| --- | --- |
| Agent runtime, tools, threads, storage or platform adapters | [Agent](docs/repos/agent.md) |
| Auth library, identities, sessions, OAuth or persistence | [Auth](docs/repos/auth.md) |
| Realtime protocol, sync clients or server adapters | [Sync](docs/repos/sync.md) |
| Event decisions, sandbox execution or recovery | [Automation](docs/repos/automation.md) |
| Landing page, hosted sign-in service or shared docs theme | [Site](docs/repos/site.md) |
| Effect diagnostic rules, compiler integration or native CLI | [Effect Diagnostics](docs/repos/effect-tsrs.md) |

## Working in components

- Resolve the selected checkouts with `./scripts/doctor <repo>`. Paths can point at existing clones or linked worktrees. Check branch, revision and local changes before editing.
- For a change that crosses repositories, identify the producer, the consumer and the interface they share. Record the revisions exercised together. [Architecture](docs/architecture.md)
- Run the affected components’ own checks. Use `./scripts/check --dry-run <repo>` to inspect commands and `./scripts/check <repo>` to execute them. Report which checks ran and which prerequisites prevented further verification. [Engineering](docs/engineering.md)
- Keep cross-repo routing and commands here. Put implementation details, public API documentation and release notes in the owning component.

## Public libraries

Merging changes into a public library or publishing a release requires explicit user confirmation or unmistakable advance permission covering that repository and action. This includes version PRs, changesets and work delegated to another agent. Permission for a consuming application applies to that application alone. When authority is ambiguous, prepare the reviewable change and ask before merging or publishing.

## Agent settings

Use the host’s default model, reasoning effort, service tier and subagent settings unless the user selects an override. Keep delegation proportional to the task. Duplicate competing runs require an explicit request. Use configured defaults for Sow handoffs unless the user requests flags.

## Portable skills

Use the target repo’s pinned workflow when working in that repo. These copies also work from a fresh home checkout.

- Public API and package boundaries are covered by [library-first](.agents/skills/library-first/SKILL.md) and [Effect](.agents/skills/effect/SKILL.md).
- Choose verification with [testing](.agents/skills/testing/SKILL.md). For performance-sensitive changes, use [measure-performance](.agents/skills/measure-performance/SKILL.md).
- Prepare or review pull requests with [pull-requests](.agents/skills/pull-requests/SKILL.md). The public-library approval rule above applies throughout the workflow.

For home repo changes, run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests`. Keep machine-specific paths in the ignored local override.
