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

### Backend

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend
yarn install
yarn start
```

### Docker Compose

```bash
docker-compose up --build
```

### Running Tests

```bash
pytest --cov=backend tests
```
