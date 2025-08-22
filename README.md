# Hami – AI-Powered Persian Mental Health App for Working Students

[![Status](https://img.shields.io/badge/status-in_development-yellow)]()  
[![License](https://img.shields.io/badge/license-academic--research-blue)]()  
[![Tech Stack](https://img.shields.io/badge/stack-React%20%7C%20FastAPI%20%7C%20HuggingFace-blueviolet)]()

> 🧠 *An ethical, AI-based Persian mobile app to assess anxiety, stress, and depression in working students — built for academic research.*

---

## 🧭 Purpose

**Hami** is an AI-enhanced mobile-first platform that combines traditional psychological assessments (like DASS-21) with machine learning, daily mood logs, and NLP-powered analysis — tailored for Persian-speaking university students who are working.

This project supports a master’s thesis titled:  
**"Validation of AI for Mental Health Assessment in Working Students."**

---

## ✨ Features

### 🧪 Mental Health Testing
- Built-in **DASS-21** (validated Persian version)
- Built-in **PHQ-9** assessment
- Future support for **GAD-7** and more
- Automatic scoring & risk level output

### 🔁 Daily Mood Logs
- “How are you feeling today?” prompt
- Emoji/scale-based logging + optional journaling
- Used for AI pattern detection & roadmap planning
- Sleep tracking for hours and quality
- Daily reflections journal

### 🤖 AI Analysis
- **NLP** on text input (journal/chat) using HuggingFace (e.g., ParsBERT)
- **ML models** classify mental health state
- Interprets results, trends, and suggests next actions

### 🧭 Personalized Roadmap
- *Fabulous-style* habit-building journeys with beautiful routines and progress tracking
- Suggestions include:
  - Sleep tracking
  - Mindfulness reminders
  - Daily reflections
  - Short gratitude practice

### 💬 Persian Chatbot (v1)
- Simple rule-based assistant in Farsi
- Empathetic tone, guided self-reflection, and safe journaling

### 🔐 Privacy & Ethics
- Research consent required
- Users can export or delete their data
- No tracking or commercial profiling
- Not a diagnostic or therapeutic replacement

---

## 🧰 Tech Stack

| Component       | Technology                          |
|----------------|--------------------------------------|
| Frontend        | React (RTL, TailwindCSS)            |
| Backend         | FastAPI (Python)                    |
| AI/NLP Models   | HuggingFace ParsBERT, scikit-learn  |
| Persian NLP     | Hazm, Parsivar                      |
| DB              | MongoDB                             |
| Auth            | JWT / Firebase Auth (to be decided) |


## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+

### Environment Variables

Copy `.env.example` to `.env` and set a strong `SECRET_KEY`. The backend will
raise an error if this variable is missing.

### Backend

Each API domain now runs as its own FastAPI service, including a dedicated IDP service for issuing JWTs. Start the ones you need:

```bash
pip install -r requirements.txt
cd backend
uvicorn services.idp_service:app --reload --port 8000  # IDP service issuing JWTs
uvicorn services.auth_service:app --reload --port 8001
uvicorn services.assessments_service:app --reload --port 8002
uvicorn services.trackers_service:app --reload --port 8003
```

### Frontend

```bash
cd frontend
yarn install
yarn start
```

### Docker Compose

Run all services together:

```bash
docker-compose up --build
```

### Kubernetes Deployment

Sample manifests are provided in `k8s/microservices.yaml` for running the
backend microservices on a Kubernetes cluster.

Build and push the backend image:

```bash
docker build -t mental-ai-backend .
```

Apply the resources:

```bash
kubectl apply -f k8s/microservices.yaml
```

Each service exposes its own Swagger UI at `/docs` and the OpenAPI schema at
`/openapi.json`.

### Running Tests

Start the required FastAPI service in one terminal:

```bash
cd backend
uvicorn services.idp_service:app --reload --port 8000  # IDP service issuing JWTs
uvicorn services.auth_service:app --reload --port 8001
```

In another terminal, run the integration tests:

```bash
python backend_test.py
```

Alternatively, run the helper script to start the server, run the tests and stop the server:

```bash
bash scripts/run_backend_tests.sh
```

If your server is running on a different host or port, set the
`API_BASE_URL` environment variable before running the tests:

```bash
API_BASE_URL=http://your-host:port python backend_test.py
```

Unit tests can still be executed directly with:

```bash
pytest --cov=backend tests
```

### Create Admin User (Optional)

For local testing you may want a predefined admin account. Run the helper script:

```bash
python scripts/create_admin_user.py
```

You can override the defaults using `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables.
