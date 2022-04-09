import os
import time
from uuid import uuid4
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from celery import Celery

from dotenv import load_dotenv
load_dotenv('.env')

DRY_RUN = os.environ.get('DRY_RUN', 'False').lower() in ('true', '1', 't')
print(f'dry run mode: {DRY_RUN}')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', 'password')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

celery = Celery(__name__)
celery.conf.broker_url = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0'
celery.conf.result_backend = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0'

@celery.task(name="print_task")
def print_task(name: str, content: str):
    print(f'length: {len(content)}, filename: {name}')
    file = NamedTemporaryFile()
    ps_file = NamedTemporaryFile()
    file.write(content.encode('utf-8'))
    if DRY_RUN:
        print(['a2ps', file.name, '-o', ps_file.name])
    else:
        proc = subprocess.run(['a2ps', file.name, '-o', ps_file.name])
        if proc.returncode != 0:
            return 'a2ps failed'

    if DRY_RUN:
        print(['lp', ps_file.name])
    else:
        proc = subprocess.run(['lp', ps_file.name])
        if proc.returncode != 0:
            return 'lp failed'

    return 'OK'
