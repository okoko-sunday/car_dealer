web: python manage.py migrate && gunicorn showroom.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile -
worker: while true; do python manage.py process_outbox --limit 100; sleep 10; done
