import serpent
from ethereum import utils, abi
from ethereum.tools import tester
serpent_code = '''
data player[2](address, choice)
data num_players
data reward
data check_winner[3][3]    # captures the rules of rock-paper-scissors game

def init():
	#If 2, tie
	#If 0, player 0 wins
	#If 1, player 1 wins

	#0 = rock
	#1 = paper
	#2 = scissors

	self.check_winner[0][0] = 2
	self.check_winner[1][1] = 2
	self.check_winner[2][2] = 2

	#Rock beats scissors
	self.check_winner[0][2] = 0
	self.check_winner[2][0] = 1

	#Scissors beats paper
	self.check_winner[2][1] = 0
	self.check_winner[1][2] = 1

	#Paper beats rock
	self.check_winner[1][0] = 0
	self.check_winner[0][1] = 1

	self.num_players = 0

#adds players who send 1000 wei to the contract to the game
def add_player(choice):
	if self.num_players < 2 and msg.value == 1000:
		self.reward = self.reward + msg.value
		self.player[self.num_players].address = msg.sender
		self.player[self.num_players].choice = choice
		self.num_players = self.num_players + 1
		return(0)
	else:
		return(-1)


def check():
	p0_choice = self.player[0].choice
	p1_choice = self.player[1].choice
	#If player 0 wins
	if self.check_winner[p0_choice][p1_choice] == 0:
		send(0,self.player[0].address, self.reward)
		return(0)
	#If player 1 wins
	elif self.check_winner[p0_choice][p1_choice] == 1:
		send(0,self.player[1].address, self.reward)
		return(1)
	#If no one wins
	else:
		send(0,self.player[0].address, self.reward/2)
		send(0,self.player[1].address, self.reward/2)
		return(2)

def balance_check():
	log(self.player[0].address.balance)
	log(self.player[1].address.balance)

'''

s = tester.Chain()
c = s.contract(serpent_code,language='serpent')

o = c.add_player(2,value=1000,sender=tester.k0)
print("Player 1 Added: {}").format(o)

o = c.add_player(1,value=1000,sender=tester.k1)
print("Player 2 Added: {}\n").format(o)

print("Player one chooses 2 which is: Scissors")

print("Player two chooses 1 which is: Paper\n")

o = c.check(sender=tester.k1)
print("Check says player {} wins\n").format(o)

c.balance_check(sender=tester.k1)



c = s.abi_contract(serpent_code)

o = c.add_player(1,value=1000,sender=tester.k0)
print("Player 1 Added: {}").format(o)

o = c.add_player(2,value=1000,sender=tester.k1)
print("Player 2 Added: {}\n").format(o)

print("Player one chooses 1 which is: paper")

print("Player two chooses 2 which is: scissors\n")

o = c.check(sender=tester.k1)
print("Check says player {} wins\n").format(o)

c.balance_check(sender=tester.k1)

c = s.abi_contract(serpent_code)

o = c.add_player(1,value=1000,sender=tester.k0)
print("Player 1 Added: {}").format(o)

o = c.add_player(1,value=1000,sender=tester.k1)
print("Player 2 Added: {}\n").format(o)

print("Player one chooses 1 which is: paper")

print("Player two chooses 1 which is: paper\n")

o = c.check(sender=tester.k1)
print("Check says player {} wins\n").format(o)

c.balance_check(sender=tester.k1)

c = s.abi_contract(serpent_code)

o = c.add_player(0,value=1000,sender=tester.k0)
print("Player 1 Added: {}").format(o)

o = c.add_player(1,value=1000,sender=tester.k1)
print("Player 2 Added: {}\n").format(o)

print("Player one chooses 0 which is: rock")

print("Player two chooses 1 which is: paper\n")

o = c.check(sender=tester.k1)
print("Check says player {} wins\n").format(o)

c.balance_check(sender=tester.k1)



c = s.abi_contract(serpent_code)

o = c.add_player(0,value=1000,sender=tester.k0)
print("Player 1 Added: {}").format(o)

o = c.add_player(1,value=1000,sender=tester.k1)
print("Player 2 Added: {}\n").format(o)

print("Player one chooses 0 which is: rock")

print("Player two chooses 2 which is: scissors\n")

o = c.check(sender=tester.k1)
print("Check says player {} wins\n").format(o)

c.balance_check(sender=tester.k1)



