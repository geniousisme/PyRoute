import json
import sys
import time

from collections import defaultdict
from datetime    import datetime
from select      import select

from Timer import CountDownTimer, ResetTimer

from Utils import LINKDOWN, LINKUP, SOWRT, CLOSE

class BFClient(object):
    def __init__(self):
        self.me = None
        self.sock = None
        self.node_map = {}
        self.timeout  = 0
        self.user_cmds = {
            CLOSE   : self._close,
            LINKDOWN: self._linkdown,
            LINKUP  : self._linkup,
            SHOWRT  : self._showrt
        }
        self.neighbor_updates = {
            LINKDOWN  : self._linkdown,
            LINKUP    : self._linkup,
            COSTUPDATE: self._cost_updates
        }

    def client_loop(self):
