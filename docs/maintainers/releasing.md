# Releasing MultiCloud Python

All 21 `multicloud-py-*` distributions share the version in `VERSION` and
are released together under one `multicloud-py-v*` tag.

## How the release version is chosen

We use [Release Please](https://github.com/googleapis/release-please) to open
and maintain a release pull request after changes are merged to `main`. It is
the release automation project maintained by the
[googleapis](https://github.com/googleapis) GitHub organization.

The version-increment policy is provided by Release Please's built-in
[`DefaultVersioningStrategy`](https://github.com/googleapis/release-please/blob/main/src/versioning-strategies/default.ts),
not by custom Python SDK code. Our
[`release-please-config.json`](https://github.com/salesforce/multicloud-py/blob/main/release-please-config.json)
selects the `simple` file-update strategy, specifies the `multicloud-py` tag
component, and tells Release Please to update `VERSION`; it does **not**
override the version-increment policy.

| Change merged since the last release | Commit convention | Result from `0.1.4` |
| --- | --- | --- |
| Backward-compatible bug fix | `fix: ...` | `0.1.5` |
| Backward-compatible capability | `feat: ...` | `0.2.0` |
| Breaking public API change | `feat!: ...` or a `BREAKING CHANGE:` footer | `1.0.0` |

Release Please calculates the largest required increment among the commits
since the previous release. It records the last released version in
[`.release-please-manifest.json`](https://github.com/salesforce/multicloud-py/blob/main/.release-please-manifest.json),
then proposes the next version in a release PR. The release configuration uses
`include-component-in-tag` and `include-v-in-tag`, so version `0.1.4` produces
the Git tag `multicloud-py-v0.1.4`.

The same default applies before `1.0.0`: `0.9.9` becomes `0.9.10` for a patch,
`0.10.0` for a feature, and `1.0.0` for a breaking change. Reaching `0.9.9`
does not itself trigger a major release.

Use `Release-As: X.Y.Z` in a commit footer only when intentionally overriding
the calculated version, such as the initial `0.1.4` bootstrap release. Do not
manually edit the manifest for an ordinary release.

After Release Please updates `VERSION`, the
[`sync-release-pr` job](https://github.com/salesforce/multicloud-py/blob/main/.github/workflows/release.yml)
runs `scripts/sync_version.py` and `uv lock` on the generated release branch.
This propagates the selected version to every distribution's `pyproject.toml`,
inter-package dependency constraints, and lock file before the release PR is
reviewed.

## One-time administrator setup

1. In GitHub Actions settings, allow workflows to create pull requests and
   grant read/write workflow permissions. Release Please and the synchronization
   job use the repository `GITHUB_TOKEN`; do not add a personal access token or
   GitHub App credential.
2. Create the protected GitHub `pypi` environment, with the required release
   reviewers. The TestPyPI bootstrap uses one environment per distribution:
   `testpypi-<distribution-name>`.
3. TestPyPI permits only three pending Trusted Publishers at a time. Register
   the three distributions in one bootstrap batch with owner `salesforce`,
   repository `multicloud-py`, workflow `test-pypi.yml`, and environment
   `testpypi-<distribution-name>`. Run **TestPyPI Rehearsal** for that batch;
   successful publication converts those three entries to active publishers and
   frees three pending slots. Repeat for all seven batches before the complete
   TestPyPI installation rehearsal.
4. Require the normal pull-request CI workflow on `main`.

## First release

1. Push this bootstrap commit, which carries `Release-As: 0.1.4`.
2. Release Please opens one release PR and the synchronization job updates all
   package versions and `uv.lock` on that branch.
3. Because `GITHUB_TOKEN` updates do not automatically start PR workflows, a
   maintainer must approve or rerun normal PR CI on the latest synchronized
   commit.
4. Before merging the first release PR, run **TestPyPI Rehearsal** against the
   release branch for each required batch and confirm all 21 distributions are
   available at the expected version.
5. Merge the PR. The tagged-release validation builds 21 wheels and 21 sdists,
   verifies their metadata/licenses, and smoke-tests isolated installed wheels.
   Only then can the protected `pypi` deployment be approved.

PyPI and TestPyPI versions are immutable. If a partial upload occurs, fix
forward with a new version—never retry the same version.
