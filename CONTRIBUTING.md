# Contributing to TalentScout Hiring Assistant

Thank you for your interest in contributing to TalentScout Hiring Assistant! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a branch for your changes
4. Make your changes
5. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Virtual environment (venv)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/talentscout-hiring-assistant.git
cd talentscout-hiring-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov

# Run tests to verify setup
pytest tests/ -v
```

## How to Contribute

### Types of Contributions

- **Bug fixes**: Fix issues in existing code
- **New features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Translations**: Add support for new languages
- **UI improvements**: Enhance the user interface

### Branch Naming

Use descriptive branch names:

- `feature/add-voice-input` - New feature
- `fix/dark-mode-header` - Bug fix
- `docs/update-readme` - Documentation
- `test/add-llm-tests` - Testing
- `refactor/cleanup-state-manager` - Code refactoring

## Coding Standards

### Python Style Guide

Follow PEP 8 guidelines:

```python
# Good
def process_candidate_info(name: str, email: str) -> dict:
    """
    Process candidate information.
    
    Args:
        name: Candidate's full name
        email: Candidate's email address
    
    Returns:
        Dictionary containing processed information
    """
    return {"name": name, "email": email}
```

### Code Organization

```
src/
├── llm/           # LLM-related code
├── components/    # Business logic components
├── ui/            # UI components
├── prompts/       # Prompt templates
├── i18n/          # Internationalization
└── utils/         # Utility functions
```

### Type Hints

Use type hints for all function parameters and return values:

```python
from typing import Dict, List, Optional

def analyze_sentiment(text: str) -> Dict[str, float]:
    """Analyze sentiment of text."""
    pass

def get_questions(tech_stack: List[str], count: Optional[int] = 3) -> List[str]:
    """Generate technical questions."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def generate_response(prompt: str, model: str = "gpt-4o") -> str:
    """
    Generate a response using the specified LLM.
    
    Args:
        prompt: The input prompt for the LLM
        model: The model to use (default: "gpt-4o")
    
    Returns:
        The generated response string
    
    Raises:
        ValueError: If prompt is empty
        LLMError: If LLM fails to generate response
    
    Example:
        >>> response = generate_response("Hello, world!")
        >>> print(response)
        "Hello! How can I help you today?"
    """
    pass
```

### Testing

Write tests for all new features:

```python
# tests/test_new_feature.py
import pytest
from src.module import function

class TestNewFeature:
    """Tests for new feature."""
    
    def test_function_with_valid_input(self):
        """Test function with valid input."""
        result = function("valid_input")
        assert result == "expected_output"
    
    def test_function_with_invalid_input(self):
        """Test function raises error with invalid input."""
        with pytest.raises(ValueError):
            function("invalid_input")
```

## Commit Guidelines

### Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

### Examples

```
feat(i18n): Add Japanese language support

- Add translations for Japanese
- Update language selector
- Add tests for Japanese translations

Closes #42
```

```
fix(ui): Fix dark mode header background

The header was showing white in dark mode due to CSS specificity issues.
Added proper CSS class and theme-aware colors.

Fixes #38
```

## Pull Request Process

### Before Submitting

1. **Update from main**: Ensure your branch is up to date
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run tests**: All tests must pass
   ```bash
   pytest tests/ -v
   ```

3. **Check code style**: Ensure code follows style guidelines

4. **Update documentation**: Update docs if needed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests passing

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

### Review Process

1. Submit PR
2. Automated tests run
3. Code review by maintainer
4. Address feedback
5. Approval and merge

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try to reproduce the bug
3. Test with latest version

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Screenshots
If applicable

## Environment
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.11.0]
- Streamlit version: [e.g., 1.28.0]
- Browser: [e.g., Chrome 119]

## Additional Context
Any other relevant information
```

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered

## Additional Context
Any other relevant information
```

## Questions?

If you have questions, feel free to:

1. Open an issue with the "question" label
2. Comment on existing issues
3. Reach out to the maintainers

---

Thank you for contributing to TalentScout Hiring Assistant! 🎉
