#!/bin/bash

err(){
	echo "usage: $0 admin_email@organization.whatever"
	exit 0
}

[ "$#" -eq 0 ] && err && exit 0

pip install -r requirements.txt

[ -f test.db ] && rm -f test.db

python -c "from app import db; db.create_all()"
sqlite3 test.db "insert into users (email) values (\"${1}\")"
sqlite3 test.db "update users set admin=1"

