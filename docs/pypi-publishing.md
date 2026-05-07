# PyPI publishing

This package is configured for PyPI Trusted Publishing through GitHub Actions.
No long-lived PyPI token is required in GitHub secrets or local config.

## Current status

The project is live on PyPI:

- Package: https://pypi.org/project/google-ads-intent-mcp/
- Initial release: `0.1.0`
- Trusted publisher: `davidmosiah/google-ads-intent-mcp` using `.github/workflows/pypi.yml`
- Environment: `pypi`

## Trusted publisher setup

The PyPI trusted publisher is already registered. If it ever needs to be recreated, use these values in PyPI account settings:

- PyPI project name: `google-ads-intent-mcp`
- Owner: `davidmosiah`
- Repository name: `google-ads-intent-mcp`
- Workflow name: `pypi.yml`
- Environment name: `pypi`

## Publishing the next release

1. Bump the version in `pyproject.toml`.
2. Run the local release checks:

   ```bash
   pytest
   python -m build
   twine check dist/*
   ```

3. Run the `Publish to PyPI` GitHub Actions workflow or publish from a GitHub release.

PyPI reference docs:

- Pending publishers: https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
- Publishing workflow: https://docs.pypi.org/trusted-publishers/using-a-publisher/

Do not add long-lived PyPI API tokens to GitHub secrets for this project.
