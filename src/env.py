# -*- coding: utf-8 -*-

# Imports
import sys
sys.dont_write_bytecode = True
import cPickle as pickle
import os, time, socket, struct
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from replica import Replica
from utils import *
from datetime import datetime
from timestampManager import TimestampManager

timestampManager = TimestampManager.get_instance()

inputs = [
    "newclient A 1",
    "newclient B 2",
    "newclient C 3",
    "newaccount 1 1",
    "addaccount 1 2",
    "balance 2 1",
    "deposit 1 100",
    "balance 2 1",
]

hosts_and_ports_array = [
    ("acceptor0", 5000),  # 172.16.238.10
    ("acceptor1", 5001),  # 172.16.238.11
    ("acceptor2", 5002),  # 172.16.238.12
    ("leader0", 5100),  # 172.16.238.13
    # ("leader1", 5101),  # 172.16.238.14
    ("replica0", 5200),  # 172.16.238.15
    ("replica1", 5201),  # 172.16.238.16
]

hosts_and_ports_map = {
    "acceptor": [("acceptor0", 5000), ("acceptor1", 5001), ("acceptor2", 5002)],
    # "leader": [("leader0", 5100), ("leader1", 5101)],
    "leader": [("leader0", 5100)],
    "replica": [("replica0", 5200), ("replica1", 5201)],
}

self_port = int(os.environ.get("PORT"))
self_ip = os.environ.get("HOST_IP")
self_node_type = os.environ.get("NODE_TYPE")
self_node_id = os.environ.get("NODE_ID")

# Constants
MAX_RUNS = 6
NACCEPTORS = 2
NREPLICAS = 2
NLEADERS = 1
NREQUESTS = 10

# Environment class
class Env:
    def __init__(self, dist):
        self.dist = False
        if dist != 1: self.dist=True
        self.available_addresses = []
        for host, port in hosts_and_ports_array:
            if host != self_ip:
                self.available_addresses.append((host, port))
        # if self.dist:
        #     s = self.generate_ports('localhost', 10000*int(sys.argv[2])+10000, 10000*int(sys.argv[2])+11111)
        #     self.available_addresses = s
        # else:
        #     s = self.generate_ports('localhost', 10000, 11111)
        #     self.available_addresses = s
        self.procs = {}
        self.proc_addresses = {}
        self.config = Config([], [], [])
        self.c = 0
        self.perf = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hosts_and_ports_map = hosts_and_ports_map

    def get_network_address(self):
        return self.available_addresses.pop(0) if self.available_addresses else None

    def generate_ports(self, host, start_port, end_port):
        return [(host, port) for port in range(start_port, end_port + 1)]

    def release_network_address(self, address):
        self.available_addresses.append(address)

    def send_single_message(self, message, address_tuple):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print "<- Message sent", message.__class__, "to", address_tuple, "\n"
            s.connect(address_tuple)
            data = pickle.dumps(message, protocol=pickle.HIGHEST_PROTOCOL)
            s.sendall(struct.pack('!I', len(data)) + data)
        except Exception as e:
            print("Failed to send message:", e)
        finally:
            s.close()

    def broadcast_message_to_acceptors(self, message):
        for acceptor in hosts_and_ports_map['acceptor']:
            self.send_single_message(message, acceptor)
        return hosts_and_ports_map['acceptor']

    def broadcast_message_to_replicas(self, message):
        for replicas in hosts_and_ports_map['replica']:
            self.send_single_message(message, replicas)

    def broadcast_message_to_leaders(self, message):
        for leaders in hosts_and_ports_map['leader']:
            self.send_single_message(message, leaders)

    def sendMessage(self, dst, msg):
        if dst in self.proc_addresses:
            host, port = self.proc_addresses[dst]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            data = pickle.dumps(msg, protocol=pickle.HIGHEST_PROTOCOL)
            s.sendall(struct.pack('!I', len(data)) + data)
        except Exception as e:
            print("Failed to send message:", e)
        finally:
            s.close()

    def addProc(self, proc):
        self.procs[proc.id] = proc
        self.proc_addresses[proc.id] = (proc.host, proc.port)
        # proc.start()

    def removeProc(self, pid):
        if pid in self.procs:
            del self.procs[pid]
            del self.proc_addresses[pid]

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(exitcode)

    # Create default configuration
    def create_default(self):
        print "Using default configuration\n\n"
        pid = self_ip
        if self_node_type == "REPLICA":
            r = Replica(self, pid, self.config, self_ip, self_port)
            self.config.replicas.append(r)
        if self_node_type == "ACCEPTOR":
            a = Acceptor(self, pid, self_ip, self_port)
            self.config.acceptors.append(a)
        if self_node_type == "LEADER":
            l = Leader(self, pid, self.config, self_ip, self_port)
            self.config.leaders.append(l)

    # Run environment
    def run(self):
        count = 0
        count_global = 0
        t0 = datetime.now()
        timestampManager.set_timestamp('t0', t0)
        while count_global < MAX_RUNS:
            count_global += 1
            print "input number ", count_global
            try:
                # input = raw_input("\nInput: ")
                input = inputs[count]
                if count < 6:
                    count += 1
                else:
                    count = 0

                # address = self.available_addresses[0]
                print "Running input", input, self_ip
                pid = "client %d.%d" % (self.c,self.perf)
                t1 = datetime.now()
                timestampManager.set_timestamp('t1', t1)
                cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                message = RequestMessage(pid,cmd)
                self.broadcast_message_to_replicas(message) # WORKING
                t2 = datetime.now()
                timestampManager.set_timestamp('t2', t2)
                # Exit
                if input == "exit":
                    self._graceexit()
                    self.perf=-1
                self.perf+=1
            except Exception as e:
                print e
                self._graceexit()

        t4 = datetime.now()
        timestampManager.set_timestamp('t4', t4)
        timedDifference = timestampManager.get_time_difference( "t4", "t0" )
        print t4 - t0
        vazao = len(input) / (t4 - t0).total_seconds()
        print "vazao(requests/seconds): ", vazao
        time.sleep(500)

# Main
def main():
  # Create environment and check arguments
    print "Ran for", self_node_type
    e = Env(len(os.sys.argv))
    if len(os.sys.argv) == 1:
        e.create_default()
        time.sleep(1)
    elif len(os.sys.argv) == 4:
        e.create_custom()
        time.sleep(5)
    else:
        print "Usage: env.py"
        print "Usage: env.py <config_file> <id> <function>"
        os._exit(1)

    # Reset log files
    for f in os.listdir("../logs"):
        path = os.path.join("../logs", f)
        if os.path.isfile(path):
            os.remove(path)

    # Run environment
    if self_node_type == "LEADER":
        e.run()
    while True:
        time.sleep(2000)
        print "sleeping"

# Main call
if __name__=='__main__':
    main()