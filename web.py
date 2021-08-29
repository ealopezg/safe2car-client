from flask import Flask, render_template, request
from waitress import serve
from config import Config
import requests
app = Flask(__name__,static_folder='./web/static',template_folder='./web/templates')
app.debug = True


config = Config('config.ini')



def testToken(token):
    api = requests.Session()
    api.headers.update({"Authorization":"Bearer "+token,"Accept": "application/json"})
    r = api.get(config.BASE_URL+'/api/user')
    if r.ok:
        return r.json()['id']
    else:
        return None




@app.route('/')
def index():
    return render_template('app.html')

@app.route('/save_token', methods = ['GET', 'POST'])
def save_token():
    token = request.form['token']
    vehicle_id = testToken(token)
    if vehicle_id:
        config.setTokenAndId(token,vehicle_id)
        return render_template('success.html')
    else:
        return render_template('fail.html')

def runApp():
    serve(app,host = '0.0.0.0', port = 8080)
    

def stopApp():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running werkzeug')
    shutdown_func()