# Site

Site owns the landing page in `apps/landing`, the hosted sign-in application in `apps/auth`, and `@yielded/starlight-theme` in `packages/starlight-theme`. Shared navigation and the library registry belong in the theme. Each library keeps its own documentation content. [Source](https://github.com/yielded-dev/site) · [Theme](https://github.com/yielded-dev/site/tree/main/packages/starlight-theme) · [Contributor instructions](https://github.com/yielded-dev/site/blob/main/AGENTS.md)

Run `./scripts/setup site` and `./scripts/check site`. The check uses `vp run ready` for static checks and builds. From the Site checkout, `vp run dev` starts the landing page. The toolchain guide explains how to test a theme edit in a consuming docs site. [Toolchain](https://github.com/yielded-dev/site/blob/main/docs/TOOLCHAIN.md)
