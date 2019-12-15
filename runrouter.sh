#!/bin/bash

./killdock


docker run -itd --privileged --name frr frr-debian:latest

docker exec -it frr vtysh