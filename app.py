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

portlist = []
namelist = []
dockerlist = {}

host='127.0.0.1'

@app.route('/destroy',methods=['POST'])
def destroy():
    global portlist
    global namelist
    req_data = request.get_json()
    container = req_data['container']
    #killing docker container
    killDocker = 'docker rm -f ' + container
    os.system(killDocker)
    # Cleaning up the port numbers and container name
    portlist.remove(dockerlist[container])
    namelist.remove(container)
    session.clear()
    return 'Killed container: ' + container


@app.route('/')
def index():
    global portlist
    global namelist
    dockercount = int(subprocess.check_output("docker container ls --all | wc -l", shell=True).decode("utf-8"))
    #Sorry all out of containers html page... Create one!!
    if(dockercount>50):
        return render_template('index.html')
    port = random.randint(30000, 50000)
    container = randomStringDigits(10)
    while port in portlist:
        port = random.randint(30000, 50000)
    portlist.append(port)
    while container in namelist:
        container = randomStringDigits(10)
    namelist.append(container)

    dockerlist[container] = port;
    password = randomStringDigits(20)
    startDocker = 'docker run -d --name ' + str(container) + ' -it --user 0 -p ' + str(port) + ':6901 -e VNC_PW='\
        + password +' atr2600/vnc-nmap-ubuntu'
    killDocker = '(sleep 30m; docker rm -f ' + str(container) + ') &'
    os.system(startDocker)
    time.sleep(0.5)
    # this script will sleep for 60 min in the background first.
    os.system(killDocker)
    url = ('http://' + str(host) + ':' + str(port) + '/?password=' + str(password))
    data = {
        'url': url,
        'container': container
    }
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = 'http://luisrei.com'
    return resp

if __name__ == '__main__':
    app.run(debug=True,host=host, port=5000, ssl_context='adhoc')
