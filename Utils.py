import socket
import sys

from datetime import datetime

CLOSE    = "close"
LINKDOWN = "linkdown"
LINKUP   = "linkup"
RTUPDATE = "rtupdate"
SHOWRT   = "showrt"

BUFFSIZE = 4096

localhost = socket.gethostbyname(socket.gethostname())

def now_time():
    return datetime.now().strftime("%Y-%b-%d %I:%M:%S %p")

def key_to_addr(key):
    ip, port = key.split(':')
    return ip, int(port)

def addr_to_key(host, port):
    return "%s:%s" % (host, port)

def init_client_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, int(port)))
        print "Start PyRoute BF-Client on %s with port %s ...\n" % (host, port)
        return sock
    except socket.err, err_msg:
        print "Ooops! Something wrong with socketbinding!"
        print "error code: %s, error message: %s\n" % err_msg
        sys.exit(1)

def argv_parser(argv):
    argv = argv[1:]
    route_info = {}

    try:
        port = int(argv.pop(0))
        timeout = float(argv.pop(0))
    except ValueError, err_msg:
        print "err code: %s, error message: %s\n" % err_msg
        sys.exit(1)

    route_info["port"] = port
    route_info["timeout"] = timeout

    while argv:
        try:
            neighbor_ip   = argv.pop(0)
            neighbor_port = int(argv.pop(0))
            neighbor_cost = float(argv.pop(0))
            neighbor_info = ':'.join([neighbor_ip, str(neighbor_port), str(neighbor_cost)])
            if route_info.get("neighbors") is None:
                route_info["neighbors"] = [neighbor_info]
            else:
                route_info["neighbors"].append(neighbor_info)
        except ValueError, err_msg:
            print "err code: %s, error message: %s\n" % err_msg
            sys.exit(1)

    return route_info

