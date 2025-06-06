# Development Guide

This project contains a FastAPI backend and a React frontend. The following instructions outline how to run each service, execute the backend test suite and apply code quality tools.

## Running the Backend

1. Install Python dependencies (preferably in a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI server from the `backend` directory:
   ```bash
   cd backend
   uvicorn server:app --reload --host 0.0.0.0 --port 8001
   ```

## Running the Frontend

1. Install dependencies using `yarn` (or `npm`):
   ```bash
   cd frontend
   yarn install
   ```
2. Start the development server:
   ```bash
   yarn start
   ```
   The application will be available at [http://localhost:3000](http://localhost:3000).

## Executing `backend_test.py`

The file `backend_test.py` performs integration tests against the running API.

1. Ensure the backend is running locally on `http://localhost:8001` or edit the
   `base_url` inside `backend_test.py` to point to the correct address.
2. Run the tests from the repository root:
   ```bash
   python backend_test.py
   ```

## Linting and Formatting

The repository uses standard tools for maintaining code style.

- **Python**: Run [Black](https://black.readthedocs.io/) for formatting and
  [Flake8](https://flake8.pycqa.org/) for linting. Optional type checking can be
  performed with `mypy`.
  ```bash
  black backend
  flake8 backend
  mypy backend
  ```
- **JavaScript/React**: ESLint is available via the frontend dev dependencies.
  ```bash
  cd frontend
  npx eslint src --ext .js,.jsx
  ```
