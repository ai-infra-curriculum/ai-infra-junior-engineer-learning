# Module 001: Python Fundamentals for AI Infrastructure

## Module Overview

Welcome to the foundational module for Python programming in AI Infrastructure! This module is specifically designed to equip you with the Python skills needed to build, deploy, and manage AI/ML systems in production environments.

Unlike general Python courses, this curriculum focuses on the intersection of Python programming and infrastructure engineering - teaching you not just how to write Python code, but how to write production-grade infrastructure code that supports machine learning workloads.

## Why Python for AI Infrastructure?

Python has become the lingua franca of AI/ML infrastructure for several compelling reasons:

1. **ML Framework Ecosystem**: TensorFlow, PyTorch, scikit-learn, and virtually all major ML frameworks use Python as their primary interface
2. **Infrastructure Tooling**: Tools like Airflow, MLflow, Kubeflow, and Ray are all Python-based
3. **Automation & Orchestration**: Python excels at scripting, automation, and orchestrating complex workflows
4. **Cloud SDK Support**: Every major cloud provider offers comprehensive Python SDKs
5. **Data Processing**: Libraries like pandas, numpy, and dask make data manipulation straightforward
6. **Community & Resources**: Massive ecosystem with solutions for virtually any infrastructure challenge

## Learning Objectives

By the end of this module, you will be able to:

### Core Python Competencies
- Set up and manage isolated Python environments using venv and virtualenv
- Manage dependencies with pip, requirements.txt, and understand dependency resolution
- Write type-annotated Python code using modern type hints (PEP 484, 585, 604)
- Implement comprehensive logging strategies for production systems
- Handle configuration management for applications across multiple environments
- Work with file systems, subprocess calls, and system-level operations
- Build command-line interfaces (CLIs) using argparse and modern alternatives

### Infrastructure-Specific Skills
- Write Python scripts that orchestrate infrastructure operations
- Implement error handling and retry logic for distributed systems
- Use Python for monitoring data collection and metric aggregation
- Parse and generate configuration files (YAML, JSON, TOML)
- Interact with REST APIs using requests and httpx
- Implement concurrent operations using threading, multiprocessing, and asyncio
- Write testable, maintainable infrastructure code

### Professional Development Practices
- Write comprehensive unit tests using pytest
- Implement code quality checks with linters (pylint, flake8, ruff)
- Format code consistently using black and isort
- Generate and maintain documentation with docstrings and type hints
- Debug Python applications using pdb and logging
- Profile Python code to identify performance bottlenecks

## Module Structure

This module is organized into four comprehensive lectures, each building upon the previous:

### Lecture 01: Python Environment & Dependency Management (Week 1)
**Duration**: 6-8 hours
- Virtual environments and isolation
- Package management with pip
- Requirements files and lock files
- Python version management with pyenv
- Setting up development environments

### Lecture 02: Advanced Python for Infrastructure (Week 2)
**Duration**: 8-10 hours
- Type hints and static type checking
- Logging best practices for production systems
- Configuration management patterns
- Working with different data formats
- Error handling and exception strategies

### Lecture 03: Python for DevOps Operations (Week 3)
**Duration**: 8-10 hours
- Subprocess management and shell interaction
- File and directory operations
- Building CLI tools with argparse
- Working with environment variables
- Parsing command-line arguments

### Lecture 04: Testing and Code Quality (Week 4)
**Duration**: 8-10 hours
- Unit testing with pytest
- Test fixtures and parametrization
- Mocking and patching in tests
- Code coverage analysis
- Linting and formatting tools
- Pre-commit hooks and automation

## Prerequisites

### Required Knowledge
- Basic programming concepts (variables, loops, conditionals, functions)
- Familiarity with command-line interfaces
- Basic understanding of software development concepts
- Access to a Linux/Unix environment (WSL on Windows is acceptable)

### Recommended Background
- Some exposure to Python (even tutorial-level)
- Basic understanding of how applications use libraries
- Awareness of version control concepts (covered in Module 003)

### Technical Requirements
- Computer with at least 8GB RAM
- Python 3.11 or later installed
- Text editor or IDE (VS Code, PyCharm, or vim)
- Terminal/shell access
- Internet connection for package downloads

## Learning Timeline

### Week 1: Environment Setup & Fundamentals
- **Day 1-2**: Lecture 01 (Python Environment)
- **Day 3**: Exercise 01 (Environment Setup)
- **Day 4**: Practice and exploration
- **Day 5**: Module 001 Quiz (sections 1-2)

### Week 2: Advanced Patterns
- **Day 1-2**: Lecture 02 (Advanced Python)
- **Day 3**: Exercise 02 (Type Hints)
- **Day 4**: Exercise 03 (Logging)
- **Day 5**: Review and practice

### Week 3: DevOps Operations
- **Day 1-2**: Lecture 03 (Python DevOps)
- **Day 3-4**: Practice exercises
- **Day 5**: Integration practice

### Week 4: Quality & Testing
- **Day 1-2**: Lecture 04 (Testing & Quality)
- **Day 3-4**: Practice and project work
- **Day 5**: Complete module assessment

**Total Estimated Time**: 30-40 hours

## Topics Covered

### 1. Python Environment Management
- Virtual environment creation and activation
- Understanding site-packages and Python paths
- Managing multiple Python versions
- Dependency isolation strategies
- Reproducible environment creation

### 2. Package & Dependency Management
- Using pip effectively
- Requirements.txt best practices
- Understanding semantic versioning
- Lock files and deterministic builds
- Private package repositories

### 3. Type Hints & Static Typing
- Basic type annotations (str, int, float, bool)
- Complex types (List, Dict, Optional, Union)
- Type aliases and custom types
- Generic types and protocols
- Using mypy for type checking

