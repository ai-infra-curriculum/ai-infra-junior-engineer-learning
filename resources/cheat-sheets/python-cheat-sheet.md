# Python Cheat Sheet — AI Infrastructure Edition

Quick reference for Python features and libraries you'll use in ML infrastructure work. Not a tutorial — assumes you've completed Module 001.

## Environments and Packaging

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate           # macOS/Linux
.venv\Scripts\activate              # Windows

# Pin versions for reproducible installs
pip install -r requirements.txt
pip freeze > requirements.txt

# Modern alternative: uv (10-100x faster pip)
uv venv
uv pip install -r requirements.txt
uv pip compile requirements.in -o requirements.txt
```

| Tool | Use |
|---|---|
| `pip` + `venv` | Standard, comes with Python |
| `uv` | Drop-in replacement, much faster |
| `poetry` | Dependency resolution + packaging, opinionated |
| `pip-tools` | Compile `requirements.in` → pinned `requirements.txt` |
| `conda` | When you need non-Python deps (CUDA, MKL) bundled |

## Type Hints

```python
from typing import Optional
from collections.abc import Iterable, Mapping

def predict(features: list[float], model_version: str = "latest") -> float:
    ...

def fetch(urls: Iterable[str]) -> Mapping[str, bytes]:
    ...

def lookup(user_id: int) -> Optional[dict]:  # or: dict | None  (3.10+)
    ...
```

Run `mypy` or `pyright` in CI. Treat type errors like compile errors.

## Logging (Not print)

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Loaded model", extra={"model_version": "v3", "size_mb": 42})

# Structured logging in JSON
import json, logging.config
logging.config.dictConfig({
    "version": 1,
    "formatters": {
        "json": {"()": "pythonjsonlogger.json.JsonFormatter",
                  "format": "%(asctime)s %(levelname)s %(name)s %(message)s"}
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"level": "INFO", "handlers": ["console"]},
})
```

Levels: `DEBUG < INFO < WARNING < ERROR < CRITICAL`.

## Error Handling

```python
try:
    result = risky()
except (TimeoutError, ConnectionError) as exc:
    logger.warning("transient", exc_info=exc)
    raise                       # re-raise, preserve traceback
except ValueError as exc:
    raise InvalidInput(str(exc)) from exc   # chain
finally:
    cleanup()
```

Don't bare-`except`. Don't catch `Exception` unless you're at the top-level boundary.

## File I/O and Paths

```python
from pathlib import Path

p = Path("/data/raw") / "events.json"
text = p.read_text()
data = json.loads(text)

# Iterate
for child in Path(".").rglob("*.parquet"):
    print(child)

# Write atomically
tmp = p.with_suffix(".tmp")
tmp.write_text(payload)
tmp.replace(p)
```

## JSON / YAML

```python
import json, yaml

data = json.loads(text)
text = json.dumps(data, indent=2, default=str)   # default=str handles datetimes

with open("config.yaml") as f:
    cfg = yaml.safe_load(f)                       # always safe_load, never load
```

## Subprocess (When You Must Shell Out)

```python
import subprocess
res = subprocess.run(
    ["kubectl", "get", "pods", "-o", "json"],
    capture_output=True, text=True, check=True, timeout=30,
)
pods = json.loads(res.stdout)
```

`check=True` raises on non-zero exit. Always set `timeout`. Never pass `shell=True` with user input.

## CLI with argparse

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--threshold", type=float, default=0.5)
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()
```

For larger CLIs: `click` or `typer`.

## HTTP with requests

```python
import requests

resp = requests.post(
    "https://api.example.com/predict",
    json={"features": [...]},
    headers={"Authorization": f"Bearer {token}"},
    timeout=(3.0, 10.0),    # (connect, read)
)
resp.raise_for_status()
data = resp.json()
```

Always set a timeout. Always `raise_for_status()` or check `resp.ok`.

## Async with asyncio

```python
import asyncio, httpx

async def fetch(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10)
        return r.json()

async def main():
    results = await asyncio.gather(*(fetch(u) for u in urls))

asyncio.run(main())
```

## Concurrency Cheats

| Workload | Tool |
|---|---|
| I/O-bound, many tasks | `asyncio` |
| I/O-bound, few tasks, simple | `concurrent.futures.ThreadPoolExecutor` |
| CPU-bound | `concurrent.futures.ProcessPoolExecutor` |
| Mixed | Separate process pool from event loop with `loop.run_in_executor` |

## Testing with pytest

```python
import pytest

def test_predict_returns_float():
    assert isinstance(predict([1.0, 2.0]), float)

@pytest.mark.parametrize("inp,expected", [([1.0], 1.0), ([2.0], 2.0)])
def test_identity(inp, expected):
    assert predict(inp) == expected

@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as c:
        yield c
```

Run: `pytest -v --cov=src --cov-report=term-missing`

## Tooling

| Tool | Purpose |
|---|---|
| `black` | Auto-formatter (no config debates) |
| `ruff` | Fast linter + formatter (replaces flake8, isort, pyupgrade) |
| `mypy` / `pyright` | Static type checking |
| `pytest` | Test runner |
| `pytest-cov` | Coverage |
| `pre-commit` | Run formatters/linters on commit |
| `bandit` | Security scanner |

## Standard Project Layout

```
myproject/
├── pyproject.toml         # project metadata + tool config
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── ...
├── tests/
│   └── test_*.py
├── requirements.txt
└── README.md
```

`src/`-layout prevents accidental imports from the working directory.

## Common Gotchas

- **Mutable default argument.** Don't write `def f(x=[]):` — use `def f(x=None): x = x or []`.
- **Late binding closures.** `[lambda: i for i in range(3)]` — all lambdas return `2`. Use `lambda i=i: i`.
- **`is` vs `==`.** `is` is identity. Only use `is None`, `is True`, `is False`.
- **Floating point.** `0.1 + 0.2 != 0.3`. Use `math.isclose` or `decimal.Decimal` for currency.
- **GIL.** Threads do not parallelize CPU work in CPython. Use processes.
- **`__init__.py` ordering.** Don't put side-effecting code in package init.

## Useful Stdlib Modules

| Module | Use |
|---|---|
| `pathlib` | Filesystem paths |
| `dataclasses` | Simple data classes |
| `enum` | Named constants |
| `collections` | `Counter`, `defaultdict`, `deque` |
| `itertools` | `chain`, `groupby`, `product`, `islice` |
| `functools` | `lru_cache`, `partial`, `reduce` |
| `contextlib` | `contextmanager`, `suppress`, `ExitStack` |
| `concurrent.futures` | Pool-based parallelism |
| `secrets` | Cryptographic randomness |
| `uuid` | Unique IDs |
| `datetime` + `zoneinfo` | Time-aware datetimes |

## See Also

- [Real Python](https://realpython.com/) — high-quality tutorials
- [Python type checking guide](https://mypy.readthedocs.io/)
- [The pytest docs](https://docs.pytest.org/)
