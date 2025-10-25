# Module 001: Python Fundamentals for Infrastructure - Comprehensive Quiz

## Overview

This quiz assesses your understanding of Python fundamentals for AI infrastructure, covering all three lectures and seven exercises from Module 001. The quiz includes multiple choice, true/false, code analysis, and scenario-based questions.

**Time Limit**: 60 minutes
**Total Questions**: 30
**Passing Score**: 75% (23/30 correct)

---

## Section 1: Python Environment and Package Management (Questions 1-5)

### Question 1: Virtual Environments

**Which command creates a new virtual environment named `ml_env` in Python?**

A) `python -m env ml_env`
B) `python -m venv ml_env`
C) `python create_env ml_env`
D) `pip install virtualenv ml_env`

**Answer**: B

**Explanation**: The correct command is `python -m venv ml_env`. The `venv` module is Python's built-in tool for creating virtual environments. Option A uses wrong module name, C isn't a valid command, and D is for installing virtualenv (a third-party tool), not creating an environment.

---

### Question 2: Dependency Management

**What is the purpose of freezing requirements with `pip freeze > requirements.txt`?**

A) To reduce the size of installed packages
B) To create an editable requirements file
C) To capture exact versions of all installed packages for reproducibility
D) To update all packages to their latest versions

**Answer**: C

**Explanation**: `pip freeze` creates a snapshot of all installed packages with their exact versions, ensuring reproducible environments. This captures both direct dependencies and transitive dependencies. It doesn't reduce size (A), create an editable file format (B), or update packages (D).

---

### Question 3: Type Hints

**What does this type hint indicate: `def train_model(config: Dict[str, Any]) -> Optional[Model]:`?**

A) The function requires a dictionary and always returns a Model
B) The function requires a dictionary and may return a Model or None
C) The function accepts any type and returns a dictionary
D) The function requires optional parameters and returns a Model

**Answer**: B

**Explanation**: `Dict[str, Any]` indicates the parameter must be a dictionary with string keys and values of any type. `Optional[Model]` (equivalent to `Union[Model, None]`) means the function may return a Model object or None. The function doesn't always return a Model (A), doesn't return a dictionary (C), and Optional applies to the return type, not parameters (D).

---

### Question 4: Environment Variables

**Which is the MOST secure way to handle database credentials in an ML application?**

A) Hard-code credentials directly in the script
B) Store credentials in a `.env` file and add it to `.gitignore`
C) Put credentials in `config.yaml` and commit to git
D) Store credentials in a Python module and import it

**Answer**: B

**Explanation**: Storing credentials in a `.env` file (excluded from git via `.gitignore`) is the most secure option listed. This keeps secrets out of version control while allowing different environments to have different credentials. Hard-coding (A) exposes secrets in code, committing to git (C) exposes secrets in version control, and importing from a Python module (D) still requires the credentials to be stored somewhere secure.

---

### Question 5: Package Installation

**What's the difference between `pip install pandas` and `pip install pandas==1.5.0`?**

A) The first installs the latest version, the second installs version 1.5.0
B) The first installs from PyPI, the second from a local file
C) There is no difference; both install the latest version
D) The first is for development, the second is for production

**Answer**: A

**Explanation**: Without version specification, pip installs the latest available version. With `==1.5.0`, it installs exactly that version. This version pinning is crucial for reproducibility in production environments. Both install from PyPI by default (B is incorrect), they behave differently (C is incorrect), and version pinning is important for both dev and prod (D is misleading).

---

## Section 2: Data Structures (Questions 6-10)

### Question 6: List Comprehension

**What does this code output? `result = [x**2 for x in range(5) if x % 2 == 0]`**

A) `[0, 1, 4, 9, 16]`
B) `[0, 4, 16]`
C) `[0, 2, 4]`
D) `[1, 9]`

**Answer**: B

**Explanation**: The comprehension squares numbers from 0-4 that are even. Even numbers in range(5) are 0, 2, and 4. Their squares are 0, 4, and 16. Option A includes all squares (missing the filter), C shows the even numbers themselves (not squared), and D shows odd number squares (wrong filter).

---

### Question 7: Dictionary Methods

