set -e
cd "${0%/*}"

source env/bin/activate

celery -A src.worker:celery worker --loglevel=info
