#! /bin/bash

tmux new-session -d -s vncdockers
tmux send-keys 'python3 /home/khan/docker_vnc_webapp/app.py' C-m
tmux detach -s vncdockers
