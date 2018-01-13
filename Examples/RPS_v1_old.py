import serpent
from ethereum import utils, abi
from ethereum.tools import tester

serpent_code = '''
data winnings_table[3][3]

def init():
	#If 0, tie
	#If 1, player 1 wins
	#If 2, player 2 wins

	#0 = rock
	#1 = paper
	#2 = scissors

	self.winnings_table[0][0] = 0
	self.winnings_table[1][1] = 0
	self.winnings_table[2][2] = 0

	#Rock beats scissors
	self.winnings_table[0][2] = 1
	self.winnings_table[2][0] = 2

	#Scissors beats paper
	self.winnings_table[2][1] = 1
	self.winnings_table[1][2] = 2

	#Paper beats rock
	self.winnings_table[1][0] = 1
	self.winnings_table[0][1] = 2

	self.storage["MAX_PLAYERS"] = 2
	self.storage["WINNINGS"] = 0

#adds players who send value to the contract to the game
def add_player():
	if not self.storage["player1"]:
		if msg.value == 1000:
			self.storage["WINNINGS"] = self.storage["WINNINGS"] + msg.value
			self.storage["player1"] = msg.sender
			return(1)
		return (0)
	elif not self.storage["player2"]:
		if msg.value == 1000:
			self.storage["WINNINGS"] = self.storage["WINNINGS"] + msg.value
			self.storage["player2"] = msg.sender
			return(2)
		return (0)
	else:
		return(0)

#stores input "choice" as the respective player's choice
def input(choice):
	if self.storage["player1"] == msg.sender:
		self.storage["p1value"] = choice
		return(1)
	elif self.storage["player2"] ==  msg.sender:
		self.storage["p2value"] = choice
		return(2)
	else:
		return(0)

def check():
	#If player 1 wins
	if self.winnings_table[self.storage["p1value"]][self.storage["p2value"]] == 1:
		send(100,self.storage["player1"], self.storage["WINNINGS"])
		return(1)
	#If player 2 wins
	elif self.winnings_table[self.storage["p1value"]][self.storage["p2value"]] == 2:
		send(100,self.storage["player2"], self.storage["WINNINGS"])
		return(2)
	#If no one wins
	else:
		send(100,self.storage["player1"], self.storage["WINNINGS"]/2)
		send(100,self.storage["player2"], self.storage["WINNINGS"]/2)
		return(0)

def balance_check():
	log(self.storage["player1"].balance)
	log(self.storage["player2"].balance)
'''

s = tester.Chain()
c = s.contract(serpent_code,language='serpent')

o = c.add_player(value=1000,sender=tester.k0)
print("Player 1 Added: {}").format(o)

o = c.add_player(value=1000,sender=tester.k1)
print("Player 2 Added: {}\n").format(o)

o = c.input(2, sender=tester.k0)
print("Player one chooses 2 which is: Scissors")

o = c.input(1, sender=tester.k1)
print("Player two chooses 1 which is: Paper\n")

o = c.check(sender=tester.k1)
print("Check says player {} wins\n").format(o)

c.balance_check(sender=tester.k1)
