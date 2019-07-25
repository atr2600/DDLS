#!/usr/bin/env python

# IMPORTS
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import os, random, subprocess,time, string
import docker
from docker import *

import eventlet

eventlet.monkey_patch()

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
networkCount = 0
# Docker client
client = docker.from_env()


# Using this to generate the names/passwords for the docer containers
def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

# List of the current ports in use
portlist = []
# List of the current names in use
namelist = []
# Map of the names to ports
# This is used to delete containers and remove the associated ports. 
dockerlist = {}

# Change this to your current IP
host = '127.0.0.1'



def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')

def spaceForDocker():
    return bool(int(subprocess.check_output("docker container ls --all | wc -l", shell=True).decode("utf-8")) > 50)

def generatePort():
    port = random.randint(30000, 50000)
    while port in portlist:
        port = random.randint(30000, 50000)
    portlist.append(port)
    return port

def generateName():
    container = randomStringDigits(10)
    while container in namelist:
        container = randomStringDigits(10)
    namelist.append(container)
    return container

def newContainer():
    global networkCount
    session['port'] = generatePort()
    session['container'] = generateName()
    session['password'] = randomStringDigits(20)
    # Adding this to the master list
    dockerlist[session['container']] = session['port']
    ipam_pool = docker.types.IPAMPool(
        subnet='172.11.' + str(networkCount % 256) + '.0/24',
        gateway='172.11.' + str(networkCount % 256) + '.254'
    )
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
    )
    client.networks.create(
        str(session['container']),
        ipam=ipam_config
    )
    client.containers.run('atr2600/zenmap-vnc-ubuntu',
                          tty=True,
                          detach=True,
                          network=str(session['container']),
                          name=str(session['container']),
                          user='0',
                          ports={'6901/tcp': str(session['port'])},
                          environment=["VNC_PW=" + str(session['password']),
                                       "VNC_RESOLUTION=800x600"])
    networkCount += 1



@app.route('/')
def index():
    global portlist
    global namelist
    global dockerlist
    print(dockerlist)
    
    #Sorry all out of containers html page... Create one!!
    if(spaceForDocker()):
        return render_template('index.html')
    
    newContainer()


    url = ('http://' + str(host) + ':' + str(session['port']) + '/?password=' + str(session['password']))
    print(url)
    return render_template('index.html', iframe = url, async_mode=socketio.async_mode)


  ####
  ## This function does:
  ## 1. Removes the port and name from the portlist and namelist
  ## 2. Removes the container from the master list.
  ## 3. Clears the session
  ## 4. Sends kill docker command to the system. 
####
def destroy():
    global portlist
    global namelist
    global dockerlist
    #killing docker container
    client.containers.get(session['container']).remove(force=True)
    client.networks.prune(filters=None)
    # Cleaning up the port numbers and container name
    portlist.remove(dockerlist[session['container']])
    namelist.remove(session['container'])
    del dockerlist[session['container']]
    print('Killed container: ' + session['container'])
    session.clear()

##################################################################################################################
##
## Below area is for the socket.io. 
## This checks to see if the connection is live.
##################################################################################################################

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
    # emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    global dockerlist
    destroy()
    print(dockerlist)
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host=host, debug=True)
