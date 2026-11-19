# Agent

Agent owns the TypeScript harness for building agents with Effect and Effect AI. Start in `packages/effect-agent` for the runtime, in `packages/platform-*` and `packages/storage-*` for adapters, and in `examples/` for working consumers. Use the glossary for terms such as thread and run. [Source](https://github.com/yielded-dev/agent) · [Contributor instructions](https://github.com/yielded-dev/agent/blob/main/AGENTS.md) · [Glossary](https://github.com/yielded-dev/agent/blob/main/GLOSSARY.md)

From home, run `./scripts/setup agent` and `./scripts/check agent`. The check runs `vp run ready` for static checks, tests and builds. Changes to Postgres storage may also need the live database coverage described in the component’s CI. For changes that touch user-facing behavior, the examples and documentation live in this checkout. [Toolchain](https://github.com/yielded-dev/agent/blob/main/docs/TOOLCHAIN.md) · [CI](https://github.com/yielded-dev/agent/blob/main/.github/workflows/ci.yml)
