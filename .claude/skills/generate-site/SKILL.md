---
name: generate-site
description: Use when previewing, validating, publishing, or diagnosing the MultiCloud-Py documentation website and its GitHub Pages deployment.
---

# Build and publish the documentation website

Read `AGENTS.md`, `mkdocs.yml`, `.github/workflows/docs.yml`, and
`docs/maintainers/website.md`. Sources live on `main` in `docs/`. API pages
are rendered from source docstrings by mkdocstrings. This public repository
deploys an Actions artifact, rather than committing generated HTML to a branch.

## Preview and validate

Use a clean, current checkout or an isolated worktree; preserve existing work.
From the repository root:

```bash
uv run --frozen --group docs mkdocs build --strict
uv run --frozen --group docs mkdocs serve
```

Use the local URL printed by MkDocs. Fix build errors in source; do not
suppress strict warnings. Inspect rendered pages and check the links and
Python imports changed by the task. Do not commit the ignored `site/` output.
For content changes, use `multi-cloudpy-docs-guides` and open a PR to `main`.

## Publish

Merging a source PR into `main` triggers the Documentation workflow. Pull
requests build without deploying. For an authorized republish of current
`main`, inspect the existing run first and then use:

```bash
gh workflow run docs.yml --repo salesforce/multicloud-py --ref main
gh run list --repo salesforce/multicloud-py --workflow docs.yml --limit 5
```

Resolve the matching run ID from its branch and commit before watching it:

```bash
gh run watch RUN_ID --repo salesforce/multicloud-py --exit-status
gh api repos/salesforce/multicloud-py/pages
```

Publication needs repository Settings → Pages → Source set to **GitHub
Actions**. A Pages API 404 or `Configure Pages` failure can mean missing
setup or insufficient access; confirm repository permissions before diagnosing
it. Report a missing setup step rather than claiming publication succeeded.
Do not change Pages settings, merge PRs, or dispatch deployments without
authorization for the corresponding action.

The deployment job needs `pages: write`, `id-token: write`, a successful build,
and the `github-pages` environment. Confirm the returned Pages URL and check
the public homepage and a guide after deployment. If a run fails, inspect
`gh run view RUN_ID --repo salesforce/multicloud-py --log-failed` and fix the
identified problem before retrying.

The canonical URL is `https://opensource.salesforce.com/multicloud-py/`.
The shared organization domain is inherited; do not add a repository `CNAME`
for it. Do not use `mkdocs gh-deploy`, force-push a publishing branch, or
reset the working tree as part of this workflow.

Report the source PR or commit, strict-build result, deployment status, and
verified URL. Distinguish a local preview from a published site.
