import socket
import sys

from datetime import datetime

CLOSE    = "close"
LINKDOWN = "linkdown"
LINKUP   = "linkup"
RTUPDATE = "rtupdate"
SHOWRT   = "showrt"

INF      = float('inf')
BUFFSIZE = 4096

localhost = socket.gethostbyname(socket.gethostname())

class NoNodeError(Exception):
    pass

class NoInputCmdError(Exception):
    pass

class NotUserCmdError(Exception):
    def __init__(self, cmd):
        self.cmd = cmd

class NoParamsForCmdError(Exception):
    def __init__(self, cmd):
        self.cmd = cmd

class NotEnoughParamsForCmdError(Exception):
    pass

def now_time():
    return datetime.now().strftime("%Y-%b-%d %I:%M:%S %p")

def key_to_addr(key):
    ip, port = key.split(':')
    return ip, int(port)

def addr_to_key(ip, port):
    return "%s:%s" % (ip, port)

def init_socket(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((ip, int(port)))
        print "Start PyRoute BF-Client on %s with port %s ...\n" % (ip, port)
        return sock
    except socket.err, err_msg:
        print "Ooops! Something wrong with socketbinding!"
        print "error code: %s, error message: %s\n" % err_msg
        sys.exit(1)

def get_ip(ip):
    return localhost if ip == "localhost" else ip

def encode_node_info(ip, port, cost):
    return addr_to_key(ip, port) + '#' + str(cost)

def decode_node_info(node_info_str):
     addr_key, cost = node_info_str.split('#')
     return addr_key, float(cost)

def argv_parser(argv):
    argv = argv[1:]
    route_dict = {}

    try:
        port = int(argv.pop(0))
        timeout = float(argv.pop(0))
    except ValueError, err_msg:
        print "err code: %s, error message: %s\n" % err_msg
        sys.exit(1)

    route_dict["port"] = port
    route_dict["timeout"] = timeout

    while argv:
        try:
            neighbor_ip   = get_ip(argv.pop(0))
            neighbor_port = int(argv.pop(0))
            neighbor_cost = float(argv.pop(0))
            neighbor_info = encode_node_info                                   \
                                    (neighbor_ip, neighbor_port, neighbor_cost)

            if route_dict.get("neighbors") is None:
                route_dict["neighbors"] = [neighbor_info]
            else:
                route_dict["neighbors"].append(neighbor_info)
        except ValueError, err_msg:
            print "err code: %s, error message: %s\n" % err_msg
            sys.exit(1)

    return route_dict

def user_cmd_parser(input_cmd, builtin_cmds):
    update_dict = {'cmd': '', 'addr': (), 'payload': {}}
    input_cmd_list = input_cmd.lower().split()
    if not input_cmd_list:
        raise NoInputCmdError
    cmd = input_cmd_list.pop(0)
    if cmd not in builtin_cmds:
        raise NotUserCmdError(cmd)
    if cmd == LINKUP or cmd == LINKDOWN:
        if not input_cmd_list: # nothing left behind 'LINKUP' or 'LINKDOWN'
            raise NoParamsForCmdError(cmd)
         # will have ValueError if there is no ':' in the string, let bfclient handle the case
        ip = input_cmd_list.pop(0)
        if not input_cmd_list:
            raise NotEnoughParamsForCmdError
        port = input_cmd_list.pop(0)
        update_dict['addr'] = (get_ip(ip), int(port))
    update_dict['cmd'] = cmd
    return update_dict

