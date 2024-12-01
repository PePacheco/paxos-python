import sys
sys.dont_write_bytecode = True
from process import Process
from message import P1aMessage,P1bMessage,PreemptedMessage,AdoptedMessage

hosts_and_ports_map = {
    "acceptor": [("acceptor0", 5000), ("acceptor1", 5001), ("acceptor2", 5002)],
    # "leader": [("leader0", 5100), ("leader1", 5101)],
    "leader": [("leader0", 5100)],
    "replica": [("replica0", 5200), ("replica1", 5201)],
}

class Scout(Process):
    def __init__(self, env, id, leader, acceptors, ballot_number, host, port):
        Process.__init__(self, env, id, host, port)
        self.leader = leader
        self.acceptors = hosts_and_ports_map["acceptor"]
        self.ballot_number = ballot_number
        self.env.addProc(self)

    def body(self):
        waitfor = set()
        message = P1aMessage(self.id, self.ballot_number)
        acceptors = self.env.broadcast_message_to_acceptors(message)
        for a in acceptors:
            waitfor.add(a)

        pvalues = set()
        while True:
            msg = self.getNextMessage()
            print "getNextMessage", msg
            if isinstance(msg, P1bMessage):
                if self.ballot_number == msg.ballot_number and msg.src in waitfor:
                    pvalues.update(msg.accepted)
                    waitfor.remove(msg.src)
                    if len(waitfor) < float(len(self.acceptors))/2:
                        message = AdoptedMessage(self.id, self.ballot_number, pvalues)
                        self.env.broadcast_message_to_leaders(message)
                        return
                else:
                    message = PreemptedMessage(self.id, msg.ballot_number)
                    self.env.broadcast_message_to_leaders(message)
                    return
            else:
                print "Scout: unexpected msg"
