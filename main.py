from typing import Optional

import uvicorn

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.responses import StreamingResponse
import shutil
import os

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/downloadfile/{filename}")
async def download_file(filename: str):
    # Check if the file exists
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="File not found")

    # Open the file and return it as a StreamingResponse
    file_path = os.path.abspath(filename)
    return StreamingResponse(open(file_path, "rb"), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})

if __name__=="__main__":
    uvicorn.run(app)