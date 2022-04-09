from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from celery.result import AsyncResult

from worker import print_task

app = FastAPI()
templates = Jinja2Templates(directory='templates')

MAX_FILE_SIZE = 30000
BUFFER_SIZE = 2**12

@app.post('/print/')
async def print_files(file: UploadFile):
    size = 0
    content = b''
    while chunk := await file.read(BUFFER_SIZE):
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='Too large'
            )
        content += chunk
    content = content.decode('utf-8')
    task = print_task.delay(file.filename, content)
    return RedirectResponse(f'/status/{task.task_id}', status_code=status.HTTP_302_FOUND)

@app.get('/status/{task_id}')
async def get_status(request: Request, task_id):
    task_result = AsyncResult(task_id)
    return templates.TemplateResponse('status.html', {
        'request': request,
        'task_id': task_id,
        'task_status': task_result.status,
        'task_result': task_result.result
    })

@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})
