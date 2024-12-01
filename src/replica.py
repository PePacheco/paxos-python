import sys
import os
sys.dont_write_bytecode = True
from process import Process
from bank import bank
from message import ProposeMessage,DecisionMessage,RequestMessage
from utils import *

self_port = int(os.environ.get("PORT"))
self_ip = os.environ.get("HOST_IP")
self_node_type = os.environ.get("NODE_TYPE")
self_node_id = os.environ.get("NODE_ID")

class Replica(Process):
    def __init__(self, env, id, config, host, port):
        Process.__init__(self, env, id, host, port)
        self.slot_in = self.slot_out = 1
        self.proposals = {}
        self.decisions = {}
        self.requests = []
        self.config = config
        self.BankStatus = bank(id.replace(" ", "_"))
        self.env.addProc(self)

    def propose(self):
        while len(self.requests) != 0 and self.slot_in < self.slot_out+WINDOW:
            if self.slot_in > WINDOW and self.slot_in-WINDOW in self.decisions:
                if isinstance(self.decisions[self.slot_in-WINDOW],ReconfigCommand):
                    r,a,l = self.decisions[self.slot_in-WINDOW].config.split(';')
                    self.config = Config(r.split(','),a.split(','),l.split(','))
                    print self.id, ": new config:", self.config
            if self.slot_in not in self.decisions:
                cmd = self.requests.pop(0)
                self.proposals[self.slot_in] = cmd
                message = ProposeMessage(self.id,self.slot_in,cmd)
                print "sending message from", self_ip, message
                self.env.broadcast_message_to_leaders(message)
                # for ldr in self.config.leaders:
                #     self.sendMessage(ldr, ProposeMessage(self.id,self.slot_in,cmd))
            self.slot_in +=1

    def perform(self, cmd):
        for s in range(1, self.slot_out):
            if self.decisions[s] == cmd:
                self.slot_out += 1
                return
        if isinstance(cmd, ReconfigCommand):
            self.slot_out += 1
            return
        input = cmd[2].split("#")[0]
        parts = input.split(" ")
        #print self.id, ": perform",self.slot_out, ":", cmd
        if parts[0] == "newclient":
            self.BankStatus.createClient(parts[1], parts[2])
        elif parts[0] == "newaccount":
            if len(parts) == 3:
                self.BankStatus.createAccount_2(parts[1], parts[2])
            else:
                self.BankStatus.createAccount(parts[1])
        elif parts[0] == "addaccount":
            self.BankStatus.addAccount(parts[1], parts[2])
        elif parts[0] == "balance":
            if len(parts) == 3:
                self.BankStatus.balance_2(parts[1], parts[2])
            else:
                self.BankStatus.balance(parts[1])
        elif parts[0] == "deposit":
            self.BankStatus.deposit(parts[1], parts[2])
        elif parts[0] == "withdraw":
            self.BankStatus.withdraw(parts[1], parts[2], parts[3])
        elif parts[0] == "transfer":
            self.BankStatus.transfer(parts[1], parts[2], parts[3], parts[4])
        elif parts[0] == "fail":
            if parts[2] == self.id.split(" ")[1]:
                print "Replica", self.id, "fails"
                self.stop = True
        self.slot_out += 1

    def body(self):
        if not self.stop:
            print "Here I am: ", self.id
        while True:
            if not self.stop:
                msg = self.getNextMessage()
                if isinstance(msg, RequestMessage):
                    self.requests.append(msg.command)
                elif isinstance(msg, DecisionMessage):
                    self.decisions[msg.slot_number] = msg.command
                    while self.slot_out in self.decisions:
                        if self.slot_out in self.proposals:
                            if self.proposals[self.slot_out]!=self.decisions[self.slot_out]:
                                self.requests.append(self.proposals[self.slot_out])
                            del self.proposals[self.slot_out]
                        self.perform(self.decisions[self.slot_out])
                else:
                    print "Replica: unknown msg type"
                self.propose()

    def handler(self, message):
        print "isinstance of RequestMessage", isinstance(message, RequestMessage)
        if isinstance(message, RequestMessage):
            self.requests.append(message.command)
        elif isinstance(message, DecisionMessage):
            self.decisions[message.slot_number] = message.command
            while self.slot_out in self.decisions:
                if self.slot_out in self.proposals:
                    if self.proposals[self.slot_out]!=self.decisions[self.slot_out]:
                        self.requests.append(self.proposals[self.slot_out])
                    del self.proposals[self.slot_out]
                self.perform(self.decisions[self.slot_out])
        else:
            print "Replica: unknown msg type"
        self.propose()
