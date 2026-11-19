# Repository ownership

Yielded distributes independent libraries. A workspace profile selects checkouts for a task. Each checkout’s manifest and lockfile determine the package versions it builds against. Cloning two repos side by side does not link their packages.

| Question | Where to make the change |
| --- | --- |
| How does an agent execute a tool and persist a run? | Agent owns the execution model and its storage and platform adapters. |
| What should happen when an event arrives, and how can an interrupted workspace resume? | Automation owns event policy and the Sandbox package owns durable workspace execution. Both packages live in the Automation repo. |
| How does an application establish a session? | Auth owns the session and identity libraries. Site owns the hosted sign-in application in `apps/auth`. |
| How does application state stay in sync across clients? | Sync owns the shared protocol, client/server runtimes and adapters. |
| Where should a docs change land? | The library owns its guides and examples. Site owns the shared Starlight theme, library registry and landing page. |
| Is a diagnostic incorrect in more than one project? | Reproduce the rule against a fixture in Effect Diagnostics. The consuming repo owns its compiler configuration and pinned tool version. |

For example, a change to a shared navigation component starts in Site’s theme. To verify it in library docs, use Site’s local theme-development instructions, build the affected library’s docs against the candidate theme and record both revisions. The owning repo’s release process handles distribution. [Site toolchain](https://github.com/yielded-dev/site/blob/main/docs/TOOLCHAIN.md)
