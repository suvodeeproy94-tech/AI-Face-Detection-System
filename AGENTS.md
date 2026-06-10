# Project Coding Instructions

This project must stay beginner friendly, professional, and viva friendly.

## Main Rules

- Use simple code that is easy to read.
- Use meaningful names for variables, functions, files, and folders.
- Add comments before important logic in simple English.
- Do not hardcode secrets, API keys, or passwords.
- Keep backend logic inside `backend/`.
- Keep frontend logic inside `frontend/`.
- Keep datasets outside Git unless they are small sample files.

## Project Flow

The main flow should remain:

Webcam Frame -> Flask API -> Face Detection -> Face Count -> Live Statistics -> React UI

## Testing Rule

Before pushing to GitHub, run:

```bash
python -m compileall backend
python backend/app.py
npm.cmd install
npm.cmd run build
```

## Git Rule

Before pushing to GitHub, check:

- No `.env` file is staged.
- No raw dataset is staged.
- No large model file is staged by mistake.
- No generated database file is staged.
- Backend and frontend start correctly.
