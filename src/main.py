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

# Constants
NACCEPTORS = 5
NREPLICAS = 3
NLEADERS = 2
NREQUESTS = 10

# Environment class
class Env:
    def __init__(self, dist):
        self.dist = False
        if dist != 1: self.dist=True
        if self.dist:
            self.available_addresses =  self.generate_ports('localhost', 10000*int(sys.argv[2])+10000, 10000*int(sys.argv[2])+11111)
        else:
            self.available_addresses =  self.generate_ports('localhost', 10000, 11111)
        self.procs = {}
        self.proc_addresses = {}
        self.config = Config([], [], [])
        self.c = 0
        self.perf = 0

    def get_network_address(self):
        return self.available_addresses.pop(0) if self.available_addresses else None

    def generate_ports(self, host, start_port, end_port):
        return [(host, port) for port in range(start_port, end_port + 1)]

    def release_network_address(self, address):
        self.available_addresses.append(address)

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
        proc.start()

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
        for i in range(NREPLICAS):
            pid = "replica %d" % i
            host, port = self.get_network_address()
            Replica(self, pid, self.config, host, port)
            self.config.replicas.append(pid)
        for i in range(NACCEPTORS):
            pid = "acceptor %d.%d" % (self.c,i)
            host, port = self.get_network_address()
            Acceptor(self, pid, host, port)
            self.config.acceptors.append(pid)
        for i in range(NLEADERS):
            pid = "leader %d.%d" % (self.c,i)
            host, port = self.get_network_address()
            Leader(self, pid, self.config, host, port)
            self.config.leaders.append(pid)

    # Create custom configuration
    def create_custom(self):
        print "Using custom configuration\n\n"
        try:
            file = open("..\config\\"+sys.argv[1], 'r')
            for line in file:
                parts = line.split(" ")
                if line.startswith("REPLICA"):
                    pid = "replica %d" % int(os.sys.argv[2])
                    self.config.replicas.append(pid)
                    host, port = parts[2].split(":")
                    self.proc_addresses[pid] = (host, int(port))
                    if os.sys.argv[3] == "REPLICA" and parts[1] == os.sys.argv[2]:
                        self.proc_addresses.pop(pid)
                        Replica(self, pid, self.config, host, int(port))
                elif line.startswith("ACCEPTOR"):
                    pid = "acceptor %d.%d" % (self.c,int(os.sys.argv[2]))
                    self.config.acceptors.append(pid)
                    host, port = parts[2].split(":")
                    self.proc_addresses[pid] = (host, int(port))
                    if os.sys.argv[3] == "ACCEPTOR" and parts[1] == os.sys.argv[2]:
                        self.proc_addresses.pop(pid)
                        Acceptor(self, pid, host, int(port))
                elif line.startswith("LEADER"):
                    pid = "leader %d.%d" % (self.c,int(os.sys.argv[2]))
                    self.config.leaders.append(pid)
                    host, port = parts[2].split(":")
                    self.proc_addresses[pid] = (host, int(port))
                    if os.sys.argv[3] == "LEADER" and parts[1] == os.sys.argv[2]:
                        self.proc_addresses.pop(pid)
                        Leader(self, pid, self.config, host, int(port))
        except Exception as e:
            print e
            self._graceexit()
        finally:
            file.close()

    # Run environment
    def run(self):
        print "\n"
        while True:
            try:
                input = raw_input("\nInput: ")

                # Exit
                if input == "exit":
                    self._graceexit()

                # New client
                elif input.startswith("newclient"):
                    parts = input.split(" ")
                    if len(parts) != 3:
                        print "Usage: newclient <client_name> <client_id>"
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses:
                                if key.startswith("replica"):
                                    self.sendMessage(val,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # New account
                elif input.startswith("newaccount"):
                    parts = input.split(" ")
                    if len(parts) != 3 and len(parts) != 2:
                        print "Usage: newaccount <client_id> <account_id>"
                        print "Usage: newaccount <account_id>"
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses:
                                if key.startswith("replica"):
                                    self.sendMessage(val,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Add account
                elif input.startswith("addaccount"):
                    parts = input.split(" ")
                    if len(parts) != 3:
                        print "Usage: addaccount <client_id> <account_id>"
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses:
                                if key.startswith("replica"):
                                    self.sendMessage(val,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Balance
                elif input.startswith("balance"):
                    parts = input.split(" ")
                    if len(parts) != 2 and len(parts) != 3:
                        print "Usage: balance <client_id> <account_id>"
                        print "Usage: balance <client_id>"
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses:
                                if key.startswith("replica"):
                                    self.sendMessage(val,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Deposit
                elif input.startswith("deposit"):
                    parts = input.split(" ")
                    if len(parts) != 3:
                        print "Usage: deposit <account_id> <amount>"
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses:
                                if key.startswith("replica"):
                                    self.sendMessage(val,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Withdraw
                elif input.startswith("withdraw"):
                    parts = input.split(" ")
                    if len(parts) != 4:
                        print "Usage: withdraw <client_id> <account_id> <amount>"
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses:
                                if key.startswith("replica"):
                                    self.sendMessage(val,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Transfer
                elif input.startswith("transfer"):
                    parts = input.split(" ")
                    if len(parts) != 5:
                        print "Usage: transfer <client_id> <from_account_id> <to_account_id> <amount>"
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            for key, val in self.proc_addresses:
                                if key.startswith("replica"):
                                    self.sendMessage(val,RequestMessage(pid,cmd))
                        else:
                            for r in self.config.replicas:
                                self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Fail
                elif input.startswith("fail"):
                    parts = input.split(" ")
                    if len(parts) != 3:
                        print "Usage: fail <func> <id>"
                    else:
                        pid = "client %d.%d" % (self.c,self.perf)
                        cmd = Command(pid,0,input+"#%d.%d" % (self.c,self.perf))
                        if self.dist:
                            #for key, val in self.proc_addresses:
                                #if key.startswith("replica"):
                                    #self.sendMessage(val,RequestMessage(pid,cmd))
                                    pass
                        else:
                            if parts[1] == "replica":
                                for r in self.config.replicas:
                                    self.sendMessage(r,RequestMessage(pid,cmd))
                            if parts[1] == "acceptor":
                                for r in self.config.acceptors:
                                    self.sendMessage(r,RequestMessage(pid,cmd))
                        time.sleep(1)

                # Create new configuration
                elif input == "reconfig":
                    self.c+=1
                    self.config = Config(self.config.replicas, [], [])
                    for i in range(NACCEPTORS):
                        pid = "acceptor %d.%d" % (self.c,i)
                        host, port = self.get_network_address()
                        Acceptor(self, pid, host, port)
                        self.config.acceptors.append(pid)
                    for i in range(NLEADERS):
                        pid = "leader %d.%d" % (self.c,i)
                        host, port = self.get_network_address()
                        Leader(self, pid, self.config, host, port)
                        self.config.leaders.append(pid)
                    for r in self.config.replicas:
                        pid = "master %d.%d" % (self.c,i)
                        cmd = ReconfigCommand(pid,0,str(self.config))
                        self.sendMessage(r, RequestMessage(pid, cmd))
                        time.sleep(1)
                    for i in range(WINDOW-1):
                        pid = "master %d.%d" % (self.c,i)
                    for r in self.config.replicas:
                        cmd = Command(pid,0,"operation noop")
                        self.sendMessage(r, RequestMessage(pid, cmd))
                        time.sleep(1)
                    self.perf=-1

                # Default
                else:
                    print "Unknown command"
                    self.perf=-1
                self.perf+=1

            except Exception as e:
                print e
                self._graceexit()

# Main
def main():
  # Create environment and check arguments
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
    # for f in os.listdir("../logs"):
    #     path = os.path.join("../logs", f)
    #     if os.path.isfile(path):
    #         os.remove(path)

    # Run environment
    e.run()

# Main call
if __name__=='__main__':
    main()