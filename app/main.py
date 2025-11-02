from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from app.services.pdf_loader import extract_text_from_pdf
from app.services.vector_store import VectorStore
from app.utils.text_splitter import split_text_into_chunks

app = FastAPI()

# Limit thread usage for BLAS/OpenMP libraries to reduce RAM pressure on small hosts
# These should be set before heavy model libraries (numpy/torch/transformers) are initialized.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Resolve paths relative to this file (backend/app)
BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Mount static files directory at /static
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

vector_store = VectorStore()
pdf_text = ""


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile):
    global pdf_text
    file_path = UPLOAD_FOLDER / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    pdf_text = extract_text_from_pdf(str(file_path))
    chunks = split_text_into_chunks(pdf_text)
    vector_store.create_index(chunks)
    return {"message": f"{file.filename} uploaded and processed successfully!"}


@app.post("/ask_question")
async def ask_question(question: str = Form(...)):
    global pdf_text
    if not pdf_text:
        return {"answer": "Please upload a PDF first."}
    if not question.strip() or len(question) < 3:
        return {"answer": "Please ask a valid question about the uploaded PDF."}

    relevant_chunks = vector_store.query(question)
    context = " ".join(relevant_chunks)
    # Import QA engine lazily to avoid loading heavy transformer models at startup
    try:
        from app.services.qa_engine import get_answer_from_context
    except Exception as e:
        return {"answer": f"Server error loading QA model: {e}"}

    answer = get_answer_from_context(question, context)
    return {"answer": answer}


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    template_path = BASE_DIR / "templates" / "index.html"
    return open(template_path, encoding="utf-8").read()

