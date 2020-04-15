#!/bin/bash

dir="/app/pyhive"

is_empty_dir(){
    return `ls -A $1|wc -w`
}

if is_empty_dir $(dir)
then
    cd /app
    pyhive init
    cd pyhive
    pyhive migrate
    pyhive initadmin
    pyhive collectstatic
fi

cd /app/pyhive
uwsgi --ini uwsgi.ini
service nginx start
tail -f /dev/null