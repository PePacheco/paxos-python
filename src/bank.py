import sys
sys.dont_write_bytecode = True

class bank:
    def __init__(self, proc_id):
        self.clients = {}
        self.accounts = {}
        self.ownerships = []
        self.proc_id = proc_id

    def createClient(self, name, id):
        if id in self.clients:
            self.print_and_log("Client already exists")
        else:
            self.clients[id] = Client(name, id)
            self.print_and_log("Client created with id: "+id)
    
    def createAccount(self, account_id):
        if account_id in self.accounts:
            self.print_and_log("Account already exists")
        else:
            self.accounts[account_id] = Account(id)
            self.print_and_log("Account created with id: "+account_id)
    
    def createAccount_2(self, client_id, account_id):
        if client_id not in self.clients:
            self.print_and_log("Client does not exist")
        elif account_id in self.accounts:
            self.print_and_log("Account already exists")
        else:
            self.createAccount(account_id)
            self.addAccount(client_id, account_id)

    def addAccount(self, client_id, account_id):
        if client_id not in self.clients:
            self.print_and_log("Client does not exist")
        elif account_id not in self.accounts:
            self.print_and_log("Account does not exist")
        else:
            self.ownerships.append(Ownership(account_id, client_id))
            self.print_and_log("Account with id "+account_id+" added to client with id " +client_id)
    
    def deposit(self, account_id, amount):
        if account_id not in self.accounts:
            self.print_and_log("Account does not exist")
        else:
            self.accounts[account_id].addBalance(amount)
            self.print_and_log("Deposited "+amount+" in account with id "+account_id)
    
    def withdraw(self, client_id, account_id, amount):
        if account_id not in self.accounts:
            self.print_and_log("Account does not exist")
        elif client_id not in self.clients:
            self.print_and_log("Client does not exist")
        elif account_id not in self.clients[client_id].get_account(self.ownerships):
            self.print_and_log("Client does not own account")
        else:
            if self.accounts[account_id].subBalance(amount):
                self.print_and_log("Withdraw "+amount+" from account with id "+account_id)
                return True
            else:
                self.print_and_log("Insufficient funds")
                return False
    
    def transfer(self, client_id, from_account_id, to_account_id, amount):
        self.print_and_log("Initiating transfer "+amount+" from account with id "+from_account_id+" to account with id "+to_account_id)
        if to_account_id not in self.accounts:
            self.print_and_log("Account with id "+to_account_id+" does not exist")
        elif from_account_id not in self.accounts:
            self.print_and_log("Account with id "+from_account_id+" does not exist")
        if self.withdraw(client_id, from_account_id, amount):
            self.deposit(to_account_id, amount)

    def balance_2(self, client_id, account_id):
        if client_id not in self.clients:
            self.print_and_log("Client does not exist")
        elif account_id not in self.accounts: 
            self.print_and_log("Account does not exist")
        elif account_id not in self.clients[client_id].get_account(self.ownerships):
            self.print_and_log("Client does not own account")
        else:
            self.print_and_log("Balance of account with id "+str(account_id)+" is "+str(self.accounts[account_id].get_balance()))
        
    def balance(self, client_id):
        if client_id not in self.clients:
            self.print_and_log("Client does not exist")
        else:
            client_accounts = self.clients[client_id].get_account(self.ownerships)
            for acc in client_accounts:
                self.balance_2(client_id, acc)
    
    def print_and_log(self, msg):
        print msg
        file = open("../logs/"+self.proc_id, "a")
        file.write(msg+"\n")
        file.close()

class Account:
    def __init__(self, id):
        self.id = id
        self.balance = 0.0
    
    def get_balance(self):
        return self.balance
    
    def addBalance(self, amount):
        self.balance += float(amount)
    
    def subBalance(self, amount):
        if self.balance >= float(amount):
            self.balance -= float(amount)
            return True
        else:
            return False
    
class Client:
    def __init__(self, name, id):
        self.name = name
        self.id = id
    
    def get_name(self):
        return self.name
    
    def get_account(self, ownerships):
        my_accounts = []
        for o in ownerships:
            if o.client_id == self.id:
                my_accounts.append(o.account_id)
        return my_accounts
        
class Ownership:
    def __init__(self, account, client):
        self.account_id = account
        self.client_id = client