web: python manage.py collectstatic --noinput; gunicorn --workers=4 --bind=0.0.0.0:$PORT api/settings.py 