### 4. Logging for Production Systems
- Python logging module architecture
- Log levels and when to use them
- Structured logging with JSON
- Log formatters and handlers
- Centralized logging considerations

### 5. Configuration Management
- Configuration file formats (YAML, JSON, TOML, .env)
- Environment-specific configurations
- Configuration validation
- Secrets management basics
- Configuration precedence patterns

### 6. File & System Operations
- Path manipulation with pathlib
- Reading and writing files safely
- Directory traversal and manipulation
- File permissions and attributes
- Temporary files and cleanup

### 7. Subprocess & Shell Integration
- Running external commands safely
- Capturing stdout and stderr
- Error handling for subprocess calls
- Streaming output from long-running processes
- Shell vs direct command execution

### 8. Building CLI Tools
- Argument parsing with argparse
- Subcommands and nested parsers
- Input validation
- Help text and documentation
- Interactive prompts

### 9. Testing with pytest
- Writing effective unit tests
- Test organization and discovery
- Fixtures for setup and teardown
- Parametrized tests for multiple scenarios
- Test coverage measurement

### 10. Code Quality & Tooling
- Linting with pylint, flake8, and ruff
- Automatic formatting with black
- Import sorting with isort
- Type checking with mypy
- Pre-commit hooks for automation

## Exercises

### Exercise 01: Environment Setup & Management
**Difficulty**: Beginner
**Duration**: 2-3 hours

Create a complete Python project with proper environment management, including:
- Virtual environment setup
- Requirements file with pinned versions
- Development vs production dependencies
- Environment activation scripts
- README with setup instructions

### Exercise 02: Type Hints Implementation
**Difficulty**: Intermediate
**Duration**: 2-3 hours

Take a provided untyped Python module and add comprehensive type hints:
- Function signatures with input/output types
- Complex nested types
- Type aliases for readability
- Pass mypy strict mode checks
- Document type design decisions

### Exercise 03: Logging Implementation
**Difficulty**: Intermediate
**Duration**: 3-4 hours

Implement a comprehensive logging strategy for a multi-module application:
- Configure root and module-level loggers
- Implement structured JSON logging
- Add context to log messages
- Configure file and console handlers
- Implement log rotation

## Quizzes & Assessments

### Module 001 Quiz
**Format**: 20 multiple-choice and short-answer questions
**Duration**: 30-45 minutes
**Passing Score**: 80% (16/20 correct)

**Topics Covered**:
- Virtual environment concepts (4 questions)
- Package management (3 questions)
- Type hints syntax and usage (4 questions)
- Logging best practices (3 questions)
- Testing fundamentals (3 questions)
- Code quality tools (3 questions)

### Practical Assessment
After completing all exercises, you'll work on a capstone project that combines all module topics:
- Build a CLI tool for managing ML model deployments
- Implement proper logging and error handling
- Include comprehensive type hints
- Write unit tests with 80%+ coverage
- Follow code quality standards

## Resources

### Official Documentation
- [Python Official Documentation](https://docs.python.org/3/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)

### Recommended Reading
- See `resources/recommended-reading.md` for curated articles and books
- Python Enhancement Proposals (PEPs) for language features
- Real Python tutorials for practical examples

### Tools & Libraries
- **Environment Management**: venv, virtualenv, pyenv, poetry
- **Testing**: pytest, pytest-cov, pytest-mock
- **Code Quality**: black, isort, flake8, pylint, ruff, mypy
- **CLI Development**: argparse, click, typer
- **Configuration**: pyyaml, python-dotenv, pydantic

## Success Criteria

You will have successfully completed this module when you can:

✅ Create and manage virtual environments without looking up commands
✅ Write requirements.txt files that ensure reproducible builds
✅ Add type hints to any Python function or class
✅ Implement logging that helps debug production issues
✅ Build CLI tools that handle edge cases gracefully
✅ Write unit tests that actually catch bugs
✅ Run linters and formatters as part of your normal workflow
✅ Debug Python code efficiently using logs and debugging tools
✅ Handle configuration for multiple environments (dev, staging, prod)
✅ Score 80% or higher on the module quiz

## Connection to AI Infrastructure

Everything in this module directly supports AI infrastructure work:

- **Environment Management**: Ensures ML models run with correct dependency versions
- **Type Hints**: Makes complex ML pipeline code maintainable
- **Logging**: Critical for debugging model serving issues in production
- **Configuration**: Manages hyperparameters and environment-specific settings
- **Subprocess Calls**: Interacts with training jobs and infrastructure tools
- **Testing**: Validates infrastructure code before deployment
- **CLI Tools**: Builds utilities for model deployment and management

## What's Next?

After completing this module, you'll move on to:
- **Module 002**: Linux Essentials for AI Infrastructure
- **Module 003**: Git & Version Control
- **Module 004**: Machine Learning Basics

The Python skills you develop here will be used extensively in all subsequent modules and projects.

## Getting Help

### During the Module
- Review lecture notes multiple times
- Complete all exercises, even if challenging
- Experiment with code examples
- Read error messages carefully
- Use Python's built-in help() function

### External Resources
- Python community forums and Stack Overflow
- Python Discord servers and communities
- Documentation for specific libraries
- GitHub repositories with example code

### Office Hours & Support
- Refer to the main repository README for community support options
- Create GitHub issues for content questions
- Join discussion forums for peer learning

---

**Module Version**: 1.0
**Last Updated**: October 2025
**Estimated Completion Time**: 30-40 hours
**Difficulty Level**: Beginner to Intermediate

**Ready to begin?** Start with `lecture-notes/01-python-environment.md`
