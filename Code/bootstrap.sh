#!/bin/sh

pip install -r requirements.txt

[ -f test.db ] && rm -r test.db

python -c "from app import db; db.create_all()"
sqlite3 test.db "insert into users (email) values (\"${1}\")"
sqlite3 test.db "update users set admin=1"
