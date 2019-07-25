#!/bin/sh


iptables -F 

iptables -A FORWARD -p tcp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A FORWARD -p udp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A FORWARD -m iprange --dst-range 172.0.0.0-172.255.255.255 -j DROP
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

iptables -A INPUT -p tcp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A INPUT -p udp --dport 6901 -m iprange --dst-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A INPUT -m iprange --dst-range 172.0.0.0-172.255.255.255 -j DROP
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

iptables -A OUTPUT -p tcp --sport 6901 -m iprange --src-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A OUTPUT -p udp --sport 6901 -m iprange --src-range 172.0.0.0-172.255.255.255 -j ACCEPT
iptables -A OUTPUT -m iprange --src-range 172.0.0.0-172.255.255.255 -j DROP
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT


