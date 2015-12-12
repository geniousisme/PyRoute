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

from Utils import LINKDOWN, LINKUP, SHOWRT, CLOSE, RTUPDATE
from Utils import argv_parser

class BFClient(object):
    def __init__(self):
        self.me = None
        self.sock = None
        self.node_map = {}
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
        pass

    def show_rt(self):
        pass

    def rt_update(self):
        pass

    def client_loop(self):
        self.start_bfclient()
        route_info = argv_parser(sys.argv)

if __name__ == "__main__":
    bfclient = BFClient()
    bfclient.run()
