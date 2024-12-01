import sys
sys.dont_write_bytecode = True
from message import P2aMessage,P2bMessage,PreemptedMessage,DecisionMessage
from process import Process

class Commander(Process):
    def __init__(self, env, id, leader, acceptors, replicas, ballot_number, slot_number, command, host, port):
        Process.__init__(self, env, id, host, port)
        self.leader = leader
        self.acceptors = acceptors
        self.replicas = replicas
        self.ballot_number = ballot_number
        self.slot_number = slot_number
        self.command = command
        self.env.addProc(self)

        # self.waitfor = set()
        # for a in self.acceptors:
        #     self.sendMessage(a, P2aMessage(self.id, self.ballot_number, self.slot_number, self.command))
        #     self.waitfor.add(a)

    def body(self):
        waitfor = set()
        for a in self.acceptors:
            self.sendMessage(a, P2aMessage(self.id, self.ballot_number, self.slot_number, self.command))
            waitfor.add(a)

        while True:
            msg = self.getNextMessage()
            if isinstance(msg, P2bMessage):
                if self.ballot_number == msg.ballot_number and msg.src in waitfor:
                    waitfor.remove(msg.src)
                    if len(waitfor) < float(len(self.acceptors))/2:
                        for r in self.replicas:
                            self.sendMessage(r, DecisionMessage(self.id, self.slot_number, self.command))
                        return
                else:
                    self.sendMessage(self.leader, PreemptedMessage(self.id, msg.ballot_number))
                    return

    def handler(self, message):
        if isinstance(message, P2bMessage):
            if self.ballot_number == message.ballot_number and message.src in self.waitfor:
                self.waitfor.remove(message.src)
                if len(self.waitfor) < float(len(self.acceptors))/2:
                    # for r in self.replicas:
                    #     self.sendMessage(r, DecisionMessage(self.id, self.slot_number, self.command))
                    message = DecisionMessage(self.id, self.slot_number, self.command)
                    self.env.broadcast_message_to_replicas(message)
                    return
            else:
                self.sendMessage(self.leader, PreemptedMessage(self.id, message.ballot_number))
                return