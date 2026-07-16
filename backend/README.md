---
title: Edusight
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# Edusight — Backend API

Backend API untuk platform pembelajaran berbasis AI Edusight.

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite + SQLAlchemy
- **Auth**: JWT (python-jose) + bcrypt
- **Validation**: Pydantic v2

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed database
python seed.py

# 3. Run server
uvicorn app.main:app --reload
```

Server akan berjalan di `http://localhost:8000`

## API Documentation

Setelah server berjalan, akses:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user baru |
| POST | `/api/auth/login` | Login, return JWT token |

### Users (Protected)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/profile` | Get profile |
| PUT | `/api/users/profile` | Update profile |
| GET | `/api/users/dashboard` | Dashboard statistics |

### Learning (Protected)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/learning/paths` | List learning paths |
| GET | `/api/learning/paths/{id}/materials` | List materials |
| GET | `/api/learning/materials/{id}` | Material detail |
| POST | `/api/learning/materials/{id}/complete` | Mark complete |
| GET | `/api/learning/materials/{id}/quiz` | Get quiz |
| POST | `/api/learning/quiz/{id}/submit` | Submit quiz |
| GET | `/api/learning/progress` | Overall progress |

### AI Insight (Protected)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/insight/me` | Get latest insight |
| POST | `/api/insight/generate` | Generate new insight |
| GET | `/api/insight/threshold` | Check activity threshold |

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── config.py         # Configuration
│   ├── database.py       # DB engine & session
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── middleware/       # Auth middleware
│   ├── utils/            # Helpers
│   ├── ai/               # K-Means clustering modules
│   └── llm/              # Groq Llama 3 API prompting modules
├── seed_real_data.py     # Database materials seeder
├── requirements.txt
└── README.md
```
