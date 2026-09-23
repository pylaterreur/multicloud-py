# Releasing MultiCloud Python

All 21 `sfdc-multicloud-*` distributions share the version in `VERSION` and
are released together under one `multicloud-py-v*` tag.

## One-time administrator setup

1. In GitHub Actions settings, allow workflows to create pull requests and
   grant read/write workflow permissions. Release Please and the synchronization
   job use the repository `GITHUB_TOKEN`; do not add a personal access token or
   GitHub App credential.
2. Create protected GitHub environments named `pypi` and `testpypi`, with the
   required release reviewers.
3. In both PyPI and TestPyPI, create a pending Trusted Publisher for every
   `sfdc-multicloud-*` distribution. Use owner `salesforce`, repository
   `multicloud-py`, and environments `pypi`/`testpypi`; use `release.yml` for
   PyPI and `test-pypi.yml` for TestPyPI.
4. Require the normal pull-request CI workflow on `main`.

## First release

1. Push this bootstrap commit, which carries `Release-As: 0.1.4`.
2. Release Please opens one release PR and the synchronization job updates all
   package versions and `uv.lock` on that branch.
3. Because `GITHUB_TOKEN` updates do not automatically start PR workflows, a
   maintainer must approve or rerun normal PR CI on the latest synchronized
   commit.
4. Before merging the first release PR, run **TestPyPI Rehearsal** against the
   release branch, approve the `testpypi` environment, and confirm all 21
   distributions are available at the expected version.
5. Merge the PR. The tagged-release validation builds 21 wheels and 21 sdists,
   verifies their metadata/licenses, and smoke-tests isolated installed wheels.
   Only then can the protected `pypi` deployment be approved.

PyPI and TestPyPI versions are immutable. If a partial upload occurs, fix
forward with a new version—never retry the same version.
