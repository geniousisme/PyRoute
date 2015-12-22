'''
rt: routing table
'''
import copy
import json
import sys
import time

from collections import defaultdict
from datetime    import datetime
from select      import select

from Timer import CountDownTimer, ResetTimer

from Utils import LINKDOWN, LINKUP, SHOWRT, CLOSE, RTUPDATE, BUFFSIZE, INF
from Utils import NoInputCmdError, NotUserCmdError, NoParamsForCmdError
from Utils import NoNodeError, NotEnoughParamsForCmdError
from Utils import argv_parser, user_cmd_parser, init_socket, localhost
from Utils import now_time, addr_to_key, key_to_addr, decode_node_info

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
        print "%s:%s is leaving PyRoute...\n" % self.sock.getsockname()
        self.sock.close()
        self.running = False
        sys.exit(0)

    def get_node(self, ip, port):
        try:
            addr_key = addr_to_key(ip, port)
            return self.node_dict[addr_key]
        except KeyError:
            raise NoNodeError

    def link_up(self, ip, port, **kwargs):
        try:
            node = self.get_node(ip, port)
            node['direct_dist'] = node['link_downed_dist']
            del node['link_downed_dist']
            node['is_neighbor'] = True
            # Bellman-Ford!
            self.calculate_costs()
        except KeyError, err_msg:
            print "error message: %s not in the nodes.\n" % err_msg
        except NoNodeError:
            print "Node at %s:%s is not in the nodes man!\n" % (ip, port)

    def link_down(self, ip, port, **kwargs):
        try:
            node = self.get_node(ip, port)
            node['link_downed_dist'] = node['direct_dist']
            node['direct_dist'] = INF
            node['is_neighbor'] = False
            node['watch_dog'].stop()
            # Bellman-Ford!
            self.calculate_costs()
        except NoNodeError:
            print "Node at %s:%s is not in the nodes man!\n" % (ip, port)

    def close(self):
        self.close_bfclient()

    def show_rt(self):
        print now_time()
        print "Distance vector list is:"
        for addr_key, node in self.node_dict.iteritems():
            if addr_key == self.me_key:
                continue
            print "Destination = %s, Cost = %s, Link = (%s)" %                 \
                            (addr_key, node['cost'], node['link'])
        print
    def init_node(self):
        return {"cost": INF, "is_neighbor": False, "link": ""}

    def node_generator(self, cost, is_neighbor,
                                    costs={}, direct_dist=INF, addr_key=""):
        node = self.init_node()
        node["cost"] = cost
        node["is_neighbor"] = is_neighbor
        node["costs"] = costs if costs else defaultdict(lambda: INF)
        node["direct_dist"] = direct_dist
        if is_neighbor:
            node['link'] = addr_key
            # make sure update_cmds use new timer to count
            monitor = ResetTimer(
                        interval=self.timeout,
                        func_ptr=self.link_down,
                        args=list(key_to_addr(addr_key)))
            monitor.start()
            node['watch_dog'] = monitor
        return node

    def get_neighbors(self):
        return {node_addr_key: node_info for node_addr_key, node_info          \
                    in self.node_dict.iteritems() if node_info['is_neighbor']}

    def rt_update(self, ip, port, **kwargs):
        costs = kwargs['costs']
        addr_key = addr_to_key(ip, port)
        for node_addr_key in costs:
            # not in the node_dict yet, add to the node_dict
            if self.node_dict.get(node_addr_key) is None:
                self.node_dict[node_addr_key] = self.init_node()

        if self.node_dict[addr_key]['is_neighbor']:
            # already neighbor, so just update node costs
            node = self.node_dict[addr_key]
            node['costs'] = costs
            # restart watch_dog timer
            node['watch_dog'].reset()
        else:
            print 'welcome new neighbor at %s !\n' % addr_key
            del self.node_dict[addr_key]
            self.node_dict[addr_key] = self.node_generator(
                                cost=self.node_dict[addr_key]['cost'],
                                is_neighbor=True,
                                direct_dist=kwargs['neighbor']['direct_dist'],
                                costs=costs,
                                addr_key=addr_key)
        # Bellman-Ford!
        self.calculate_costs()

    def broadcast_costs(self):
        costs = {node_addr_key: node_info['cost'] for node_addr_key, node_info \
                                              in self.node_dict.iteritems()}
        packet  = {'cmd': RTUPDATE}
        for neighbor_key, neighbor in self.get_neighbors().iteritems():
            updated_costs = copy.deepcopy(costs)
            for dest_addr, cost in costs.iteritems():
                if dest_addr not in [self.me_key, neighbor_key] and            \
                    self.node_dict[dest_addr]['link'] == neighbor_key:
                        updated_costs[dest_addr] = INF # poisoned the cost!
            packet['payload'] = {'costs': updated_costs,
                                 'neighbor': {'direct_dist':
                                                neighbor['direct_dist']}}
            send_packet = json.dumps(packet)
            self.sock.sendto(send_packet, key_to_addr(neighbor_key))

    def calculate_costs(self):
        for dest_addr, dest_node in self.node_dict.iteritems():
            if dest_addr == self.me_key:
                continue
            # iterate neighbors and search for min cost for destination
            min_cost, next_hop = INF, ""
            for neighbor_key, neighbor in self.get_neighbors().iteritems():
                '''
                # distance =
                # direct cost to neighbor + cost from neighbor to destination
                '''
                if dest_addr in neighbor['costs']:
                    dist = neighbor['direct_dist'] + neighbor['costs'][dest_addr]
                    if dist < min_cost:
                        min_cost = dist
                        next_hop = neighbor_key
            # set new estimated cost to node in the network
            dest_node['cost'] = min_cost
            dest_node['link'] = next_hop

    def init_rt(self):
        pass

    def client_loop(self):
        self.start_bfclient()
        route_dict = argv_parser(sys.argv)
        self.node_dict = defaultdict(lambda: self.init_node())
        self.timeout = 3 * route_dict["timeout"]

        self.sock = init_socket(localhost, route_dict["port"])
        connections = [self.sock, sys.stdin]
        self.me_key = addr_to_key(*self.sock.getsockname())
        self.node_dict[self.me_key] = self.node_generator(cost=0.0,
                                                          addr_key=self.me_key,
                                                          is_neighbor=False,
                                                          direct_dist=0.0)
        for neighbor_info in route_dict["neighbors"]:
            addr_key, cost = decode_node_info(neighbor_info)
            self.node_dict[addr_key] = self.node_generator(cost=cost,
                                                           addr_key=addr_key,
                                                           is_neighbor=True,
                                                           direct_dist=cost)
        self.broadcast_costs()
        CountDownTimer(route_dict["timeout"], self.broadcast_costs).start()

        while self.running:
            try:
                read_sockets, write_sockets, except_sockets =                  \
                                                    select(connections, [], [])
                for socket in read_sockets:
                    if socket == sys.stdin:
                        update_dict = user_cmd_parser                          \
                                         (sys.stdin.readline(), self.user_cmds)
                        cmd = update_dict['cmd']
                        if cmd == LINKUP or cmd == LINKDOWN:
                            send_data = json.dumps({'cmd': cmd,
                                                    'payload':
                                                     update_dict['payload']})
                            self.sock.sendto(send_data, update_dict['addr'])
                        self.user_cmds[cmd](*update_dict['addr'],
                                            **update_dict['payload'])
                    else:
                        recv_data, sender_addr = socket.recvfrom(BUFFSIZE)
                        recv_json = json.loads(recv_data)
                        cmd       = recv_json['cmd']
                        payload   = recv_json['payload']
                        self.update_cmds[cmd](*sender_addr, **payload)

            except KeyError, err_msg:
                    print "error message: %s\n" % err_msg
            except ValueError, err_msg:
                    print "error message: %s\n" % err_msg
            except NotEnoughParamsForCmdError:
                    print "not enough params for this command!\n"
            except NoInputCmdError:
                    print "please type in something man\n"
            except NotUserCmdError:
                    print "It is not in builtin commands"
                    print "builtin commands: %s, %s, %s, %s\n"                 \
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
