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
- `backend/` - FastAPI server with `server.py` and dependencies.
- `frontend/` - React app powered by Create React App and TailwindCSS.
- `scripts/` - Helper scripts like `update-and-start.sh` used in dev containers.
- `backend_test.py` - Stand‑alone API test suite.

## ⚙️ Installing Dependencies

### Backend
```bash
pip install -r backend/requirements.txt
```

### Frontend
```bash
cd frontend
npm install   # or `yarn install`
```

## ▶️ Running Locally

Start the API server:
```bash
cd backend
uvicorn server:app --reload --port 8001
```

Start the React frontend in another terminal:
```bash
cd frontend
npm start
```
The site will be available at `http://localhost:3000` and the API at `http://localhost:8001`.

## 🐳 Docker

To build and run the full stack via Docker:
```bash
docker build -t hami .
docker run -p 8080:8080 -p 8001:8001 hami
```
Open `http://localhost:8080` to view the app.

## 🧪 Running Tests

`backend_test.py` exercises the API endpoints. Make sure the backend is running and edit the `base_url` variable at the bottom of the file if necessary. Then run:
```bash
python backend_test.py
```
