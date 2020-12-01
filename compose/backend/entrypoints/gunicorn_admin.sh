cd $SOURCE_DIR
python manage.py collectstatic --no-input
gunicorn \
    --bind=0.0.0.0:8010 \
    --bind=unix:gunicorn/admin.sock \
    --error-logfile=logs/gunicorn_admin_error.log \
    --capture-output \
    --access-logfile=logs/gunicorn_admin_access.log \
    --workers=1 \
    --timeout 60 \
    config.wsgi:application