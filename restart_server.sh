ps aux | grep 'gunicorn' | awk '{print $2'} | xargs kill -9
ps aux | grep 'celery' | awk '{print $2'} | xargs kill -9
source /srv/www/gunicorn_start &
nohup python /srv/www/sscl.net/manage.py celery worker --concurrency=2 &

