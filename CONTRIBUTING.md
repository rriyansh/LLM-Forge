
# Contributing to LLM-Forge

<p align="left">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square&logo=github&logoColor=white" alt="PRs Welcome" />
  <img src="https://img.shields.io/badge/contributions-open-blue?style=flat-square&logo=opensourceinitiative&logoColor=white" alt="Contributions Open" />
  <img src="https://img.shields.io/badge/code%20of%20conduct-v2.1-purple?style=flat-square&logo=contributorcovenant&logoColor=white" alt="Code of Conduct" />
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square&logo=opensourceinitiative&logoColor=white" alt="License MIT" />
</p>

First off, thank you for considering contributing to LLM-Forge. It is people like
you who make open-source projects such a great community to learn, inspire, and
create.

We welcome contributions of all kinds: bug reports, feature requests, documentation
improvements, code patches, and design feedback. This document outlines the process
to make contributing as smooth as possible for everyone involved.

Please take a moment to read through this guide. Following these guidelines helps
maintainers and contributors communicate effectively and keeps the project healthy.

---

## Table of Contents

| | Section |
|---|---|
| ▸ | [Code of Conduct](#code-of-conduct) |
| ▸ | [Getting Started](#getting-started) |
| ▸ | [How Can I Contribute](#how-can-i-contribute) |
| ▸ | [Development Setup](#development-setup) |
| ▸ | [Coding Standards](#coding-standards) |
| ▸ | [Commit Message Convention](#commit-message-convention) |
| ▸ | [Testing Guidelines](#testing-guidelines) |
| ▸ | [Review Process](#review-process) |
| ▸ | [Security Vulnerabilities](#security-vulnerabilities) |
| ▸ | [Community](#community) |
| ▸ | [License](#license) |

---

## Code of Conduct

<img src="https://img.shields.io/badge/required-read%20first-red?style=flat-square&logo=contributorcovenant&logoColor=white" alt="Required" />

This project and everyone participating in it is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to
uphold this code. Please report unacceptable behavior to
[conduct@llmforge.dev](mailto:conduct@llmforge.dev).

---

## Getting Started

<img src="https://img.shields.io/badge/step-1-blue?style=flat-square" alt="Step 1" />

Before you begin, please check the [issue tracker](https://github.com/yourorg/llm-forge/issues)
to see whether the bug or feature you have in mind has already been reported.
Duplicate issues slow down the triage process.

If you are new to the project, look for issues tagged with:

| Label | Meaning |
|---|---|
| <img src="https://img.shields.io/badge/good%20first%20issue-7057ff?style=flat-square" alt="good first issue" /> | Simple, well-scoped tasks ideal for newcomers |
| <img src="https://img.shields.io/badge/help%20wanted-008672?style=flat-square" alt="help wanted" /> | Tasks where we explicitly welcome external contributions |
| <img src="https://img.shields.io/badge/documentation-0075ca?style=flat-square" alt="documentation" /> | Non-code contributions that improve the docs |

---

## How Can I Contribute

### Reporting Bugs

<img src="https://img.shields.io/badge/bug%20report-d73a4a?style=flat-square&logo=github&logoColor=white" alt="Bug Report" />

If you find a bug, please open an issue on the [issue tracker](https://github.com/yourorg/llm-forge/issues).
A good bug report should include:

**Title**: Use a clear and descriptive title that summarizes the problem.

**Description**: Describe the exact steps which reproduce the problem in as
many details as possible. Include:

| Item | Description |
|---|---|
| Version | Commit SHA, tag, or branch of LLM-Forge |
| OS | Operating system and version |
| Python | Python version |
| GPU | GPU model and CUDA version (if applicable) |
| Runtime | vLLM and PyTorch version |
| Deployment | Docker or bare-metal |
| Env | Relevant environment variables (redact secrets first) |

**Expected behavior**: What you expected to happen.

**Actual behavior**: What actually happened, including the full stack trace
or error message.

**Reproduction**: Provide a minimal, reproducible example. Ideally a short
script or `curl` command that reliably triggers the bug.

**Logs**: Attach the relevant portion of the application logs. Use `LOG_LEVEL=DEBUG`
to capture more detail. Redact any API keys, tokens, or PII before posting.

**Additional context**: Screenshots, related issues, or links to relevant
discussions.

> **Warning**: Do not include sensitive information such as real API keys,
> passwords, or personal data. If you must share sensitive material, use a
> secure channel (see [Security Vulnerabilities](#security-vulnerabilities)).

---

### Suggesting Enhancements

<img src="https://img.shields.io/badge/enhancement-a2eeef?style=flat-square&logo=github&logoColor=black" alt="Enhancement" />

Enhancement suggestions are tracked as GitHub issues. When creating an
enhancement issue, please:

| ▸ | Use a clear and descriptive title that summarizes the suggestion |
|---|---|
| ▸ | Provide a step-by-step description of the enhancement |
| ▸ | Explain the current behavior and why it is insufficient |
| ▸ | Describe the desired behavior and how it solves the problem |
| ▸ | Include specific examples (input/output pairs, API sketches, or mockups) |
| ▸ | Consider alternatives you have evaluated and why they are less suitable |
| ▸ | Assess impact: who benefits, how often, and how significantly |

Before opening the issue, search existing issues and pull requests for
similar suggestions. If a related discussion exists, add a comment there
instead of opening a new one.

---

### Improving Documentation

<img src="https://img.shields.io/badge/documentation-0075ca?style=flat-square&logo=readthedocs&logoColor=white" alt="Documentation" />

Documentation contributions are highly valued. This includes:

| ▸ | Fixing typos, grammar, or broken links |
|---|---|
| ▸ | Clarifying ambiguous sections |
| ▸ | Adding missing examples or use cases |
| ▸ | Writing tutorials or guides |
| ▸ | Translating documentation (see issue label `translation`) |
| ▸ | Updating screenshots or diagrams |

You can propose documentation changes directly via a pull request. For
significant additions (new pages, new sections), please open an issue first
to discuss scope and placement.

---

### Submitting Pull Requests

<img src="https://img.shields.io/badge/pull%20request-2ea44f?style=flat-square&logo=git&logoColor=white" alt="Pull Request" />

Following this workflow helps us review and merge your PR quickly:

| Step | Action | Command |
|---|---|---|
| **1** | Fork the repository and create a branch | `git checkout -b feat/short-descriptive-name` |
| **2** | Set up your development environment | See [Development Setup](#development-setup) |
| **3** | Make changes following the coding standards | See [Coding Standards](#coding-standards) |
| **4** | Add or update tests | All features need tests; bugs need regression tests |
| **5** | Update documentation | For user-facing changes |
| **6** | Run the full local suite | `make lint typecheck test security-scan` |
| **7** | Commit using Conventional Commits | See [Commit Message Convention](#commit-message-convention) |
| **8** | Push and open a pull request | Fill in the PR template completely |
| **9** | Respond to review feedback | Maintainers may request changes |
| **10** | Approved, then merged | Maintainer merges per repo settings |

Use a branch name that reflects the change:

| Prefix | Purpose |
|---|---|
| `feat/...` | New features |
| `fix/...` | Bug fixes |
| `docs/...` | Documentation |
| `chore/...` | Maintenance |
| `refactor/...` | Refactoring |
| `perf/...` | Performance |
| `test/...` | Tests only |

Please keep pull requests focused on a single concern. If you find yourself
touching multiple unrelated areas, split the changes into separate PRs.

---

## Development Setup

<img src="https://img.shields.io/badge/setup-required-orange?style=flat-square&logo=gnubash&logoColor=white" alt="Setup" />

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" /> | 3.11 or newer | Runtime |
| <img src="https://img.shields.io/badge/Git-latest-F05032?style=flat-square&logo=git&logoColor=white" alt="Git" /> | Latest | Version control |
| <img src="https://img.shields.io/badge/Docker-24%2B-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" /> | 24 or newer | Local Redis and Postgres |
| <img src="https://img.shields.io/badge/CUDA-12.x-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="CUDA" /> | 12.x | Only for training or serving tests |
| <img src="https://img.shields.io/badge/Make-GNU-6D00CC?style=flat-square&logo=gnu&logoColor=white" alt="Make" /> | GNU Make | Build scripts |

### First-time setup

```bash
# 1. Clone your fork
git clone https://github.com/<your-username>/llm-forge.git
cd llm-forge

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate         # Linux / macOS
# .venv\Scripts\activate          # Windows

# 3. Install dependencies
make install-dev

# 4. Set up pre-commit hooks
pre-commit install

# 5. Configure environment
cp .env.example .env
# Edit .env with development-safe values:
#   API_KEY=dev_dev_dev_dev_dev_dev_dev_dev_dev_dev
#   JWT_SECRET_KEY=$(openssl rand -hex 32)
#   ENV=dev
#   LOG_LEVEL=DEBUG

# 6. Start local services
docker compose -f docker/docker-compose.yml up -d redis postgres

# 7. Verify setup
make lint typecheck test
```

### Daily workflow

```bash
# Pull latest changes
git checkout main
git pull --rebase origin main

# Create a feature branch
git checkout -b feat/my-feature

# Make changes, then format and test
make format
make lint typecheck test

# Commit and push
git add -A
git commit -m "feat(scope): short description"
git push origin feat/my-feature
```

---

## Coding Standards

<img src="https://img.shields.io/badge/standards-enforced-critical?style=flat-square&logo=ruff&logoColor=white" alt="Standards" />

### Python Style

| ▸ | **Python 3.11+** features only. Use modern syntax such as `X | Y` unions, `match` statements, `Self` type, and f-strings with `=` for debugging. |
|---|---|
| ▸ | **Type hints everywhere**. All function signatures must be fully typed. The project enforces `mypy --strict`; untyped functions will fail CI. |
| ▸ | **Line length is 100 characters**. Enforced by both `black` and `ruff`. |
| ▸ | **Use `async def` for all I/O-bound code**. Blocking calls in request paths must be offloaded to a thread via `asyncio.to_thread`. |
| ▸ | **Use structured logging**. Always use `get_logger()` from `src.utils.logger` and emit structured events with `log.info("event", key=value)`. Never use `print()` in application code. |
| ▸ | **Never hardcode secrets**. Read from environment variables or a secret manager. The structlog processor will redact obvious secrets in logs, but they must never appear in source. |
| ▸ | **Fail closed for security-critical paths**. If a security check cannot be performed, deny the request rather than allowing it through. |

### Tool badges

<p align="left">
  <img src="https://img.shields.io/badge/ruff-D7FF64?style=flat-square&logo=ruff&logoColor=black" alt="Ruff" />
  <img src="https://img.shields.io/badge/black-000000?style=flat-square&logo=python&logoColor=white" alt="Black" />
  <img src="https://img.shields.io/badge/mypy-2A6DB2?style=flat-square&logo=python&logoColor=white" alt="mypy" />
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="pytest" />
  <img src="https://img.shields.io/badge/pre--commit-FAB040?style=flat-square&logo=pre-commit&logoColor=black" alt="pre-commit" />
  <img src="https://img.shields.io/badge/gitleaks-000000?style=flat-square&logo=git&logoColor=white" alt="gitleaks" />
</p>

### Naming Conventions

| Entity | Convention | Example |
|---|---|---|
| Modules | `snake_case` | `rate_limiter.py` |
| Packages | `snake_case` | `src/serving/` |
| Classes | `PascalCase` | `SemanticCache` |
| Functions | `snake_case` | `verify_api_key` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_REQUEST_BYTES` |
| Private members | `_leading_underscore` | `_engine` |
| Type aliases | `PascalCase` | `Principal` |

### File and Directory Layout

| ▸ | One module per concern. If a file grows beyond 500 lines, consider splitting. |
|---|---|
| ▸ | `__init__.py` files should export the public API of the package and be otherwise empty. |
| ▸ | Tests mirror the source tree: `src/serving/cache.py` is tested by `tests/test_cache.py`. |
| ▸ | Configuration files live in `configs/` and are loaded through `src/utils/config_parser.py`. |

### Documentation

| ▸ | Every public function, class, and module has a docstring. |
|---|---|
| ▸ | Docstrings follow Google style. |
| ▸ | Security-relevant code includes an inline comment explaining *why* a particular control exists, not just what it does. |
| ▸ | Complex algorithms link to a reference (paper, RFC, blog post). |
| ▸ | User-facing changes are reflected in `docs/`. |

Example docstring:

```python
def verify_api_key(provided: str | None, expected: str) -> bool:
    """Verify an API key in constant time.

    Args:
        provided: The API key supplied by the caller, or None.
        expected: The API key configured for the service.

    Returns:
        True if the keys match, False otherwise.

    Notes:
        The comparison uses hmac.compare_digest over SHA-256 hashes to
        prevent timing side channels.
    """
```

### Dependencies

| ▸ | Add new dependencies sparingly. Every dependency is a potential security and maintenance burden. |
|---|---|
| ▸ | Pin exact versions in `requirements.txt` and `requirements-dev.txt`. |
| ▸ | Prefer libraries with active maintenance, permissive licenses, and low transitive dependency counts. |
| ▸ | New dependencies must pass `pip-audit` in CI. |

---

## Commit Message Convention

<img src="https://img.shields.io/badge/format-conventional%20commits-FE5196?style=flat-square&logo=conventionalcommits&logoColor=white" alt="Conventional Commits" />

This project uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
This produces a consistent, machine-readable history that supports automated
changelog generation and semantic versioning.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Badge | Type | Purpose |
|---|---|---|
| <img src="https://img.shields.io/badge/feat-2ea44f?style=flat-square" alt="feat" /> | `feat` | A new feature |
| <img src="https://img.shields.io/badge/fix-d73a4a?style=flat-square" alt="fix" /> | `fix` | A bug fix |
| <img src="https://img.shields.io/badge/docs-0075ca?style=flat-square" alt="docs" /> | `docs` | Documentation only |
| <img src="https://img.shields.io/badge/style-ededed?style=flat-square&logoColor=black" alt="style" /> | `style` | Formatting, whitespace, no logic change |
| <img src="https://img.shields.io/badge/refactor-fbca04?style=flat-square&logoColor=black" alt="refactor" /> | `refactor` | Code restructuring, no behavior change |
| <img src="https://img.shields.io/badge/perf-8B5CF6?style=flat-square" alt="perf" /> | `perf` | Performance improvement |
| <img src="https://img.shields.io/badge/test-0A9EDC?style=flat-square" alt="test" /> | `test` | Adding or refactoring tests |
| <img src="https://img.shields.io/badge/build-6D00CC?style=flat-square" alt="build" /> | `build` | Build system or dependency changes |
| <img src="https://img.shields.io/badge/ci-2088FF?style=flat-square&logo=github-actions&logoColor=white" alt="ci" /> | `ci` | CI configuration changes |
| <img src="https://img.shields.io/badge/chore-CCCCCC?style=flat-square&logoColor=black" alt="chore" /> | `chore` | Maintenance tasks |
| <img src="https://img.shields.io/badge/security-critical-red?style=flat-square&logo=shield&logoColor=white" alt="security" /> | `security` | Security fix (highest priority for review) |

### Scopes

Common scopes include `serving`, `training`, `data`, `eval`, `db`, `auth`,
`security`, `metrics`, `docs`, `deploy`, `ci`. Use the scope that best
identifies the affected subsystem.

### Subject

| ▸ | Use the imperative mood: "add feature", not "added feature" or "adds feature" |
|---|---|
| ▸ | Do not capitalize the first letter |
| ▸ | Do not end with a period |
| ▸ | Keep under 72 characters |

### Body

| ▸ | Explain *what* changed and *why*, not *how* |
|---|---|
| ▸ | Wrap at 72 characters |
| ▸ | Separate from subject with a blank line |

### Footer

| ▸ | Reference issues closed by this commit: `Closes #123` |
|---|---|
| ▸ | Mark breaking changes: `BREAKING CHANGE: <description>` |
| ▸ | Include co-author trailers for pair programming |

### Examples

Simple fix:

```
fix(security): reject prompts with malformed unicode escapes

Unicode escape sequences such as \u0000 were previously passed through
to the tokenizer, causing truncation. Strip them in sanitize_text
before tokenization.
```

Feature with a breaking change:

```
feat(serving): require API key on all generation endpoints

BREAKING CHANGE: /generate now requires an Authorization header. Deployments
that previously relied on anonymous access must configure API_KEY and update
clients.

Closes #142
```

---

## Testing Guidelines

<img src="https://img.shields.io/badge/coverage-minimum%2070%25-brightgreen?style=flat-square&logo=pytest&logoColor=white" alt="Coverage" />

### Running Tests

```bash
# Full suite with coverage
make test

# Coverage as HTML
make test-cov
open htmlcov/index.html

# A single file
pytest tests/test_security.py -v

# A single test
pytest tests/test_security.py::test_verify_api_key_ok -v

# Integration tests against a live server
BASE_URL=http://localhost:8000 pytest tests/integration -v

# GPU tests
RUN_GPU_TESTS=1 pytest tests/test_engine.py -v
```

### Writing Tests

| ▸ | Every bug fix must include a regression test. |
|---|---|
| ▸ | Every new feature must include unit tests and, if it touches an endpoint, integration tests. |
| ▸ | Use fixtures from `tests/conftest.py` for shared setup. |
| ▸ | Mock external services (Redis, Postgres, Hugging Face, W&B) rather than hitting them directly in unit tests. |
| ▸ | Mark slow tests with `@pytest.mark.slow`; mark GPU tests with `@pytest.mark.gpu`; mark integration tests with `@pytest.mark.integration`. |
| ▸ | Tests must be deterministic. Avoid wall-clock time, network access, and random seeds unless explicitly controlled. |
| ▸ | Aim for high coverage of security-critical code. Anything in `src/utils/security.py`, `src/utils/auth.py`, and `src/serving/middleware.py` should have near-complete coverage. |

### Test Structure

```python
def test_feature_does_expected_behavior() -> None:
    # Arrange
    ...

    # Act
    ...

    # Assert
    ...
```

Use descriptive test names that explain the invariant being checked.

---

## Review Process

<img src="https://img.shields.io/badge/review-required-orange?style=flat-square&logo=github&logoColor=white" alt="Review Required" />

### What Maintainers Look For

| # | Criterion | Description |
|---|---|---|
| 1 | Correctness | Does the change actually solve the problem? |
| 2 | Tests | Are the new behaviors covered by tests? |
| 3 | Security | Does the change introduce new attack surface? Are inputs validated? |
| 4 | Performance | Does it regress throughput or latency? |
| 5 | Backward compatibility | Does it break existing callers? If so, is a migration path provided? |
| 6 | Documentation | Is user-facing behavior documented? |
| 7 | Style | Does it follow the coding standards? |
| 8 | Scope | Is the change focused, or does it mix unrelated concerns? |

### CI Requirements

Every pull request must pass:

<p align="left">
  <img src="https://img.shields.io/badge/Ruff-passing-brightgreen?style=flat-square&logo=ruff&logoColor=black" alt="Ruff" />
  <img src="https://img.shields.io/badge/Black-passing-brightgreen?style=flat-square&logo=python&logoColor=white" alt="Black" />
  <img src="https://img.shields.io/badge/mypy-passing-brightgreen?style=flat-square&logo=python&logoColor=white" alt="mypy" />
  <img src="https://img.shields.io/badge/pytest-passing-brightgreen?style=flat-square&logo=pytest&logoColor=white" alt="pytest" />
  <img src="https://img.shields.io/badge/Coverage-70%25%2B-brightgreen?style=flat-square" alt="Coverage" />
  <img src="https://img.shields.io/badge/pip--audit-passing-brightgreen?style=flat-square&logo=pypi&logoColor=white" alt="pip-audit" />
  <img src="https://img.shields.io/badge/Bandit-passing-brightgreen?style=flat-square&logo=python&logoColor=white" alt="Bandit" />
  <img src="https://img.shields.io/badge/Gitleaks-passing-brightgreen?style=flat-square&logo=git&logoColor=white" alt="Gitleaks" />
</p>

### Approvals

| ▸ | At least one maintainer approval is required before merge. |
|---|---|
| ▸ | Changes to security-critical files require approval from a member of the `@llm-forge/security` team. |
| ▸ | Breaking changes require a `BREAKING CHANGE:` footer in the commit message and a migration note in the PR description. |

Security-critical files:

- `src/utils/security.py`
- `src/utils/auth.py`
- `src/serving/middleware.py`
- `src/serving/quota.py`
- anything under `deployment/`

### Response Times

Maintainers aim to respond to new PRs within two business days. If a PR has
been open for more than a week without response, feel free to ping the thread
politely.

---

## Security Vulnerabilities

<img src="https://img.shields.io/badge/security-do%20not%20open%20public%20issue-critical?style=flat-square&logo=shieldsdotio&logoColor=white" alt="Security" />

**Do not open a public issue for security vulnerabilities.**

If you believe you have found a security vulnerability in LLM-Forge, please
email us at:

**security@llmforge.dev**

Please include:

| ▸ | A clear description of the vulnerability |
|---|---|
| ▸ | Steps to reproduce |
| ▸ | The version of LLM-Forge affected |
| ▸ | Potential impact |
| ▸ | Any suggested mitigations |

We will acknowledge receipt within 48 hours and aim to provide a resolution
timeline within five business days.

A PGP key for encrypted reports is available at
`https://llmforge.dev/security.asc` (fingerprint: `ABCD EFGH IJKL MNOP QRST UVWX YZ01 2345`).

We will credit reporters in the changelog and release notes unless you prefer
to remain anonymous.

---

## Community

<img src="https://img.shields.io/badge/community-welcome-purple?style=flat-square&logo=discord&logoColor=white" alt="Community" />

### Communication Channels

| Platform | Channel | Purpose |
|---|---|---|
| <img src="https://img.shields.io/badge/GitHub%20Issues-d73a4a?style=flat-square&logo=github&logoColor=white" alt="Issues" /> | Issues | Bug reports and feature requests |
| <img src="https://img.shields.io/badge/GitHub%20Discussions-2ea44f?style=flat-square&logo=github&logoColor=white" alt="Discussions" /> | Discussions | Questions, design proposals, show and tell |
| <img src="https://img.shields.io/badge/Discord-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord" /> | `#llm-forge` | Real-time chat |
| <img src="https://img.shields.io/badge/Email-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email" /> | team@llmforge.dev | Direct contact |

### Recognition

Contributors are recognized in each release's changelog and in the project's
`CONTRIBUTORS.md` file. Significant contributions are acknowledged in the
release notes on GitHub.

### Maintainer Responsibilities

| ▸ | Responding to issues and PRs in a timely manner |
|---|---|
| ▸ | Reviewing changes with an eye toward long-term maintainability |
| ▸ | Keeping documentation in sync with code |
| ▸ | Communicating design decisions clearly |
| ▸ | Fostering a welcoming, respectful community |

---

## License

<img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square&logo=opensourceinitiative&logoColor=white" alt="License MIT" />

By contributing to LLM-Forge, you agree that your contributions will be
licensed under the MIT License. See [LICENSE](LICENSE) for the full text.

You confirm that:

| ▸ | You have the right to submit the contribution |
|---|---|
| ▸ | The contribution is your original work or is appropriately licensed |
| ▸ | Your contribution does not violate any third-party rights |

---

## Questions

<img src="https://img.shields.io/badge/questions-welcome-blue?style=flat-square&logo=github&logoColor=white" alt="Questions" />

If anything in this guide is unclear, or if you have a suggestion for how to
improve it, please open an issue or reach out to the maintainers. Thank you for
contributing to LLM-Forge.



**No emoji** — only shields.io badges and unicode `▸` bullets.

Bolo **"next"** toh `CHANGELOG.md` deta hoon.
