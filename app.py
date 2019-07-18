#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context,redirect, jsonify, Response

from flask_cors import CORS

import os
import random
import string
import time
from datetime import timedelta
import subprocess
import json

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'

def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

portlist = list(range(30000,50000))
random.shuffle(portlist)
portcount = 0

host='10.1.1.12'

@app.route('/destroy',methods=['POST'])
def destroy():
    req_data = request.get_json()
    container = req_data['container']
    print('Killed: ' + container)
    killDocker = 'docker rm -f ' + container
    os.system(killDocker)
    session.clear()
    return 'Killed container: ' + container


@app.route('/')
def index():
    global portcount
    if portcount is 19995:
        portcount = 0
    dockercount = int(subprocess.check_output("sudo docker container ls --all | wc -l",shell=True).decode("utf-8"))
    #Sorry all out of containers html page... Create one!!
    if(dockercount>50):
        return render_template('index.html')
    port = portlist[portcount]
    portcount += 1
    container = randomStringDigits(10)
    startDocker = 'docker run -d --name ' + str(container) + ' -it --user 0 -p ' + str(port) + ':6901 atr2600/testdock'
    killDocker = '(sleep 30m; docker rm -f ' + str(container) + ') &'
    os.system(startDocker)
    time.sleep(0.5)
    # this script will sleep for 60 min in the background first.
    os.system(killDocker)
    url = ('http://' + str(host) + ':' + str(port) + '/?password=vncpassword')
    data = {
        'url'  : url,
        'container' : container
    }
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = 'http://luisrei.com'
    return resp

if __name__ == '__main__':
    app.run(debug=True,host=host, port=5000)
