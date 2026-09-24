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

The version line in `VERSION` carries Release Please's required
`x-release-please-version` annotation. Repository scripts parse only the
semantic version before that annotation, while Release Please uses the marker
to update the file in every generated release PR.

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
   reviewers. It is used only after the one-time production PyPI bootstrap is
   complete. The bootstrap workflows use one environment per distribution:
   `testpypi-<distribution-name>` for TestPyPI and
   `pypi-<distribution-name>` for production PyPI.
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
   The automatic production publish job is intentionally skipped until
   `PYPI_BOOTSTRAP_COMPLETE` is set to `true`.

## One-time production PyPI bootstrap

Production PyPI treats every distribution as an independent project. A single
pending Trusted Publisher configuration cannot create all 21 projects, so the
first production release is intentionally staged.

1. Keep the repository Actions variable `PYPI_BOOTSTRAP_COMPLETE` unset (or
   set to anything other than `true`). This prevents `release.yml` from
   publishing the first tag through the shared `pypi` environment.
2. After the first release tag exists, register three **pending** publishers at
   a time on PyPI. For each distribution, use owner `salesforce`, repository
   `multicloud-py`, workflow `bootstrap-pypi.yml`, and environment
   `pypi-<distribution-name>`. PyPI permits only three pending publishers at
   once.
3. Run **Bootstrap production PyPI** with that release tag and its batch. It
   checks out and fully validates the tag before publishing only that batch's
   three distributions. A successful upload turns the three pending publishers
   into active publishers. Repeat for all seven batches.
4. Verify the 21 released projects and install the published distributions from
   production PyPI in a fresh environment.
5. On each existing PyPI project, add the shared, ordinary Trusted Publisher:
   owner `salesforce`, repository `multicloud-py`, workflow `release.yml`, and
   environment `pypi`. This configuration can be shared because all projects
   already exist.
6. Set the GitHub Actions repository variable `PYPI_BOOTSTRAP_COMPLETE` to
   `true`. Future tagged releases use the protected `pypi` environment and
   upload the complete validated artifact set together.

PyPI and TestPyPI versions are immutable. If any bootstrap upload fails after
an artifact reaches PyPI, stop and inspect the project before continuing. Do
not overwrite or delete artifacts; release a new version if the published set
cannot be completed safely.
