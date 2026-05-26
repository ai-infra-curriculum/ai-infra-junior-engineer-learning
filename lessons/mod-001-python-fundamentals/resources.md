# Module 001 — Python Fundamentals Resources

## Official documentation

- **Python documentation** — [docs.python.org](https://docs.python.org/3/). The authoritative reference. Bookmark the tutorial and the standard library index.
- **PEP 8 — Style Guide for Python Code** — [peps.python.org/pep-0008](https://peps.python.org/pep-0008/). Read it once; refer back often.
- **PEP 20 — The Zen of Python** — [peps.python.org/pep-0020](https://peps.python.org/pep-0020/). Short, worth re-reading periodically.

## Books

### Beginner / intermediate

- **Fluent Python (2nd ed.)** by Luciano Ramalho. The standard Pythonic-idioms reference. Covers the parts of the language that distinguish "Python written by a Java engineer" from "Python written by a Python engineer."
- **Effective Python (2nd ed.)** by Brett Slatkin. 90 specific items of best practice. Excellent companion to Fluent Python.
- **Python Crash Course** by Eric Matthes. Friendly introduction if you're new to programming overall.

### For ML engineers specifically

- **Python for Data Analysis (3rd ed.)** by Wes McKinney (creator of pandas). The reference for the NumPy/pandas data layer.
- **Designing Machine Learning Systems** by Chip Huyen. Not Python-specific but the canonical ML systems text — useful framing for why this module's skills matter.

## Online courses

- **Real Python** — [realpython.com](https://realpython.com/). High-quality tutorials across all levels. Worth the subscription.
- **MIT 6.0001 / 6.0002 Introduction to Computer Science with Python** — free on MIT OpenCourseWare. The most thorough free intro available.
- **CS50P (Harvard's Introduction to Programming with Python)** — [cs50.harvard.edu/python](https://cs50.harvard.edu/python/). Free, well-paced.

## Modern Python tooling

- **uv** — [astral.sh/uv](https://docs.astral.sh/uv/). Fast (10-100x) replacement for pip/pip-tools/virtualenv. Use this for new projects.
- **ruff** — [docs.astral.sh/ruff](https://docs.astral.sh/ruff/). Fast linter + formatter, drop-in replacement for black + flake8 + isort.
- **mypy** — [mypy.readthedocs.io](https://mypy.readthedocs.io/). Static type checker. Add to your CI.
- **pytest** — [docs.pytest.org](https://docs.pytest.org/). The de facto Python testing framework.

## ML-specific Python references

- **NumPy documentation** — [numpy.org/doc](https://numpy.org/doc/stable/). The substrate for every ML library.
- **pandas documentation** — [pandas.pydata.org/docs](https://pandas.pydata.org/docs/). DataFrames + Series, the working surface for tabular ML.
- **PyTorch tutorials** — [pytorch.org/tutorials](https://pytorch.org/tutorials/). Used in later modules.

## Anti-patterns to avoid

- Reaching for inheritance when composition fits better.
- Using `requests` (sync) in async code.
- Writing classes for everything when functions would do.
- Catching bare `except:` clauses (catch specific exceptions).
- `from X import *` (loses traceability).

## Community + practice

- **/r/learnpython** — [reddit.com/r/learnpython](https://www.reddit.com/r/learnpython/). Beginner-friendly questions welcome.
- **Stack Overflow** — `[python]` tag. Curated answers.
- **PyCon** — annual conference; many talks freely posted to YouTube.
- **Python Bytes podcast** — [pythonbytes.fm](https://pythonbytes.fm/). Weekly news + libraries.

## Cross-references in this curriculum

- Module 003 (Git) — version-control your Python code.
- Module 004 (ML Basics) — applies Python to ML workloads.
- Engineer track's mod-101 — production Python patterns at depth.
