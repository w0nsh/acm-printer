set -e
cd "${0%/*}"

source .env
source env/bin/activate

export CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:6379/0
export CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:6379/0

celery -A src.worker:celery worker --loglevel=info
