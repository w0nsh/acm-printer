from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status

from worker import print_task

app = FastAPI()

MAX_FILE_SIZE = 30000
BUFFER_SIZE = 2**12

@app.post("/print/")
async def print_files(file: UploadFile):
    print(file)
    size = 0
    content = b''
    while chunk := await file.read(BUFFER_SIZE):
        print(chunk)
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Too large"
            )
        content += chunk
    content = content.decode('utf-8')
    task = print_task.delay(file.filename, content)
    return {"name": file.filename, "length": len(content), "task-id": task.task_id}


@app.get("/")
async def main():
    content = """
<body>
<form action="/print/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit" value="Print">
</form>
</body>
    """
    return HTMLResponse(content=content)
