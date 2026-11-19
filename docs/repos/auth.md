# Auth

Auth owns the Effect libraries for authentication, sessions and identity. Look in `packages/auth` for the core, `packages/oauth` for OAuth, and the persistence and platform packages for their adapters. The hosted Yielded sign-in application is a consumer in Site’s `apps/auth`. [Source](https://github.com/yielded-dev/auth) · [Contributor instructions](https://github.com/yielded-dev/auth/blob/main/AGENTS.md) · [Hosted application](https://github.com/yielded-dev/site/tree/main/apps/auth)

From home, run `./scripts/setup auth` and `./scripts/check auth`. The check runs `vp run ready`, including package exports, tests and package-consumer builds. Use the examples when changing adapter behavior and update the guides beside the library. [Toolchain](https://github.com/yielded-dev/auth/blob/main/docs/TOOLCHAIN.md) · [Examples](https://github.com/yielded-dev/auth/tree/main/examples) · [Auth docs](https://yielded.dev/auth/)
