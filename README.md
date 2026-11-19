# yielded-home

Start here to work across Yielded’s public repositories. This repo maps each part of the stack to its source and gives contributors and coding agents one way to set up and check the components they need.

| Repository | What lives there |
| --- | --- |
| [agent](docs/repos/agent.md) | The Effect agent runtime, storage and platform adapters, and runnable examples |
| [auth](docs/repos/auth.md) | Authentication, sessions, OAuth and persistence for Effect applications |
| [sync](docs/repos/sync.md) | Realtime synchronization contracts, client and server runtimes, and platform adapters |
| [automation](docs/repos/automation.md) | Event-driven automation and durable agent workspaces |
| [site](docs/repos/site.md) | The Yielded landing page, hosted sign-in application and shared docs theme |
| [effect-tsrs](docs/repos/effect-tsrs.md) | The Rust implementation of Effect diagnostics, its CLI and Oxlint integration |

## Get started

The home scripts use Git and Python 3.11 or newer. For the default `agent` and `auth` checkouts, install the global Vite+ CLI and a supported Node.js version. The scripts read the Bun pin from each checkout’s `package.json` and select it with `vp env exec` for setup and checks. This also works when your shell prefers a different system Bun. [Vite+ environment guide](https://viteplus.dev/guide/env)

```sh
git clone https://github.com/yielded-dev/yielded-home.git
cd yielded-home
./scripts/setup          # clone the core repos into repos/ and install their dependencies
./scripts/doctor         # show paths, branches, commits, dirty state and required tools
./scripts/check agent    # run Agent's contributor checks
```

**Already have checkouts?** Before running setup, create an ignored `repos.local.toml` in this directory. For sibling clones, use the following paths.

```toml
[paths]
agent = "../agent"
auth = "../auth"
```

Paths resolve from `yielded-home`. Absolute paths and `~/` paths work too. Bootstrap verifies the Git root and origin and reuses the current branch, including a dirty worktree. Run `./scripts/bootstrap` for a clone-only setup. Running `./scripts/setup` also executes the selected repos’ dependency installers in those checkouts.

## Select repositories

Every command accepts repo names or one named profile. The default `core` profile selects Agent and Auth. `libraries` adds Sync and Automation, `web` selects Site, `tooling` selects Effect Diagnostics, and `all` selects all six. Each component guide lists its extra prerequisites.

```sh
./scripts/bootstrap --profile all --dry-run   # preview every clone or reuse
./scripts/setup sync site                     # install deps and Sync's test browser
./scripts/doctor --profile libraries
./scripts/check --dry-run sync site           # inspect commands even before cloning
./scripts/check sync site                     # run them in each checkout
```

Setup and check stop at the first failing command in each repo, continue with the other selections, and return a failing exit status if any repo fails. A dry run only prints the plan. [Repository catalog](repos.toml)

## Work from this repo

Start your coding agent in this checkout and point it at `AGENTS.md`. Claude Code loads the same instructions through `CLAUDE.md`. The architecture guide covers questions that span repositories, such as whether a sign-in change belongs to the Auth library or the hosted application. [Agent instructions](AGENTS.md) · [Architecture](docs/architecture.md) · [Engineering](docs/engineering.md)

The home repo includes the shared skills and their linked references from a public Agent revision. Each skill directory carries its origin receipt. Keep notices and licenses with the files when refreshing them. [Source snapshot](https://github.com/yielded-dev/agent/tree/b3abdfb97ff73e5ff505c0bb7b35c796fff01c9e/.agents/skills) · [Bundled skills](.agents/skills/)

After changing the catalog, docs or scripts, run the same offline checks as CI.

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests
./scripts/setup --dry-run --profile all
```
