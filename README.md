# AskMyPDF / Chat_with_pdf

A small FastAPI-based backend and UI for uploading a PDF and asking natural-language questions about it. The project extracts text from uploaded PDFs, chunks it, builds a vector index, and answers user questions using a retrieval-augmented approach.

This repository contains a `backend/` folder with the FastAPI app and simple static UI.

## Features

- Upload a PDF via a web form
- Extract text from PDFs (PyMuPDF / fitz)
- Split text into chunks for semantic search
- Create a vector index (faiss + sentence-transformers)
- Simple Q&A endpoint that queries the vector index and runs a context-aware answer routine
- Minimal single-page UI served from `backend/app/templates/index.html`

## Requirements

The backend dependencies are listed in `backend/requirements.txt`. Key packages:

- fastapi
- uvicorn
- PyMuPDF
- sentence-transformers
- faiss-cpu
- transformers
- torch
- jinja2
- python-multipart

## Quick setup (Windows PowerShell)

Open PowerShell and run:

```powershell
# change to the backend folder
cd 'c:\Users\samim_40uxmfb\Documents\prject\Chat_with_pdf\backend'

# create a virtual environment (recommended)
python -m venv .venv
# activate it
.\.venv\Scripts\Activate.ps1

# install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Notes:
- If you want GPU support for PyTorch, install the appropriate `torch` wheel for CUDA instead of the CPU-only wheel.
- `faiss-cpu` is used by default; swap to `faiss-gpu` if you install CUDA-enabled faiss.

## Run the app (development)

From the `backend` directory with your virtualenv activated:

```powershell
# run uvicorn with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open your browser at http://127.0.0.1:8000/

## Endpoints

- GET /  — serves the frontend HTML UI (`backend/app/templates/index.html`).
- POST /upload_pdf — accepts a multipart/form-data file field named `file`. Upload a PDF and the server will extract text and build the vector index.
- POST /ask_question — form field `question` (x-www-form-urlencoded or multipart). Returns JSON with `answer`.
- Static files (CSS/JS) are mounted at `/static` and served from `backend/app/static`.

## UI

The simple UI is at `backend/app/templates/index.html`. It references static assets at `/static/style.css` and `/static/script.js`.

If you see 404s for `/static/*`, ensure:

- You started the server from the `backend` folder (or that Python can import `app.main`). The application computes static and template paths relative to `app/main.py`.
- `backend/app/static/style.css` and `backend/app/static/script.js` exist.
- Uvicorn is running and no import errors occurred on startup.

## Uploads and data

Uploaded PDFs are saved in `backend/app/uploads/` by default. This folder is included in `.gitignore` created at `backend/.gitignore` to avoid accidentally committing uploaded files.

## Troubleshooting

- "Import fastapi could not be resolved" in your editor: install the dependencies into the interpreter your editor uses (or point the editor to the virtualenv `.venv`).
- Static 404s: ensure static mount is present in `app/main.py` (the app mounts `/static` to `backend/app/static`).
- If the server fails to start, check the uvicorn output for the first exception — missing packages or incompatible versions are common causes.

## Development notes

- The app currently uses a local in-memory vector store object. For production, consider persisting the index or using a managed vector database.
- For large PDFs, chunk size and overlap in the splitter may need tuning.

## Contributing

Small improvements are welcome: tests, CI, improved packaging, or a nicer frontend.

## License

This repository does not include a license file. Add one if you plan to share or publish the project (MIT is a common permissive choice).
