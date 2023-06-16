WORKER_NAME=$1
CONCURRENCY=$2
. src/configs/local_config.sh
cat local_worker_setup_started

if [ $? != 0 ]; then
    rm -rf .venv
    mkdir .venv
    pip install poetry && poetry install
fi
sleep 5
if [ -z "$WORKER_NAME" ]; then
    echo "🚫[FATAL] : Worker name not specified."
    exit 1
fi

if [ -z "$CONCURRENCY" ]; then
    CONCURRENCY=2
fi

touch local_worker_setup_started
cd src
../.venv/bin/celery -A celery_worker.celery_app worker -l info -Q $WORKER_NAME -c $CONCURRENCY