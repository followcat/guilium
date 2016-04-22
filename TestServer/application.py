from flask import Flask
from flask import request
from flask import render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/samplemotor')
def samplemotor():
    return render_template('sample_motor.html')

@app.route('/content')
def contentindex():
    user_agent = request.headers.get('User-Agent')
    source = render_template('index.html')
    if 'Nexus 5' in user_agent:
        return source.replace('showcasing', 'showcasiny')
    return source

@app.route('/mod')
def modindex():
    source = render_template('index.html')
    user_agent = request.headers.get('User-Agent')
    if 'Nexus 5' in user_agent:
        return source.replace('This is a template', 'This iis a template').replace('Bootstrap', 'Boo0ststrap')
    return source

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
