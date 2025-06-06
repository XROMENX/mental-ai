# Agent Instructions

## Running Tests

Install dependencies and run the pytest suite from the repository root:

```bash
pip install -r requirements.txt
pytest
```

The file `tests/test_backend_api.py` contains integration tests that require a running backend API. They are skipped by default.
