import sys
sys.dont_write_bytecode = True
from utils import BallotNumber
from process import Process
from commander import Commander
from scout import Scout
from message import ProposeMessage,AdoptedMessage,PreemptedMessage
from timeout_semaphore import TimeoutSemaphore

class Leader(Process):
    def __init__(self, env, id, config, host, port, callback):
        Process.__init__(self, env, id, host, port)
        self.ballot_number = BallotNumber(0, self.id)
        self.active = False
        self.proposals = {}
        self.config = config
        self.env.addProc(self)
        self.semaphore = TimeoutSemaphore()
        self.callback = callback
        self.scout_number=1
        self.commander_number=1
        self.create_scout()


    def create_scout(self):
        address = (self.host, 5300+self.scout_number)
        if address:
            host, port = address
            scout_id = "scout:{}:{}".format(self.id, self.ballot_number)
            scout = Scout(self.env, scout_id, self.id, self.config.acceptors, self.ballot_number, host, port)
            scout.start()

        self.scout_number+=1

    def create_commander(self, slot_number, command):
        address = (self.host, 5400+self.commander_number)
        if address:
            host, port = address
            commander_id = "commander:{}:{}:{}".format(self.id, self.ballot_number, slot_number)
            commander = Commander(self.env, commander_id, self.id, self.config.acceptors, self.config.replicas,
                                  self.ballot_number, slot_number, command, host, port)
            commander.start()
        self.commander_number+=1

    def body(self):
        pass
    #     print "Here I am: ", self.id
    #     self.create_scout()
    #     while True:
    #         msg = self.getNextMessage()
    #         if isinstance(msg, ProposeMessage):
    #             if msg.slot_number not in self.proposals:
    #                 self.proposals[msg.slot_number] = msg.command
    #                 if self.active:
    #                     self.create_commander(msg.slot_number, msg.command)
    #         elif isinstance(msg, AdoptedMessage):
    #             if self.ballot_number == msg.ballot_number:
    #               pmax = {}
    #               for pv in msg.accepted:
    #                   if pv.slot_number not in pmax or pmax[pv.slot_number] < pv.ballot_number:
    #                       pmax[pv.slot_number] = pv.ballot_number
    #                       self.proposals[pv.slot_number] = pv.command
    #               for sn in self.proposals:
    #                   self.create_commander(sn, self.proposals[sn])
    #               self.active = True
    #         elif isinstance(msg, PreemptedMessage):
    #             if msg.ballot_number > self.ballot_number:
    #                 self.active = False
    #                 self.ballot_number = BallotNumber(msg.ballot_number.round+1, self.id)
    #                 self.create_scout()
    #         else:
    #             print "Leader: unknown msg type"

    def handler(self, message):
        if isinstance(message, ProposeMessage):
            self.callback()
            if message.slot_number not in self.proposals:
                self.proposals[message.slot_number] = message.command
                if self.active:
                    self.create_commander(message.slot_number, message.command)
        elif isinstance(message, AdoptedMessage):
            if self.ballot_number == message.ballot_number:
                pmax = {}
                for pv in message.accepted:
                    if pv.slot_number not in pmax or pmax[pv.slot_number] < pv.ballot_number:
                        pmax[pv.slot_number] = pv.ballot_number
                        self.proposals[pv.slot_number] = pv.command
                for sn in self.proposals:
                    self.create_commander(sn, self.proposals[sn])
                self.active = True
        elif isinstance(message, PreemptedMessage):
            if message.ballot_number > self.ballot_number:
                self.active = False
                self.ballot_number = BallotNumber(message.ballot_number.round+1, self.id)
                self.create_scout()
        else:
            print ""