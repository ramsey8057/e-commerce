from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Welcome to my flask project you are using heroku server</h1>'

if __name__ == '__main__':
    app.run()