**Given `config = {"lr": 0.001, "epochs": 100}`, what happens with `config.get("batch_size", 32)`?**

A) Raises a KeyError
B) Returns None
C) Returns 32
D) Adds "batch_size": 32 to the dictionary

**Answer**: C

**Explanation**: The `.get()` method returns the default value (32) when the key doesn't exist. This prevents KeyError exceptions. It doesn't raise an error (A), returns None only if no default is provided (B), and doesn't modify the dictionary (D) - use `.setdefault()` for that.

---

### Question 8: Set Operations

**What does this code do? `train_ids & test_ids`**

A) Combines all unique IDs from both sets
B) Finds IDs that appear in both sets (intersection)
C) Finds IDs only in train_ids
D) Removes test_ids from train_ids

**Answer**: B

**Explanation**: The `&` operator performs set intersection, returning elements common to both sets. This is crucial for detecting data leakage in ML train/test splits. Option A describes union (`|`), C describes difference (`-`), and D also describes difference in reverse.

---

### Question 9: Tuple Immutability

**Why would you use a tuple instead of a list for model configuration?**

A) Tuples are faster than lists
B) Tuples can store more data than lists
C) Tuples are immutable, preventing accidental modification
D) Tuples have more built-in methods than lists

**Answer**: C

**Explanation**: Tuples are immutable, making them ideal for configuration data that shouldn't change during execution. While tuples can be slightly faster for iteration (A), the main reason to choose them is immutability. They have the same storage capacity as lists (B), and actually have fewer methods than lists (D).

---

### Question 10: Nested Data Structures

**What's the output of `experiments["exp_001"]["metrics"]["accuracy"]` where experiments is properly initialized?**

```python
experiments = {
    "exp_001": {
        "model": "resnet",
        "metrics": {"accuracy": 0.92, "loss": 0.15}
    }
}
```

A) `{"accuracy": 0.92, "loss": 0.15}`
B) `0.92`
C) `"accuracy"`
D) KeyError

**Answer**: B

**Explanation**: This chain of dictionary accesses retrieves the nested value 0.92. First, it gets the "exp_001" dictionary, then the "metrics" dictionary inside it, then the "accuracy" value. Option A returns the entire metrics dict (missing final key access), C returns the string key itself (wrong syntax), and D would only occur if keys were misspelled.

---

## Section 3: Functions and Modules (Questions 11-15)

### Question 11: Function Arguments

**What's wrong with this function signature? `def train(data, epochs=10, batch_size, lr=0.001):`**

A) Nothing is wrong
B) Default arguments must come after non-default arguments
C) Too many parameters
D) Parameter names are too short

**Answer**: B

**Explanation**: In Python, parameters with default values must come after parameters without defaults. The correct order would be: `def train(data, batch_size, epochs=10, lr=0.001):`. This is a syntax requirement, not a style preference. A is incorrect, C and D are not syntax errors.

---

### Question 12: Type Hints with Multiple Types

**What does `Union[int, float, None]` mean?**

A) The value must be int, float, and None simultaneously
B) The value can be int, float, or None
C) The value is optional with default None
D) The value is always None

**Answer**: B

**Explanation**: `Union[int, float, None]` indicates the value can be any one of these types. This is equivalent to `Optional[Union[int, float]]`. A value can't be multiple types simultaneously (A), Optional specifically means Union with None (C is partially correct but not the full explanation), and D is completely wrong.

---

### Question 13: Decorators

**What does this decorator do?**

```python
@timing_decorator
def train_model():
    # training code
    pass
```

A) Makes the function run in parallel
B) Measures and logs the function execution time
C) Caches the function results
D) Validates function inputs

**Answer**: B

**Explanation**: A timing decorator typically measures how long a function takes to execute and logs or returns that information. The decorator name suggests timing functionality. Parallel execution (A), caching (C), and validation (D) would require different decorators with different names.

---

### Question 14: Module Imports

**What's the difference between `from ml_utils import metrics` and `from ml_utils.metrics import accuracy`?**

A) No difference, they're equivalent
B) First imports the metrics module, second imports the accuracy function
C) First is for production, second is for development
D) Second is faster

**Answer**: B

