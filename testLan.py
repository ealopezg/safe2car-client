import netifaces as ni

ni.ifaddresses('eth1')
ip = ni.ifaddresses('eth1')
print(ip)  # should print "192.168.100.37"