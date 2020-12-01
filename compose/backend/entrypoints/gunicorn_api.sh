cd $SOURCE_DIR
gunicorn \
    --bind=0.0.0.0:8000 \
    --bind=unix:gunicorn/api.sock \
    --error-logfile=logs/gunicorn_api_error.log \
    --capture-output \
    --access-logfile=logs/gunicorn_api_access.log \
    --workers=9 \
    --timeout 60 \
    config.wsgi:application