**Explanation**: The first imports the entire `metrics` module (you'd call `metrics.accuracy()`), while the second imports just the `accuracy` function (you'd call `accuracy()` directly). This affects namespace and how you reference the function. A is incorrect, C is arbitrary, and D isn't meaningfully true.

---

### Question 15: *args and **kwargs

**What does this function signature accept? `def log_metrics(*args, **kwargs):`**

A) Only positional arguments
B) Only keyword arguments
C) Any number of positional arguments and any number of keyword arguments
D) Exactly one argument of any type

**Answer**: C

**Explanation**: `*args` captures any number of positional arguments as a tuple, and `**kwargs` captures any number of keyword arguments as a dictionary. This makes the function extremely flexible. A and B are partially correct but incomplete, and D is completely wrong.

---

## Section 4: File I/O (Questions 16-20)

### Question 16: Context Managers

**Why use `with open(file, 'r') as f:` instead of `f = open(file, 'r')`?**

A) It's faster
B) It automatically closes the file, even if an error occurs
C) It allows reading binary files
D) It's required for large files

**Answer**: B

**Explanation**: Context managers (the `with` statement) ensure resources are properly cleaned up, even if exceptions occur. The file is automatically closed when the block exits. While this might have minor performance benefits (A), the main reason is proper resource management. File mode determines binary vs text (C), and neither approach is required for large files specifically (D).

---

### Question 17: JSON vs Pickle

**Which format should you use to save a trained ML model for long-term storage?**

A) JSON - it's more readable
B) CSV - it's more compatible
C) Pickle - it's native Python
D) A framework-specific format (like PyTorch's .pth or TensorFlow's SavedModel)

**Answer**: D

**Explanation**: Framework-specific formats are designed for model persistence and are the best practice. They handle model architecture, weights, and metadata properly. JSON (A) can't serialize complex Python objects, CSV (B) is for tabular data, and pickle (C) has compatibility and security issues across Python versions.

---

### Question 18: CSV Reading

**What's the advantage of `csv.DictReader` over `csv.reader`?**

A) It's faster
B) It can read larger files
C) It returns rows as dictionaries with column names as keys, improving readability
D) It can read files with missing values

**Answer**: C

**Explanation**: `DictReader` maps columns to their names from the header row, returning dictionaries instead of lists. This makes code more readable and maintainable (`row['accuracy']` vs `row[3]`). It's not necessarily faster (A), file size handling is similar (B), and both can handle missing values (D).

---

### Question 19: File Paths

**Why use `Path` from `pathlib` instead of string concatenation for file paths?**

A) It's faster
B) It handles OS-specific path separators automatically
C) It uses less memory
D) It's required by Python 3.10+

**Answer**: B

**Explanation**: `pathlib.Path` automatically handles differences between operating systems (forward slashes vs backslashes), provides useful methods (`.exists()`, `.glob()`), and makes path operations clearer. Minor speed differences (A) exist but aren't the main reason, memory usage (C) is similar, and it's not required but recommended (D).

---

### Question 20: YAML Configuration

**Why prefer YAML over JSON for configuration files?**

A) YAML is faster to parse
B) YAML supports comments and is more human-readable
C) YAML is more secure
D) YAML files are smaller

**Answer**: B

**Explanation**: YAML allows comments, has cleaner syntax (no quotes required for strings, no commas), and is generally more human-friendly for configuration files. JSON is actually often faster to parse (A), neither is inherently more secure (C), and file size is comparable (D). The human-readability and comments are the key advantages.

---

## Section 5: Error Handling (Questions 21-25)

### Question 21: Exception Handling

**What's printed by this code?**

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("A")
except Exception:
    print("B")
else:
    print("C")
finally:
    print("D")
