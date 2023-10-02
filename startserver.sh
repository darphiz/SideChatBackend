#!/usr/bin/bash

set -e

# make database migrations
python manage.py migrate

# start server
gunicorn -c guni.py --bind 0.0.0.0:8080 sidechat_backend.wsgi:application
tail -f /var/log/app/app.log
