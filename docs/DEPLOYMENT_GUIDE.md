# Deployment Guide

This guide explains how to prepare the project for deployment.

## Local Production Check

Run these commands before deployment:

```bash
python -m compileall backend
```

```bash
cd frontend
npm.cmd run build
```

## Frontend Deployment

The frontend can be deployed on:

- Vercel
- Netlify
- Render Static Site

Build command:

```bash
npm.cmd run build
```

Output folder:

```text
frontend/dist
```

Environment variable:

```text
VITE_API_BASE_URL=https://your-backend-url
```

## Backend Deployment

The backend can be deployed on:

- Render
- Railway
- Python server

Install command:

```bash
python -m pip install -r backend/requirements.txt
```

Start command for development:

```bash
python backend/app.py
```

For real production, use a WSGI server such as Gunicorn on Linux.

## Important Production Notes

- Use HTTPS for camera access in production.
- Set the correct frontend URL in backend CORS settings.
- Keep `.env` files out of GitHub.
- Do not commit raw datasets.
- Do not commit generated SQLite database files.

## Deployment Limitation

Live webcam access works best on localhost or HTTPS. Browsers may block webcam
access on insecure HTTP production domains.
