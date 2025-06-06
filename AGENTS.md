# Repository Agent Instructions

This file defines conventions for both main and testing agents working in this repository.

## Running the Backend
- Install dependencies with `pip install -r requirements.txt`.
- Launch the API from the `backend` directory:
  ```bash
  cd backend
  uvicorn server:app --reload --host 0.0.0.0 --port 8001
  ```

## Running the Frontend
- Install dependencies:
  ```bash
  cd frontend
  yarn install
  ```
- Start the development server:
  ```bash
  yarn start
  ```

## Testing
- Run integration tests after the backend is accessible. Execute from the repository root:
  ```bash
  python backend_test.py
  ```
- If the backend is not running on `http://localhost:8001`, update `base_url` in `backend_test.py` before running tests.

## Linting and Formatting
- Format and lint Python code:
  ```bash
  black backend
  flake8 backend
  mypy backend  # optional type checking
  ```
- Lint frontend code:
  ```bash
  cd frontend
  npx eslint src --ext .js,.jsx
  ```

## Required Actions
- Run the commands in the **Linting and Formatting** and **Testing** sections before committing changes.
- Ensure `git status` shows a clean working tree prior to completing a pull request.
