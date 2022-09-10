python manage.py makemigrations
python manage.py migrate
#python manage.py loaddata fixtures.json
python manage.py collectstatic --no-input
gunicorn foodgram.wsgi:application --bind 0:8000