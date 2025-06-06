# 🇮🇷 Hami – AI-Powered Persian Mental Health App for Working Students

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
- Future support for **PHQ-9**, **GAD-7**, and more
- Automatic scoring & risk level output

### 🔁 Daily Mood Logs
- “How are you feeling today?” prompt
- Emoji/scale-based logging + optional journaling
- Used for AI pattern detection & roadmap planning

### 🤖 AI Analysis
- **NLP** on text input (journal/chat) using HuggingFace (e.g., ParsBERT)
- **ML models** classify mental health state
- Interprets results, trends, and suggests next actions

### 🧭 Personalized Roadmap
- *Fabulous-style* habit-building journeys
- Suggestions include:
  - Sleep tracking
  - Mindfulness reminders
  - Daily reflections

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
| DB              | PostgreSQL / Firebase               |
| Auth            | JWT / Firebase Auth (to be decided) |

---

## 🗂️ Project Structure

```
backend/   - FastAPI application
frontend/  - React single-page app
scripts/   - helper scripts for development/deployment
tests/     - automated test suite
```

## 🚀 Setup

1. Create a virtual environment and install backend requirements:

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

2. Copy environment variables and set a `SECRET_KEY`:

```bash
cp backend/.env backend/.env.local  # edit values as needed
export SECRET_KEY="change-me"      # required for JWT
```

3. Start the backend:

```bash
uvicorn backend.server:app --reload
```

4. Install and run the frontend:

```bash
cd frontend
yarn install
yarn start
```

The repository keeps `frontend/yarn.lock` to ensure reproducible builds.

## 🧪 Running Tests

Run the automated API tests once the backend is running:

```bash
python backend_test.py http://localhost:8000
```

## 🐳 Docker

To build and run the combined application with Docker:

```bash
docker build -t hami .
docker run -p 80:80 hami
```

## 📝 License

This project is provided for **academic research** purposes only. See the [LICENSE](LICENSE) file for details.
