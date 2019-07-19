#!/usr/bin/env python

# IMPORTS
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import os, random, subprocess,time, string

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

portlist = []
namelist = []
dockerlist = {}

host='10.1.1.12'


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
    global portlist
    global namelist
    global dockerlist
    print(dockerlist)
    dockercount = int(subprocess.check_output("docker container ls --all | wc -l", shell=True).decode("utf-8"))
    #Sorry all out of containers html page... Create one!!
    if(dockercount>50):
        return render_template('index.html')
    # Creating a random port number and container ID number
    port = random.randint(30000, 50000)
    container = randomStringDigits(10)
    while port in portlist:
        port = random.randint(30000, 50000)
    portlist.append(port)
    while container in namelist:
        container = randomStringDigits(10)
    namelist.append(container)
    # Adding this to the session
    session['port'] = port
    session['container'] = container
    # Adding this to the master list
    dockerlist[container] = port
    password = randomStringDigits(20)
    startDocker = 'docker run -d --name ' + str(container) + ' -it --user 0 -p ' + str(port) + ':6901 -e VNC_PW='\
        + password +' atr2600/vnc-nmap-ubuntu'
    killDocker = '(sleep 30m; docker rm -f ' + str(container) + ') &'
    os.system(startDocker)
    time.sleep(0.5)
    # this script will sleep for 60 min in the background first.
    os.system(killDocker)
    url = ('http://' + str(host) + ':' + str(port) + '/?password=' + str(password))
    return render_template('index.html', iframe = url, async_mode=socketio.async_mode)


def destroy():
    global portlist
    global namelist
    global dockerlist
    container = session['container']
    #killing docker container
    killDocker = 'docker rm -f ' + container
    os.system(killDocker)
    # Cleaning up the port numbers and container name
    portlist.remove(dockerlist[container])
    namelist.remove(container)
    del dockerlist[container]
    session.clear()
    return 'Killed container: ' + container


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


@socketio.on('connect', namespace='/test')
def test_connect():
    print("client connected")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    global dockerlist
    destroy()
    print(dockerlist)
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host=host, debug=True)
