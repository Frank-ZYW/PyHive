#!/bin/bash

cd /app/pyhive
uwsgi --ini uwsgi.ini
service nginx start
tail -f /dev/null