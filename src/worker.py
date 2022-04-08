import os
import time
from uuid import uuid4
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from celery import Celery


DRY_RUN = os.environ.get('DRY_RUN', 'False').lower() in ('true', '1', 't')

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


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
            return False

    if DRY_RUN:
        print(['lp', ps_file.name])
    else:
        proc = subprocess.run(['lp', ps_file.name])
        if proc.returncode != 0:
            return False

    return True