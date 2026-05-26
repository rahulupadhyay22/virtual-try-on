web: gunicorn fabricvision.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
worker: celery -A fabricvision worker --loglevel=info --concurrency=2 --max-tasks-per-child=10
