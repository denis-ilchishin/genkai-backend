cd $SOURCE_DIR
rm -rf celerybeat.pid
celery --app=config.celery.app --loglevel=INFO beat --scheduler django_celery_beat.schedulers:DatabaseScheduler