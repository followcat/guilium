from flask import Flask
from flask import request
from flask import render_template


app = Flask(__name__)
samplemotor_nums = 0


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mismatch')
def mismatch():
    global samplemotor_nums
    user_agent = request.headers.get('User-Agent')
    if 'Nexus 5' in user_agent:
        is_match = False
    else:
        is_match = True
    if 'Nexus 5' in user_agent:
        return render_template('mismatch.html', is_match=is_match).replace('This is a template', 'This iis a template').replace('Primary', 'Primmmmmmmmmmmmmmmary').replace('Bootstrap', 'Boo0ststrap')
    else:
        return render_template('mismatch.html', is_match=is_match)


@app.route('/image')
def samplemotor():
    global samplemotor_nums
    if samplemotor_nums%2 == 0:
        img_str = "/static/img/motor.jpg"
    else:
        img_str = "/static/img/DodgeTomahawk.jpg"
    samplemotor_nums += 1
    return render_template('sample_motor.html', img_str=img_str)

@app.route('/text')
def contentindex():
    user_agent = request.headers.get('User-Agent')
    source = render_template('index.html')
    if 'Nexus 5' in user_agent:
        return source.replace('showcasing', 'showcasiny')
    return source

@app.route('/textlayout')
def modindex():
    source = render_template('index.html')
    user_agent = request.headers.get('User-Agent')
    if 'Nexus 5' in user_agent:
        return source.replace('This is a template', 'This iis a template').replace('Primary', 'Primmmmmmmmmmmmmmmary').replace('Bootstrap', 'Boo0ststrap')
    return source

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
