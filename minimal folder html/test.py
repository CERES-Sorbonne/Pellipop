from pathlib import Path
from typing import List, Tuple

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse


app = FastAPI()

@app.get("/")
async def read_root():
    return HTMLResponse(content=open('test.html').read(), status_code=200)

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)) -> List[Tuple[str, str, str]]:
    file_contents = {}
    for file in files:
        file_name = file.filename
        file_content = await file.read()
        file_contents[file_name] = file_content.decode('utf-8')
    return flatten_directory(file_contents)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "test:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
