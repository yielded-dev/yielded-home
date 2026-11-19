# Working across Yielded

## Prepare the checkout

Run `./scripts/doctor <repo>` in the home repo to see the selected path, revision and working-tree state. Bootstrap clones a missing repo and inspects an existing one. Fetch in the component when the task calls for current `origin/main`. If local work is in progress, use a separate branch and worktree for your change.

## Use the component toolchain

Agent, Auth, Sync, Automation and Site use Vite+ and Bun. Follow the Node range, package-manager pin and lockfile in the checkout you are changing. Run `vp` commands from that repo’s root. Effect Diagnostics uses npm and a pinned Rust toolchain. The setup and check entries in the catalog point to the contributor commands for each. [Catalog](../repos.toml)

Start verification at the smallest boundary that exercises the change. For a package export or API change, include a consumer that imports the candidate package. For storage or runtime behavior, exercise the relevant adapter. When changes span repos, record how the consumer resolved the producer’s build and which commits and commands passed. Component CI may also run integration suites that require a service, a browser or a particular platform.

## Review and release

Open each code or documentation change in the repo that owns it. Link related changes and describe any ordering dependency. Use the component’s changeset and release guidance for published packages. Obtain explicit permission for the specific public library and action before merging a PR or publishing a release. [Public-library policy](../AGENTS.md#public-libraries)

## Maintain the workspace

Keep checkout path overrides, credentials and dependency installs local. To add a component, add its public remote, contributor commands and profile membership to the catalog, write its guide in `docs/repos/`, and update the navigation in the README and agent instructions. Use the home checks documented in the README to validate the change. [Home checks](../README.md#work-from-this-repo)
