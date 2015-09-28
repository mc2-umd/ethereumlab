import serpent
from ethereum import tester, utils, abi
from sha3 import sha3_256
import sys
import struct
import binascii
import pytest

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

#adds two players to the contract
def add_player():
	#prevents a max callstack exception
	if self.test_callstack() != 1: return(-1)

	#runs if there are no players
	if not self.storage["player1"]:
		if msg.value >= 1000:
			self.storage["WINNINGS"] = self.storage["WINNINGS"] + msg.value
			self.storage["player1"] = msg.sender
			#returns any funds sent to the contract over 1000
			if msg.value - 1000 > 0:
				send(25,msg.sender,msg.value-1000)
			return(1)
		else:
			#if they don't send at least 1000, they aren't added and money is refunded
			send(25,msg.sender,msg.value)
			return(0)
	#if player1 is setup
	elif not self.storage["player2"]:
		if msg.value >= 1000:
			self.storage["WINNINGS"] = self.storage["WINNINGS"] + msg.value
			self.storage["player2"] = msg.sender
			if msg.value - 1000 > 0:
				send(25,msg.sender,msg.value-1000)
			return(2)
		else:
			send(25,msg.sender,msg.value)
			return(0)
	#if the game is full, anyone else who tries to join gets a refund
	else:
		send(25,msg.sender,msg.value)
		return(0)

#accepts a hash from the player in form sha3(address, choice, nonce)
def input(player_commitment):
	if self.test_callstack() != 1: return(-1)

	if self.storage["player1"] == msg.sender:
		self.storage["p1commit"] = player_commitment
		return(1)
	elif self.storage["player2"] ==  msg.sender:
		self.storage["p2commit"] = player_commitment
		return(2)
	else:
		return(0)

#verifies the choice in their committed answer matches
def open(choice, nonce):
	if self.test_callstack() != 1: return(-1)

	if self.storage["player1"] == msg.sender:
		if sha3([msg.sender, choice, nonce], items=3) == self.storage["p1commit"]:
			#if the commitment was verified the plaintext option is stored for finding winner
			self.storage["p1value"] = choice
			#boolean flag to mark correct commitment opening
			self.storage["p1reveal"] = 1
			#a timer is put in place to call check() in case other player doesn't open
			if self.storage["timer_start"] == null:
				self.storage["timer_start"] = block.number
			return(1)
		else:
			return(0)
	elif self.storage["player2"] == msg.sender:
		if sha3([msg.sender, choice, nonce], items=3) == self.storage["p2commit"]:
			self.storage["p2value"] = choice
			self.storage["p2reveal"] = 1
			if self.storage["timer_start"] == null:
				self.storage["timer_start"] = block.number
			return(2)
		else:
			return(0)
	else:
		return(-1)

def check():
	if self.test_callstack() != 1: return(-3)

	#Check to make sure at least 10 blocks have been given for both players to reveal their play.
	if block.number - self.storage["timer_start"] < 10: return(-2)

	#check to see if both players have revealed answer
	if self.storage["p1reveal"] == 1 and self.storage["p2reveal"] == 1:
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
			send(100,self.storage["player1"], 1000)
			send(100,self.storage["player2"], 1000)
			return(0)
	#if p1 revealed but p2 did not, send money to p1
	elif self.storage["p1reveal"] == 1 and not self.storage["p2reveal"] == 1:
		send(100,self.storage["player1"], self.storage["WINNINGS"])
		return(1)
	#if p2 revealed but p1 did not, send money to p2
	elif not self.storage["p1reveal"] == 1 and self.storage["p2reveal"] == 1:
		send(100,self.storage["player2"], self.storage["WINNINGS"])
		return(2)
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

o = c.add_player(value=1000, sender=tester.k0)
print("Player 1 Added: {}").format(o)

o = c.add_player(value=1000, sender=tester.k1)
print("Player 2 Added: {}\n").format(o)

##################################### SETUP COMMITMENTS ########################################
choice = ["rock", "paper", "scissors"]

tobytearr = lambda n, L: [] if L == 0 else tobytearr(n / 256, L - 1)+[n % 256]

choice1 = 0x01
nonce1 = 0x01
ch1 = ''.join(map(chr, tobytearr(choice1, 32)))
no1 = ''.join(map(chr, tobytearr(nonce1, 32)))
print("Player one chooses {} which is: {}").format(choice1, choice[choice1])

k0_pub_addr_hex = utils.privtoaddr(tester.k0)

## Prepare and pad the address 
k0_pub_addr  = ''.join(map(chr, tobytearr(long(k0_pub_addr_hex,16),32)))

## Now use it for the commitment
s1 = ''.join([k0_pub_addr, ch1, no1])
comm1 = utils.sha3(s1)

choice2 = 0x02
nonce2 = 0x01
ch2 = ''.join(map(chr, tobytearr(choice2, 32)))
no2 = ''.join(map(chr, tobytearr(nonce2, 32)))
print("Player two chooses {} which is: {}\n").format(choice2, choice[choice2])

k1_pub_addr_hex = utils.privtoaddr(tester.k1)
#print(type(k1_pub_addr_hex))  ## This is an encoded hex string .. cannot be used directly

## Prepare and pad the address 
k1_pub_addr  = ''.join(map(chr, tobytearr(long(k1_pub_addr_hex,16),32)))

## Now use it for the commitment
s2 = ''.join([k1_pub_addr, ch2, no2])
comm2 = utils.sha3(s2)

o = c.input(comm1, sender=tester.k0)
print("Input for player 1: {}").format(o)

o = c.input(comm2, sender=tester.k1)
print("Input for player 2: {}\n").format(o)

o = c.open(0x01,0x01, sender=tester.k0)
print("Open for player 1: {}").format(o)

o = c.open(0x02,0x01, sender=tester.k1)
print("Open for player 2: {}\n").format(o)

s.mine(11) # needed to move the blockchain at least 10 blocks so check can run

o = c.check(sender=tester.k1)
print("Check says player {} wins\n").format(o)

c.balance_check(sender=tester.k0)
