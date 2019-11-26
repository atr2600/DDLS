# main.py

from flask import Blueprint, render_template, session, redirect
from flask_login import login_required, current_user
from . import *

# ======================================================================
# Start Docker py imports
# ======================================================================

import random
import string
import subprocess
import docker
from docker import *

# ======================================================================
# End Docker py imports
# ======================================================================

main = Blueprint('main', __name__)

networkCount = 0
# Docker limit
docker_limit = 100
# List of the current ports in use
portlist = []
# List of the current names in use
namelist = []
# Map of the names to ports
# This is used to delete containers and remove the associated ports.
dockerlist = {}
client = docker.from_env()



@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


# Using this to generate the names/passwords for the docer containers
def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


def spaceForDocker(count):
    return bool(int(subprocess.check_output("docker container ls --all | wc -l", shell=True).decode("utf-8")) > count)


def generatePort():
    global portlist
    port = random.randint(30000, 50000)
    while port in portlist:
        port = random.randint(30000, 50000)
    portlist.append(port)
    return port


def generateName():
    global namelist
    container = randomStringDigits(10)
    while container in namelist:
        container = randomStringDigits(10)
    namelist.append(container)
    return container


# This function creates a new docker network with a unique subnet
def newNetwork(subnet):
    global client
    # class IPAMPool(subnet=None, iprange=None, gateway=None, aux_addresses=None)
    #       Create an IPAM pool config dictionary to be added to the pool_configs parameter of IPAMConfig.
    ipam_pool = docker.types.IPAMPool(
        subnet=subnet
    )

    # class IPAMConfig(driver='default', pool_configs=None, options=None)
    #       Create an IPAM (IP Address Management) config dictionary to be used with create_network().
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
    )

    #  create(name, *args, **kwargs)
    #       Create a network. Similar to the docker network create.
    client.networks.create(
        str(session['container']),
        ipam=ipam_config
    )


def newContainer(imageName):
    global networkCount
    global dockerlist
    global client
    session['port'] = generatePort()
    session['container'] = generateName()
    session['password'] = randomStringDigits(20)
    # Adding this to the master list
    dockerlist[session['container']] = session['port']
    newNetwork(('172.11.' + str(networkCount % 256) + '.0/24'))
    client.containers.run(imageName,
                          tty=True,
                          detach=True,
                          network=str(session['container']),
                          name=str(session['container']),
                          user='0',
                          ports={'6901/tcp': str(session['port'])},
                          environment=["VNC_PW=" + str(session['password']),
                                       "VNC_RESOLUTION=800x600"])
    networkCount += 1


def getDocker(imageName):
    newContainer(imageName)
    url = ('http://' + str(host) + ':' + str(session['port']) + '/?password=' + str(session['password']))
    print(url)
    return url


@main.route('/')
@login_required
def index():
    global portlist
    global namelist
    global dockerlist
    global docker_limit
    print(dockerlist)

    # Sorry all out of containers html page... Create one!!
    if spaceForDocker(docker_limit):
        return render_template('error.html')

    url = getDocker('atr2600/zenmap-vnc-ubuntu')
    return redirect(url)


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
    global client
    # killing docker container
    client.containers.get(session['container']).remove(force=True)
    client.networks.prune(filters=None)
    # Cleaning up the port numbers and container name
    portlist.remove(dockerlist[session['container']])
    namelist.remove(session['container'])
    del dockerlist[session['container']]
    print('Killed container: ' + session['container'])
    session.clear()
