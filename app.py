#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context,redirect

import os
import random
import string
import time
from datetime import timedelta
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

portlist = list(range(30000,50000))
random.shuffle(portlist)
portcount = 0

host='127.0.0.1'
@app.route('/')
def index():
    global portcount
    if portcount is 19995:
        portcount = 0
    dockercount = int(subprocess.check_output("sudo docker container ls --all | wc -l",shell=True).decode("utf-8"))
    #Sorry all out of containers html page... Create one!!
    if(dockercount>50):
        return render_template('index.html')
    # print(activeUsers)
    if 'username' in session:
        # return render_template('index.html', async_mode=socketio.async_mode, iframe=('http://' + str(host) + ':' + str(session['port']) + '/?password=vncpassword'))
        return redirect(('http://' + str(host) + ':' + str(session['port']) + '/?password=vncpassword'))
    else:
        session['username'] = randomStringDigits(10)
        print(session['username'])
    port = portlist[portcount]
    portcount += 1
    print(portcount)
    session['port'] = port
    print(session['port'])
    session['name'] = randomStringDigits(10)
    name = session['name']
    startDocker = 'docker run -d --name ' + str(name) + ' -it --user 0 -p ' + str(port) + ':6901 atr2600/testdock'
    killDocker = '(sleep 30m; docker rm -f ' + name + ') &'
    os.system(startDocker)
    time.sleep(0.5)
    # this script will sleep for 60 min in the background first.
    os.system(killDocker)
    url = ('http://' + str(host) + ':' + str(session['port']) + '/?password=vncpassword')
    # return render_template('index.html', async_mode=socketio.async_mode, iframe=('http://' + str(host) + ':' + str(session['port']) + '/?password=vncpassword'))
    return redirect(url)

if __name__ == '__main__':
    app.run(debug=True,host=host, port=5000)
