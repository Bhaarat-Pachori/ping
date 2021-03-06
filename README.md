# ping
This in an implementation of unix based ping command in Python. To successfully run the code superuser permissions are needed.

## See the following for usage of ping.py

**Usage:**
- ping.py google.com        [a normal ping request]
- c:  ping.py -c 5 google.com,  [sends 5 ECHO Request]
- s:  ping.py -s 4 google.com,  [send data of 10+8 bytes, "Minimum length is 0 byte"]
- i:  ping.py -i 3 google.com,  [sends request every 3 seconds]
- t:  ping.py -t 3 google.com,  [times out in 3 seconds] 

Press Enter to continue

PING  google.com ['172.217.10.142'] :  56  data bytes

64  bytes from  google.com icmp_seq= 1  ttl= 55 time=0.05 seconds
64  bytes from  google.com icmp_seq= 2  ttl= 55 time=0.04 seconds
64  bytes from  google.com icmp_seq= 3  ttl= 55 time=0.03 seconds
64  bytes from  google.com icmp_seq= 4  ttl= 55 time=0.05 seconds
64  bytes from  google.com icmp_seq= 5  ttl= 55 time=0.04 seconds

Follow the above usage for different inputs to the ping command.

This implementation has used Raw Sockets. Raw sockets is a way to bypass the Host-to-Host layer. Pricisely, Ping commands runs on Application layer and the ICMP works on Internetworking layer so to bypass the Host-to-Host layer Raw sockets are used. Using the Raw sockets we send and receive ICMP ECHO request and response.

A nice explanation is given at this link about the Ping implementation in python and how it works :+1: [How it works](http://images.globalknowledge.com/wwwimages/whitepaperpdf/WP_Mays_Ping.pdf) using the Raw sockets and ICMP messages.
