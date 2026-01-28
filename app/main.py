from fastapi import FastAPI, UploadFile, BackgroundTasks
from slowapi.middleware import SlowAPIMiddleware
from app.ingestion import ingest_document
from app.rag import retrieve, generate_answer
from app.models import QueryRequest
from app.rate_limit import limiter

app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.post("/upload")
async def upload_document(file: UploadFile, bg: BackgroundTasks):
    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    bg.add_task(ingest_document, file_path)
    return {"status": "Document ingestion started"}

@app.post("/ask")
@limiter.limit("5/minute")
def ask_question(query: QueryRequest):
    chunks = retrieve(query.question)
    answer = generate_answer(query.question, chunks)
    return {"answer": answer}

@app.get("/health")
def health():
    return {"status": "running"}
