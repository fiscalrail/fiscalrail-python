# Releasing FiscalRail for Python

Releases use PyPI Trusted Publishing. The repository does not store a PyPI API
token.

## One-time setup

1. Create a PyPI account, verify its email address, enable two-factor
   authentication, and save the recovery codes.
2. Register a pending Trusted Publisher at
   <https://pypi.org/manage/account/publishing/> with:

   - PyPI project name: `fiscalrail`
   - GitHub owner: `fiscalrail`
   - GitHub repository: `fiscalrail-python`
   - Workflow filename: `release.yml`
   - Environment name: `pypi`

3. Create a GitHub Environment named `pypi` and require a maintainer's approval
   before deployment. Restrict deployment to protected tags when the repository
   plan supports it.

The first successful Trusted Publishing upload creates the PyPI project. Do not
create or store a long-lived `PYPI_API_TOKEN` GitHub secret.

## Publish a release

1. Update the version in `pyproject.toml` and add the release to
   `CHANGELOG.md`.
2. Run:

   ```bash
   uv run python scripts/generate_contract.py --check
   uv run pytest
   uv run ty check
   uv run ruff check .
   uv build
   ```

3. Push the release commit.
4. Create and publish a GitHub Release whose tag is exactly `v<version>`, such
   as `v0.1.0`.
5. Approve the `pypi` deployment in GitHub Actions.

The release workflow verifies that the Git tag matches `pyproject.toml`, reruns
the SDK checks, builds the wheel and source distribution in a separate job, and
publishes those exact artifacts to PyPI.
