import sys
sys.dont_write_bytecode = True
from utils import PValue
from process import Process
from message import P1aMessage,P1bMessage,P2aMessage,P2bMessage,RequestMessage

class Acceptor(Process):
    def __init__(self, env, id, host, port):
        Process.__init__(self, env, id, host, port)
        self.ballot_number = None
        self.accepted = set()
        self.env.addProc(self)

    def body(self):
        if not self.stop:
            print "Here I am: ", self.id
        while True:
            if not self.stop:
                msg = self.getNextMessage()
                if isinstance(msg, P1aMessage):
                    if msg.ballot_number > self.ballot_number:
                        self.ballot_number = msg.ballot_number
                    self.sendMessage(msg.src,P1bMessage(self.id,self.ballot_number,self.accepted))
                elif isinstance(msg, P2aMessage):
                    if msg.ballot_number == self.ballot_number:
                        self.accepted.add(PValue(msg.ballot_number, msg.slot_number, msg.command))
                    self.sendMessage(msg.src, P2bMessage(self.id, self.ballot_number, msg.slot_number))
                elif isinstance(msg, RequestMessage):
                    if msg.command[2].split(" ")[2].split("#")[0] == self.id.split(".")[1]:
                        print "Acceptor", self.id, "fails"
                        self.stop = True