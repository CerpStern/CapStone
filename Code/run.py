from app import app
from os import system as do_the_thing

do_the_thing('ls')
app.run(debug=True, ssl_context=('./ssl.crt', './ssl.key'), host='127.0.0.1')
