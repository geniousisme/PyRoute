'''
rt: routing table
To Do:
Define your own exception with param(ex. cmd) return
'''
import json
import sys
import time

from collections import defaultdict
from datetime    import datetime
from select      import select

from Timer import CountDownTimer, ResetTimer

from Utils import LINKDOWN, LINKUP, SHOWRT, CLOSE, RTUPDATE, BUFFSIZE, INF
from Utils import NoInputCmdError, NotUserCmdError, NoParamsForCmdError
from Utils import argv_parser, user_cmd_parser, init_socket, localhost, key_to_addr, addr_to_key

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

        self.update_cmds = {
            RTUPDATE: self.rt_update,
            LINKDOWN: self.link_down,
            LINKUP  : self.link_up
        }

    def start_bfclient(self):
        self.running = True

    def close_bfclient(self):
        print "%s:%s is leaving PyRoute..." % self.sock.getsockname()
        self.sock.close()
        sys.exit(0)

    def link_up(self):
        pass

    def link_down(self):
        pass

    def close(self):
        self.close_bfclient()

    def show_rt(self):
        pass

    def init_node(self):
        return {"cost": INF, "is_neighbor": False, "link": ""}

    def new_node(self, cost, is_neighbor, neighbor_costs={},
                                            direct_dist=INF, addr=()):
        node = self.init_node()
        node["cost"] = cost
        node["is_neighbor"] = is_neighbor
        node["neighbor_costs"] = neighbors if neighbor_costs                   \
                                           else defaultdict(lambda: INF)
        node["direct_dist"] = direct_dist
        return node

    def rt_update(self):
        pass

    def broadcast_costs(self):
        pass

    def calculate_costs(self):
        pass

    def client_loop(self):
        self.start_bfclient()
        route_dict = argv_parser(sys.argv)
        self.node_dict = defaultdict(lambda: self.init_node())
        self.timeout = 3 * route_dict["timeout"]

        self.sock = init_socket(localhost, route_dict["port"])
        connections = [self.sock, sys.stdin]
        self.me_addr = self.sock.getsockname()
        self.node_dict[self.me_key] = self.new_node(cost=0.0,                  \
                                                    addr=self.me_addr,         \
                                                    is_neighbor=False,         \
                                                    direct_dist=0.0)

        for neighbor_info_tuple in route_dict["neighbors"]:
            addr, cost = neighbor_info_tuple
            self.node_dict[addr] = self.new_node(cost=cost,                    \
                                                 addr=addr,                    \
                                                 is_neighbor=True,             \
                                                 direct_dist=cost)
        self.broadcast_costs()
        CountDownTimer(route_dict["timeout"], self.broadcast_costs).start()

        while self.running:
            try:
                read_sockets, write_sockets, except_sockets =                  \
                                                    select(connections, [], [])
                for socket in read_sockets:
                    if socket == sys.stdin:
                        update_dict = user_cmd_parser(sys.stdin.readline(),    \
                                                      self.user_cmds)
                        cmd = update_dict['cmd']
                        if cmd == LINKUP or cmd == LINKDOWN:
                            send_data = json.dumps({                           \
                                                    'cmd': cmd,                \
                                                    'payload':                 \
                                                        update_dict['payload'] \
                                                   })
                            self.sock.sendto(send_data, update_dict['addr'])
                        self.user_cmds[cmd](*update_dict['addr'],              \
                                            **update_dict['payload'])
                    else:
                        recv_data, sender_addr = socket.recvfrom(BUFFSIZE)
                        recv_json  = json.dumps(recv_data)
                        cmd = recv_json['cmd']
                        payload    = recv_json['payload']
                        self.update_cmds[cmd](*sender_addr, **payload)

            except KeyError, cmd:
                    print "There is no '%s' command in update commands.\n" % cmd
            except ValueError, err_msg:
                    print "err code: %s, error message: %s\n" % err_msg
            except NoInputCmdError:
                    print "please type in something man\n"
            except NotUserCmdError:
                    print "It is not in builtin commands"
                    print "builtin commands: %s, %s, %s, %s\n"                   \
                                            % (LINKUP, LINKDOWN, SHOWRT, CLOSE)
            except NoParamsForCmdError:
                    print "plz provide parameters for the command you want\n"
            except KeyboardInterrupt, SystemExit:
                    self.close_bfclient()

    def run(self):
        self.client_loop()

if __name__ == "__main__":
    bfclient = BFClient()
    bfclient.run()
