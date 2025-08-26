from fastapi import FastAPI, UploadFile, File
from pyresparser import ResumeParser
import tempfile
import shutil

app = FastAPI()

@app.post("/parse_resume/")
async def parse_resume(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    data = ResumeParser(tmp_path).get_extracted_data()
    return {"extracted_data": data}
