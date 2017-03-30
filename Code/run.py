from app import app

app.run(debug=True, ssl_context=('./ssl.crt', './ssl.key'), host='127.0.0.1')
