from flask import Flask, redirect, session, url_for, render_template
from flask import request
from flask import jsonify
import os
import random
import string
import time
from datetime import timedelta

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=5)


app.config['SECRET_KEY'] = 'secret!'



def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


@app.route('/')
def index():
    host = '127.0.0.1'
    # print(activeUsers)
    if 'username' not in session:
        session['username'] = randomStringDigits(10)
        print(session['username'])
        session['port'] = random.randint(30000, 50000)
        print(session['port'])
        port = session['port']
        session['name'] = randomStringDigits(10)
        name = session['name']
        startDocker = 'docker run -d --name ' + str(name) + ' -p ' + str(port) + ':6901 consol/ubuntu-xfce-vnc'
        killDocker = '(sleep 30m; docker rm -f ' + name + ') &'
        os.system(startDocker)
        time.sleep(1)
        # this script will sleep for 30 min in the background first.
        os.system(killDocker)
    print('current session: ' + session['username'])
    return redirect('http://' + str(host) + ':' + str(session['port']) + '/?password=vncpassword')


if __name__ == '__main__':
    app.run(threaded=True)
