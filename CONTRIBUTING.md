# Contributing to AI Infrastructure Junior Engineer Learning Repository

Thank you for your interest in contributing to the AI Infrastructure Curriculum! This repository is designed to help aspiring AI Infrastructure Engineers learn the foundational skills needed to start their careers. Your contributions help make this learning resource better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Style Guides](#style-guides)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to ai-infra-curriculum@joshua-ferguson.com.

## How Can I Contribute?

### Reporting Bugs or Issues

If you find a bug in the code, documentation, or learning materials:

1. **Check existing issues** to see if it's already been reported
2. If not, **create a new issue** using our bug report template
3. Include:
   - Clear, descriptive title
   - Steps to reproduce the issue
   - Expected behavior vs. actual behavior
   - Your environment (OS, Python version, etc.)
   - Screenshots or error messages if applicable

### Suggesting Enhancements

Have an idea to improve the learning experience?

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** using our feature request template
3. Clearly describe:
   - The problem or gap you've identified
   - Your proposed solution
   - Why this would benefit learners
   - Any alternative solutions you've considered

### Improving Documentation

Documentation improvements are always welcome! This includes:

- Fixing typos or grammatical errors
- Clarifying confusing explanations
- Adding examples or diagrams
- Improving code comments
- Expanding the README or guides

For small fixes (typos, grammar), feel free to submit a PR directly. For larger changes, please open an issue first to discuss.

### Contributing Code or Exercises

We welcome contributions of:

- Bug fixes to existing code stubs
- Improvements to exercise clarity
- Additional test cases
- Better code examples
- New resources or references

**Important**: This is a **learning repository**. Code stubs should remain incomplete with clear TODOs. Do not submit complete solutions to this repository (those belong in the solutions repository).

### Improving Learning Materials

Help make the lessons better by:

- Clarifying difficult concepts
- Adding real-world examples
- Creating diagrams or visualizations
- Suggesting additional resources
- Improving exercise instructions
- Adding practice problems

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- GitHub account
- Basic understanding of AI/ML concepts (or willingness to learn!)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ai-infra-junior-engineer-learning.git
   cd ai-infra-junior-engineer-learning
   ```

3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/ai-infra-curriculum/ai-infra-junior-engineer-learning.git
   ```

4. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

6. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Running Tests

Before submitting changes, ensure all tests pass:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_specific.py
```

### Code Quality Checks

We use several tools to maintain code quality:

```bash
# Format code with black
black .

# Sort imports
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .

# Or run all checks at once with pre-commit
pre-commit run --all-files
```

## Contribution Guidelines

### General Principles

1. **Keep it Educational**: Remember this is a learning resource. Code should be clear and well-commented.

2. **Maintain Difficulty Level**: This is the Junior Engineer repository. Keep complexity appropriate for beginners.

3. **Follow Existing Patterns**: Match the style and structure of existing content.

4. **Test Your Changes**: Ensure code works and tests pass.

5. **Document Everything**: Clear explanations help learners understand.

### What Makes a Good Contribution?

Good contributions are:

- **Clear and focused**: One logical change per PR
- **Well-tested**: Include or update tests as needed
- **Well-documented**: Explain what changed and why
- **Pedagogically sound**: Helps learners understand concepts
- **Accessible**: Uses clear language and explains jargon
- **Complete**: Includes all necessary files and updates

### What We're NOT Looking For

Please avoid:

- Complete solutions to exercises (use the solutions repo instead)
- Advanced topics beyond junior engineer scope
- Large refactors without prior discussion
- Changes that break existing functionality
- Poorly documented or tested code
- Plagiarized content

## Pull Request Process

### Before You Submit

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Keep your fork updated**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

3. **Make your changes** following our guidelines

4. **Run tests and quality checks**:
   ```bash
   pytest
   black .
   flake8 .
   mypy .
   ```

5. **Commit your changes** with clear messages:
   ```bash
   git add .
   git commit -m "feat: add exercise for model deployment"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new features or exercises
   - `fix:` bug fixes
   - `docs:` documentation changes
   - `test:` adding or updating tests
   - `refactor:` code refactoring
   - `style:` formatting changes
   - `chore:` maintenance tasks

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Submitting Your PR

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template completely
5. Link any related issues
6. Submit the PR

### PR Review Process

1. **Automated checks** will run (tests, linting, etc.)
2. **Maintainers will review** your code (usually within 3-5 days)
3. **Address feedback** by pushing new commits to your branch
4. Once approved, a maintainer will **merge your PR**

### After Your PR is Merged

1. **Delete your branch**:
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update your fork**:
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

3. **Celebrate!** You've contributed to open source education!

## Style Guides

### Python Code Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting (line length: 88)
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Add type hints using Python 3.11+ syntax
- Write docstrings in [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

Example:

```python
from typing import List, Optional


def process_model_data(
    data: List[float],
    normalize: bool = True,
    scaling_factor: Optional[float] = None,
) -> List[float]:
    """Process model input data with optional normalization.

    Args:
        data: Input data points to process
        normalize: Whether to normalize the data
        scaling_factor: Optional scaling factor to apply

    Returns:
        Processed data ready for model inference

    Raises:
        ValueError: If data is empty or scaling_factor is negative
    """
    # TODO: Implement data processing logic
    pass
```

### Documentation Style

- Use clear, simple language
- Define technical terms when first used
- Include code examples
- Use diagrams where helpful
- Keep paragraphs short and scannable
- Use headers to organize content

### Markdown Style

- Use ATX-style headers (`#` not underlines)
- One blank line before and after headers
- Use fenced code blocks with language specification
- Keep line length reasonable (80-100 characters)
- Use relative links for internal references

### Commit Message Style

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): brief description

Longer explanation if needed. Wrap at 72 characters.

- Bullet points are okay
- Use present tense: "add" not "added"
- Reference issues: "fixes #123"

BREAKING CHANGE: description of breaking change if applicable
```

Types:
- `feat`: New feature or exercise
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test changes
- `refactor`: Code refactoring
- `style`: Formatting changes
- `chore`: Maintenance

### Exercise and Lesson Guidelines

When creating or modifying exercises:

1. **Clear Learning Objective**: State what the learner will accomplish
2. **Prerequisites**: List required knowledge or completed lessons
3. **Step-by-Step Instructions**: Break complex tasks into manageable steps
4. **Expected Outcomes**: Describe what success looks like
5. **Common Pitfalls**: Warn about typical mistakes
6. **Resources**: Link to relevant documentation or tutorials
7. **Estimated Time**: Give realistic time expectations

Example structure:

```markdown
## Exercise: Deploy Your First Model

**Learning Objective**: Deploy a trained scikit-learn model using FastAPI

**Prerequisites**:
- Completed Lesson 03: Model Training
- Basic understanding of REST APIs
- Python 3.11+ installed

**Estimated Time**: 45 minutes

### Instructions

1. **Set up FastAPI application**
   ```python
   # TODO: Import required libraries
   # TODO: Create FastAPI app instance
   ```

2. **Load the trained model**
   - Model file is located at `models/classifier.pkl`
   - Use joblib to load the model

   [Continue with detailed steps...]

### Expected Outcome

You should have a running API that:
- Accepts POST requests with feature data
- Returns predictions in JSON format
- Handles errors gracefully

### Common Pitfalls

- **Model loading errors**: Ensure pickle compatibility
- **Port conflicts**: Check if port 8000 is already in use
- **Data validation**: Use Pydantic for input validation

### Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Model Serialization Guide](link)
```

## Community

### Getting Help

- **Issues**: Browse existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Email**: ai-infra-curriculum@joshua-ferguson.com

### Recognition

Contributors will be:
- Listed in our Contributors section
- Credited in release notes
- Mentioned in our community highlights

### Staying Connected

- Watch the repository for updates
- Star the repo to show support
- Share your learning journey on social media with `#AIInfraCurriculum`

## Questions?

Don't hesitate to ask! We're here to help:

- Open a GitHub Discussion
- Comment on relevant issues
- Email us at ai-infra-curriculum@joshua-ferguson.com

Thank you for helping make AI Infrastructure education better for everyone!

---

**Remember**: This is a learning community. We value patience, kindness, and the desire to help others succeed. Every contribution, no matter how small, makes a difference.
