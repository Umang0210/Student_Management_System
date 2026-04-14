# Student Hub (MERN-Style Full Stack App)

Student Hub is a full-stack student management system with authentication and CRUD operations for student records.

## Tech Stack

- Frontend: React, CRACO, Tailwind CSS, Radix UI, Axios
- Backend: FastAPI, Motor (MongoDB async client), JWT auth, bcrypt
- Database: MongoDB

## Features

- Cookie-based authentication (`/api/auth/login`, `/api/auth/logout`, `/api/auth/me`)
- Student management: create, list, update, delete
- Search and status filtering on student list
- Pagination support on backend student listing

## Project Structure

```
backend/
	requirements.txt
	server.py
frontend/
	package.json
	craco.config.js
	src/
		App.js
		contexts/
		pages/
		components/
```

## Prerequisites

- Node.js 18+
- Python 3.10+
- MongoDB (local or remote)

## Backend Setup

1. Go to backend folder:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` in `backend/` with:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=student_hub
JWT_SECRET=replace-with-a-strong-secret
REACT_APP_BACKEND_URL=http://localhost:3000
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

5. Run backend:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

1. Go to frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create `.env` in `frontend/`:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

4. Start frontend:

```bash
npm start
```

## API Summary

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/students`
- `GET /api/students`
- `GET /api/students/{student_id}`
- `PUT /api/students/{student_id}`
- `DELETE /api/students/{student_id}`

## Notes

- Backend CORS currently allows the origin from `REACT_APP_BACKEND_URL`.
- Authentication is cookie-based with short-lived access token and longer-lived refresh token.
- Admin user is seeded on backend startup from environment variables.
