cd $SOURCE_DIR
celery --app=config.celery.app --loglevel=INFO worker 