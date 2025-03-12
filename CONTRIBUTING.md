# Contributing to Auto-LinkedIn

Thank you for considering contributing to Auto-LinkedIn! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

- Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/main-salman/auto-linkedin/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/main-salman/auto-linkedin/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or a **reproducible test case** demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements

- Open a new issue with a clear title and detailed description.
- Provide specific examples and steps to demonstrate the enhancement.
- Explain why this enhancement would be useful to most Auto-LinkedIn users.

### Pull Requests

1. Fork the repository.
2. Create a new branch from `main` for your feature or bug fix.
3. Make your changes, including appropriate tests.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Submit a pull request to the `main` branch.

## Development Setup

1. Clone your fork of the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/auto-linkedin.git
   cd auto-linkedin
   ```

2. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install Playwright browsers:
   ```bash
   python -m playwright install chromium
   ```

4. Run tests to verify your setup:
   ```bash
   pytest
   ```

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.
- Write docstrings for all functions, classes, and methods following [Google style guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Write meaningful commit messages that clearly explain the changes.

## Running Tests

Run the test suite with pytest:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=auto_linkedin
```

## Documentation

Any new feature or change should include corresponding documentation updates. Documentation is written in Markdown and stored in the `docs/` directory.

## License

By contributing to Auto-LinkedIn, you agree that your contributions will be licensed under the project's [MIT License](LICENSE). 