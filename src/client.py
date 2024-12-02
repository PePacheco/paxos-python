import threading
import time
import random
from Queue import Queue

class Client:
    def __init__(self, client_id, env):
 
        self.client_id = client_id
        self.env = env
        self.command_queue = Queue()
        self.lock = threading.Lock()

    def add_command(self, command):
        self.command_queue.put(command)
        # #print "Cliente {}: Comando '{}' adicionado a fila.".format(self.client_id, command)
    
    def set_command_queue(self, command_list):

        for command in command_list:
            self.command_queue.put(command)
        # #print "Cliente {}: Fila de comandos configurada com {} comandos.".format(self.client_id, len(command_list))

    def process_commands(self):

        while not self.command_queue.empty():
            command = self.command_queue.queue[0]
            # #print "Cliente {}: Tentando enviar comando '{}'.".format(self.client_id, command)
            self.send_command(command)

    def send_command(self, command):
        with self.lock: 
            # #print "Cliente {}: Enviando comando '{}' para o lider.".format(self.client_id, command)
            
            success = self.env.process_command(self.client_id, command)

            if success:
                print "Cliente {}: Comando '{}' foi ACEITO pelo lider.".format(self.client_id, command)
                self.command_queue.get()  
            else:
                #print "Cliente {}: Comando '{}' foi REJEITADO. Tentando novamente...".format(self.client_id, command)
                time.sleep(random.uniform(0.5, 2)) 
