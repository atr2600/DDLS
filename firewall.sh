#!/bin/sh

#################################################################
# CHECKING TO SEE IF USER IS ROOT/SUDO
#################################################################
#if [[ $EUID -ne 0 ]]; then
#       echo "This script must be run as root" 
#          exit 1
#      fi
#################################################################

##################################################################
# IPTABLE COMMANDS START HERE
##################################################################
#######################
##                   ##
##  FLUSHING RULES   ##
#######################
iptables -F 


#######################
##                   ##
##   FOWARD RULES    ##
#######################
# Allowing all established and related FOWARD packets to docker container.
iptables -I FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
# Dropping FOWARD packets to a containerwith an assigned ip in 172.*.*.* subnet
iptables -I FORWARD -m iprange --dst-range 172.0.0.0-172.255.255.255 -j DROP
# Allowing FOWARD packets to the docker containers VNC's port 6901
iptables -I FORWARD -p tcp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -I FORWARD -p udp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT


#######################
##                   ##
##   INPUT RULES     ##
#######################
# Allowing all established and related INPUT packets to docker containers.
iptables -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# Dropping INPUT packets to a container with an assigned ip in 172.*.*.* subnet
iptables -I INPUT -m iprange --dst-range 172.0.0.0-172.255.255.255 -j DROP
# Allowing INPUT packets to the docker containers VNC's port 6901
iptables -I INPUT -p tcp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -I INPUT -p udp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT


#######################
##                   ##
##   OUTPUT RULES    ##
#######################
# Allowing all established and related OUTPUT packets from docker containers.
iptables -I OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# Dropping OUTPUT packets from a container with an assigned ip in 172.*.*.* subnet
iptables -I OUTPUT -m iprange --src-range 172.0.0.0-172.255.255.255 -j DROP
# Allowing OUTPUT packets from the docker containers VNC's port 6901
iptables -I OUTPUT -p tcp --sport 6901 -m iprange --src-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -I OUTPUT -p udp --sport 6901 -m iprange --src-range 172.0.0.0-172.255.255.255 -j ACCEPT
