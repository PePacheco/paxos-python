import threading
import time
import random
from Queue import Queue

class Cliente:
    def __init__(self, client_id, leader):
        """
        Inicializa o cliente.

        Args:
            client_id (str): Identificador único para o cliente.
            leader (Leader): Instância do líder que o cliente comunica.
        """
        self.client_id = client_id
        self.leader = leader
        self.command_queue = Queue()
        self.lock = threading.Lock()

    def add_command(self, command):
        """
        Adiciona um comando à fila do cliente.

        Args:
            command (str): O comando a ser adicionado à fila.
        """
        self.command_queue.put(command)
        print "Cliente {}: Comando '{}' adicionado à fila.".format(self.client_id, command)

    def process_commands(self):
        """
        Processa os comandos na fila do cliente.
        """
        while not self.command_queue.empty():
            command = self.command_queue.queue[0]  # Olha o primeiro comando na fila sem removê-lo
            print "Cliente {}: Tentando enviar comando '{}'.".format(self.client_id, command)
            self.send_command(command)

    def send_command(self, command):
        """
        Envia um comando para o líder.

        Args:
            command (str): O comando que o cliente deseja enviar.
        """
        with self.lock:  # Garante que apenas um comando seja enviado por vez
            print "Cliente {}: Enviando comando '{}' para o líder.".format(self.client_id, command)
            
            # Simula a comunicação com o líder
            success = self.leader.process_command(self.client_id, command)

            if success:
                print "Cliente {}: Comando '{}' foi aceito pelo líder.".format(self.client_id, command)
                self.command_queue.get()  # Remove o comando da fila após sucesso
            else:
                print "Cliente {}: Comando '{}' foi rejeitado. Tentando novamente...".format(self.client_id, command)
                time.sleep(random.uniform(0.5, 2))  # Aguarda um tempo aleatório antes de tentar novamente