```

A) A, D
B) B, D
C) C, D
D) Only D

**Answer**: A

**Explanation**: The ZeroDivisionError is caught, printing "A". The `else` block (C) only runs if no exception occurs. The `finally` block (D) always runs, so output is "A" then "D". Option B would occur with a different exception, C would occur with no exception, and D alone would only happen if exceptions weren't caught.

---

### Question 22: Custom Exceptions

**When should you create a custom exception class?**

A) Never, built-in exceptions are sufficient
B) For every function you write
C) When you need domain-specific error handling with additional context
D) Only for fatal errors

**Answer**: C

**Explanation**: Custom exceptions are useful when you need to add domain-specific information (like which model failed, at what epoch) or when you want to distinguish your application errors from system errors for targeted handling. A is too restrictive, B is excessive, and D is unnecessary - custom exceptions can represent any severity.

---

### Question 23: Context Managers for Resources

**What does this context manager ensure?**

```python
class GPUContext:
    def __enter__(self):
        allocate_gpu()
    def __exit__(self, exc_type, exc_val, exc_tb):
        release_gpu()
```

A) GPU is allocated and released even if errors occur
B) GPU operations run faster
C) Multiple GPUs can be used simultaneously
D) GPU memory is increased

**Answer**: A

**Explanation**: Context managers guarantee cleanup code (in `__exit__`) runs even if exceptions occur in the `with` block. This ensures GPU resources are properly released, preventing memory leaks. It doesn't affect speed (B), enable multi-GPU (C requires different implementation), or increase memory (D).

---

### Question 24: Retry Logic

**When implementing retry logic for model downloads, what should you consider?**

A) Retry immediately without delay
B) Use exponential backoff to avoid overwhelming servers
C) Retry indefinitely until success
D) Never retry, always fail immediately

**Answer**: B

**Explanation**: Exponential backoff (increasing delay between retries: 1s, 2s, 4s, etc.) prevents overwhelming servers and is respectful to rate limits. Immediate retries (A) can make problems worse, infinite retries (C) can hang applications, and never retrying (D) reduces resilience.

---

### Question 25: Error Logging

**What information should be logged when an ML pipeline fails?**

A) Only the error message
B) Error message, timestamp, affected data/models, and stack trace
C) Nothing, to keep logs clean
D) Only the function name where it failed

**Answer**: B

**Explanation**: Comprehensive logging should include: what happened (error message), when (timestamp), where (stack trace), and what was affected (data/model identifiers). This enables effective debugging. A, C, and D all provide insufficient information for troubleshooting complex ML pipelines.

---

## Section 6: Async Programming (Questions 26-28)

### Question 26: Async vs Sync

**When is async programming MOST beneficial for ML workflows?**

A) Training a single model on GPU
B) Performing CPU-intensive matrix calculations
C) Downloading multiple datasets from remote storage concurrently
D) Running a for loop over training samples

**Answer**: C

**Explanation**: Async shines for I/O-bound operations like network requests or file I/O where you're waiting for external resources. Downloading multiple datasets concurrently can dramatically reduce total time. GPU training (A) and CPU calculations (B) are CPU-bound (better suited to multiprocessing), and simple loops (D) don't benefit from async unless they contain I/O operations.

---

### Question 27: Async Syntax

**What's wrong with this code?**

```python
async def process_data():
    data = load_data()  # load_data is async
    return data
