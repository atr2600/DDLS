#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import os
import random
import string
import time
from datetime import timedelta

host='10.1.1.12'

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


@app.route('/')
def index():
    # print(activeUsers)
    # if 'username' not in session:
    print("hello")
    session['username'] = randomStringDigits(10)
    print(session['username'])
    session['port'] = random.randint(30000, 50000)
    print(session['port'])
    port = session['port']
    session['name'] = randomStringDigits(10)
    name = session['name']
    startDocker = 'docker run -d --name ' + str(name) + ' -it --user 0 -p ' + str(port) + ':6901 atr2600/testdock'
    killDocker = '(sleep 60m; docker rm -f ' + name + ') &'
    os.system(startDocker)
    time.sleep(1)
    # this script will sleep for 60 min in the background first.
    os.system(killDocker)
    return render_template('index.html', async_mode=socketio.async_mode, iframe=('http://' + str(host) + ':' + str(session['port']) + '/?password=vncpassword'))


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    name = session['name']
    killDocker = 'docker rm -f ' + name
    os.system(killDocker)
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, host=host, port=5000)
