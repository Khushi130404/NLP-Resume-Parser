from fastapi import FastAPI, UploadFile, File
from pyresparser import ResumeParser
import tempfile
import shutil

app = FastAPI(title="Resume Parser API", version="1.0")

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Resume Parser API. Use /parse_resume/ to upload resumes."}

# Resume parsing endpoint
@app.post("/parse_resume/")
async def parse_resume(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Parse the resume
    data = ResumeParser(tmp_path).get_extracted_data()

    return {"extracted_data": data}