```

A) Nothing is wrong
B) Missing `await` before `load_data()`
C) Should use `async with` instead
D) The function should not be async

**Answer**: B

**Explanation**: When calling an async function, you must use `await`: `data = await load_data()`. Without `await`, you get a coroutine object instead of the result. A is incorrect, C would be for async context managers, and D is incorrect because the function contains async operations.

---

### Question 28: Asyncio.gather()

**What does `await asyncio.gather(task1, task2, task3)` do?**

A) Runs tasks sequentially and returns results
B) Runs tasks concurrently and returns results when all complete
C) Runs only the fastest task
D) Runs tasks and returns the first result

**Answer**: B

**Explanation**: `asyncio.gather()` runs multiple coroutines concurrently and waits for all to complete, returning results in the same order as the input tasks. It doesn't run sequentially (A), doesn't pick the fastest (C), and waits for all, not just the first (D - that's `asyncio.wait()` with FIRST_COMPLETED).

---

## Section 7: Testing (Questions 29-30)

### Question 29: Pytest Fixtures

**What's the purpose of pytest fixtures?**

A) To fix broken tests automatically
B) To provide reusable test data and setup code
C) To make tests run faster
D) To mock all external dependencies

**Answer**: B

**Explanation**: Fixtures provide reusable setup code and test data that can be shared across multiple tests. They handle setup and teardown, reducing code duplication. They don't fix broken tests (A), don't necessarily speed up tests though they can help (C), and don't automatically mock dependencies (D) - that's a separate feature.

---

### Question 30: Test Coverage

**You have 85% test coverage. What does this mean?**

A) 85% of your tests pass
B) 85% of your code is executed by tests
C) Your code is 85% correct
D) You need to write 15% more tests

**Answer**: B

**Explanation**: Test coverage measures what percentage of your code (lines, branches, functions) is executed when tests run. 85% coverage means 15% of code isn't tested. It doesn't measure pass rate (A), doesn't guarantee correctness (C - even 100% coverage can have bugs), and D is oversimplified - you need tests for the untested code, but quantity matters less than quality.

---

## Bonus Question 31: Practical Application

**You're building an ML inference service. Which combination of Python concepts is MOST important?**

A) Virtual environments, lists, and print statements
B) Type hints, async programming, error handling, and testing
C) List comprehensions and for loops
D) Only numpy and pandas knowledge

**Answer**: B

**Explanation**: Production inference services need:
- **Type hints**: Clear interfaces and IDE support
- **Async programming**: Handle multiple concurrent requests efficiently
- **Error handling**: Graceful degradation when models fail
- **Testing**: Ensure reliability

While A, C, and D contain useful elements, B represents the core professional infrastructure skills needed for production systems.

---

## Bonus Question 32: Debugging Scenario

**Your ML pipeline intermittently fails with "Connection refused" when loading data from S3. What's the BEST fix?**

A) Ignore the error and continue
B) Implement retry logic with exponential backoff
C) Restart the pipeline manually when it fails
D) Switch to loading from local disk

**Answer**: B

**Explanation**: Transient network issues are common. Retry logic with exponential backoff handles temporary failures gracefully while respecting server resources. A loses data, C isn't automated, and D might not be feasible (data might only be in S3) and doesn't address the root cause of network reliability.

---

## Answer Key Summary

1. B - Virtual environment creation
2. C - Freezing requirements
3. B - Optional return type
4. B - Secure credential storage
5. A - Version pinning
6. B - List comprehension with filter
7. C - Dictionary .get() method
8. B - Set intersection
9. C - Tuple immutability
10. B - Nested dictionary access
11. B - Default argument order
12. B - Union type hints
13. B - Timing decorator
14. B - Import specificity
15. C - Variable arguments
16. B - Context manager cleanup
17. D - Model storage format
18. C - DictReader advantages
19. B - Path handling
20. B - YAML vs JSON
21. A - Exception flow control
22. C - Custom exceptions
23. A - Resource management
24. B - Retry strategies
25. B - Error logging
26. C - Async use cases
27. B - Await keyword
28. B - Asyncio.gather
29. B - Pytest fixtures
30. B - Test coverage meaning
31. B - Production concepts (Bonus)
32. B - Network resilience (Bonus)

---

## Scoring Guide

- **27-30+ correct (90-100%)**: Excellent! You have strong Python fundamentals for AI infrastructure
- **23-26 correct (75-89%)**: Good! Review the topics you missed
- **18-22 correct (60-74%)**: Passing, but review key concepts before moving to Module 002
- **Below 18 (< 60%)**: Review Module 001 lectures and exercises before proceeding

---

## Review Recommendations

**If you scored below 75%**, focus on:

1. **Environment Management**: Re-do Exercise 01
2. **Data Structures**: Practice Exercise 02 problems
3. **Error Handling**: Review Lecture 03 and Exercise 05
4. **Async Programming**: Complete Exercise 06 examples
5. **Testing**: Work through Exercise 07 systematically

**Next Steps:**
- Review incorrect answers and explanations
- Complete any exercises you skipped
- Build a small project combining these concepts
- Proceed to Module 002: Linux Essentials

---

**Module Completed**: Ready for Module 002 when scoring 75%+
**Time to Review**: Estimated 2-4 hours for concepts needing reinforcement
**Practice Projects**: Build a tested async ML utility library

Good luck! These fundamentals are critical for success as an AI Infrastructure Engineer.
