# Development

## Get started

Ready to contribute? Here's how to set up `lab_adaption` for local development.

1. Clone the repository from GitLab:
   ```bash
   git clone git@gitlab.com:OpenLabAutomation/adaption-template.git
   cd adaption-template
   ```
2. Create and activate a virtualenv with Python 3.12 or higher:
   ```bash
   python -m venv labautomation
   source labautomation/bin/activate
   ```
3. Install the package with its development dependencies and the pre-commit hooks:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```
4. Create a branch for local development (please do not use `#` in branch names):
   ```bash
   git checkout -b feature/IssueNumber_name-of-your-bugfix-or-feature
   ```
5. When you're done making changes, check that linting, formatting and tests pass:
   ```bash
   ruff check
   ruff format --check
   pytest tests/
   ```
6. Commit your changes and push your branch to GitLab:
   ```bash
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin feature/IssueNumber_name-of-your-bugfix-or-feature
   ```
7. Submit a merge request through GitLab.

## Merge request guidelines

Before you submit a merge request, check that it meets these guidelines:

1. The merge request should only include changes relating to one ticket.
2. The merge request should include tests to cover any added changes and
   check that all existing and new tests pass.
3. If the merge request adds functionality, the docs should be updated.
   Put your new functionality into a function with a docstring, and add
   the feature to the list in README.md.
4. The team should be informed of any impactful changes.

## Documentation

The documentation is built with [MkDocs](https://www.mkdocs.org/) (Material theme) from the `docs/` directory.
Install the docs dependencies and serve it locally with live reload:

```bash
pip install -e ".[docs]"
make serve
```

`make build` builds the static site into `site/`. On `main`, the GitLab CI `pages` job publishes it to GitLab Pages.

## Tips

To run a subset of tests:

```bash
pytest tests/test_process_registration.py
```

## Releasing

For every release:

1. Add your changes to the `## Unreleased` section of HISTORY.md.
2. Bump the version (`patch`, `minor` or `major`). This updates `pyproject.toml`, `lab_adaption/__init__.py`,
   `CITATION.cff` and HISTORY.md, then commits and tags:
   ```bash
   bump-my-version bump minor
   ```
3. Push the commit and the tag:
   ```bash
   git push --follow-tags
   ```

On a tag, the GitLab CI pipeline builds the package and uploads it to the GitLab package registry, and the
Zenodo job publishes the release to Zenodo.
