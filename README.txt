# PyRoute
### Computer Networks Programming Assignment 3: Distributed Bellman­-Ford

![Hope you like it](http://imgs.xkcd.com/comics/pillow_talk.jpg)

#### Program Overview

PyRoute includes 3 files:

- main program files: Utils.py, bfclient.py, Timer.py

1. bfclient.py:

  All of the main functions are in this file, like bellman-ford function, linkup, linkdown, routing table update, close, etc... Basically I used JSON file to record each node routing table, and also use JSON to tranmit the update information.

2. Utils.py

  Utility functions, inlcuding a lot of often-used funtions, like argument parser, user input parser, now_time formatter, and a lot of constant variable are defined here. Also, I define a lot of Error classes by myself to help us to know the error cases better user face now.

3. Timer.py

  Control the thread timing function.

- other files: Makefile.

1. Makefile: nothing there, just some echo message.

#### How To Use It?
Add a node to an existing network or create a new network if this is the first node:
```
python bfclient.py <listening-port> <timeout> <ip-address1 port1 weight1> <ip-address2 port2 weight2> ...
```
Above command means that node will listen on localhost will listen on listen-port, and will broadcast the distance vector to its neighbots.

The cost, or weight of edge to other nodes in the network are defined through the `ip-address port distance` argument triples.


#### Testing
```
python bfclient.py 20000 4 localhost 20001 25.0
```
```
python bfclient.py 20001 4 localhost 20000 25.0
```
```
python bfclient.py 4115 3 localhost 4116 5.0 localhost 4118 30.0
python bfclient.py 4116 3 localhost 4115 5.0
python bfclient.py 4118 3 localhost 4115 30.0
```
```
python bfclient.py 4117 3 localhost 4118 20.0
linkdown localhost 4118
linkup localhost 4118
close
```
------

#### Hope you enjoy PyRoute !!!

=======


