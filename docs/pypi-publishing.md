# PyPI publishing

This package is configured for PyPI Trusted Publishing through GitHub Actions.
No long-lived PyPI token is required in GitHub secrets or local config.

## One-time PyPI setup

Create a pending GitHub publisher in PyPI account settings:

- PyPI project name: `google-ads-intent-mcp`
- Owner: `davidmosiah`
- Repository name: `google-ads-intent-mcp`
- Workflow name: `pypi.yml`
- Environment name: `pypi`

PyPI docs:

- Pending publishers: https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
- Publishing workflow: https://docs.pypi.org/trusted-publishers/using-a-publisher/

After the pending publisher exists, run the `Publish to PyPI` GitHub Actions
workflow manually or publish a GitHub release.
