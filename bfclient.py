'''
rt: routing table
'''
import json
import sys
import time

from collections import defaultdict
from datetime    import datetime
from select      import select

from Timer import CountDownTimer, ResetTimer

from Utils import LINKDOWN, LINKUP, SHOWRT, CLOSE, RTUPDATE, BUFFSIZE, INF
from Utils import argv_parser, init_socket, localhost, key_to_addr, addr_to_key

class BFClient(object):
    def __init__(self):
        self.me_key = ""
        self.sock = None
        self.node_dict = {}
        self.timeout  = 0
        self.running  = False
        self.user_cmds = {
            CLOSE   : self.close,
            LINKDOWN: self.link_down,
            LINKUP  : self.link_up,
            SHOWRT  : self.show_rt
        }

        self.udates = {
            RTUPDATE: self.rt_update,
            LINKDOWN: self.link_down,
            LINKUP  : self.link_up
        }

    def start_bfclient(self):
        self.running = True

    def close_bfclient(self):
        self.running = False

    def run(self):
        self.client_loop()

    def link_up(self):
        pass

    def link_down(self):
        pass

    def close(self):
        print "%s:%s is leaving PyRoute..." % self.sock.getsockname()
        sys.exit(0)

    def show_rt(self):
        pass

    def init_node(self):
        return {"cost": INF, "is_neighbor": False, "link": ""}

    def new_node(self, cost, is_neighbor, neighbor_costs={}, direct=INF, addr=None):
        node = self.init_node()
        node["cost"] = cost
        node["is_neighbor"] = is_neighbor
        node["neighbor_costs"] = neighbors if neighbor_costs else defaultdict(lambda: INF)
        node["direct"] = direct


    def rt_update(self):
        pass

    def client_loop(self):
        self.start_bfclient()
        route_info = argv_parser(sys.argv)
        self.node_dict = defaultdict(lambda: self.init_node())
        self.timeout = 3 * route_info["timeout"]

        self.sock = init_socket(localhost, route_info["port"])
        self.me_key = addr_to_key(*self.sock.getsockname())
        self.node_dict = [self.me_key]


        for neighbor_str in route_info["neighbors"]:
            addr_key, cost = neighbor_str.split('#')
            self.node_dict[addr_key] = self.new_node(cost=cost,
                                                     addr=addr_key,
                                                     is_neighbor=True,
                                                     direct=cost)




if __name__ == "__main__":
    bfclient = BFClient()
    bfclient.run()
