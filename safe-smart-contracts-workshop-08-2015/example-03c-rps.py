import serpent
from ethereum import tester, utils, abi
from sha3 import sha3_256
import sys
import struct
import binascii

serpent_code = '''
data player[2](address, commit, choice, has_revealed)
data num_players
data reward
data timer_start
data check_winner[3][3]

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

#accepts a hash from the player in form sha3(address, choice, nonce)
def add_player(player_commitment):
	#prevents a max callstack exception
	if self.test_callstack() != 1: return(-1)

	if self.num_players < 2 and msg.value >= 1000:
		self.reward = self.reward + msg.value
		self.player[self.num_players].address = msg.sender
		self.player[self.num_players].commit = player_commitment
		self.num_players = self.num_players + 1
		if msg.value - 1000 > 0:
			send(0, msg.sender, msg.value-1000)
		return(0)

	else:	
		if msg.value > 0 :
			# prevent unnecessary leakage of money
			send(0, msg.sender, msg.value)
		return(-1)
		
#verifies the choice in their committed answer matches
def open(choice, nonce):
	if self.test_callstack() != 1: return(-1)

	#Ensure two players are in the contract
	if not num_players == 2: return(-1)

	#Determine which player submitted the open request
	if msg.sender == self.player[0].address:
		player_num = 0
	elif msg.sender == self.player[1].address:
		player_num = 1
	else:
		return(-1)

	#Check the commitment and ensure they have not tried to commit already
	if sha3([msg.sender, choice, nonce], items=3) == self.player[player_num].commit and not self.player[player_num].has_revealed:
		#If commitment verified, we should store choice in plain text
		self.player[player_num].choice = choice
		#Store current block number to give other player 10 blocks to open their commit
		self.player[player_num].has_revealed = 1		

		if not self.timer_start:
			self.timer_start = block.number

		return(0)
	else:
		return(-1)

def check():
	if self.test_callstack() != 1: return(-1)

	#Check to make sure at least 10 blocks have been given for both players to reveal their play.
	if block.number - self.timer_start < 10: return(-2)

	#check to see if both players have revealed answer
	if self.player[0].has_revealed and self.player[1].has_revealed:
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

	#if p1 revealed but p2 did not, send money to p1
	elif self.player[0].has_revealed and not self.player[1].has_revealed:
		send(0,self.player[0].address, self.reward)
		return(0)

	#if p2 revealed but p1 did not, send money to p2
	elif not self.player[0].has_revealed and self.player[1].has_revealed:
		send(0,self.player[1].address, self.reward)
		return(1)

	#if neither p1 nor p2 revealed, keep both of their bets
	else:
		return(-1)

#returns the balance to ensure funds were lost and won properly
def balance_check():
	log(self.storage["player1"].balance)
	log(self.storage["player2"].balance)

def test_callstack():
	return(1)
'''

s = tester.state()
c = s.abi_contract(serpent_code)

print("Output of 1 designated success for player 1.")
print("Output of 2 designated success for player 2.")
print("Output of 0 designated a tie.\n")
print("Output of -1 designated an error.\n")

##################################### SETUP COMMITMENTS ########################################
choice = ["rock", "paper", "scissors"]

# Use default addresses for Alice and Bob
alice = tester.a0
alice_key = tester.k0
bob = tester.a1
bob_key = tester.k1

tobytearr = lambda n, L: [] if L == 0 else tobytearr(n / 256, L - 1)+[n % 256]
zfill = lambda s: (32-len(s))*'\x00' + s

choice1 = random.randint(0,2)
nonce1 = random.randint(0,2**32-1)
ch1 = ''.join(map(chr, tobytearr(choice1, 32)))
no1 = ''.join(map(chr, tobytearr(nonce1, 32)))
print("Alice chooses {} which is: {}").format(choice1, choice[choice1])



## Use Alice's address for the commitment
s1 = ''.join([zfill(alice), ch1, no1])
comm1 = utils.sha3(s1)

choice2 = random.randint(0,2)
nonce2 = random.randint(0,2**32-1)
ch2 = ''.join(map(chr, tobytearr(choice2, 32)))
no2 = ''.join(map(chr, tobytearr(nonce2, 32)))
print("Bob chooses {} which is: {}\n").format(choice2, choice[choice2])

## Use Bob's address for the commitment
s2 = ''.join([zfill(bob), ch2, no2])
comm2 = utils.sha3(s2)

o = c.add_player(comm1, value=1000, sender=alice_key)
print("Alice Added: {}").format(o)

o = c.add_player(comm2, value=1000, sender=bob_key)
print("Bob Added: {}\n").format(o)

o = c.open(choice1,nonce1, sender=alice_key)
print("Open for Alice: {}").format(o)

o = c.open(choice2,nonce2, sender=bob_key)
print("Open for Bob: {}\n").format(o)

s.mine(11) # needed to move the blockchain at least 10 blocks so check can run

o = c.check(sender=tester.k1)
if o == 2: print('Tied!')
elif o == 0: print("Alice won!")
elif o == 1: print("Bob won!")

c.balance_check(sender=tester.k0)
