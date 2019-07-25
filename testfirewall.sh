#!/bin/sh


iptables -A DOCKER-USER -p tcp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A DOCKER-USER -p udp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A DOCKER-USER -p tcp --sport 6901 -m iprange --src-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A DOCKER-USER -p udp --sport 6901 -m iprange --src-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A DOCKER-USER -m iprange --dst-range 172.0.0.0-172.255.255.255 -j DROP
iptables -A DOCKER-USER -m iprange --src-range 172.0.0.0-172.255.255.255 -j DROP
iptables -A DOCKER-USER -m state --state ESTABLISHED,RELATED -j ACCEPT
