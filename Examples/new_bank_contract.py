import serpent
from ethereum import tester, utils, abi

serpent_code = '''
#Deposit
def deposit():
	self.storage[msg.sender] += msg.value
	return(1)

#Withdraw the given amount (in wei)
def withdraw(amount):
	#Check to ensure enough money in account
	if self.storage[msg.sender] < amount:
		return(-1)
	else:
		#If there is enough money, complete with withdraw
		self.storage[msg.sender] -= amount
		send(0, msg.sender, amount)
		return(1)

#Transfer the given amount (in wei) to the destination's public key
def transfer(amount, destination):
	#Check to ensure enough money in sender's account
	if self.storage[msg.sender] < amount:
		return(-1)
	else:
		#If there is enough money, complete the transfer
		self.storage[msg.sender] -= amount
		self.storage[destination] += amount
		return(1)

#Just return the sender's balance
def balance():
	return(self.storage[msg.sender])
'''

public_k1 = utils.privtoaddr(tester.k1)

s = tester.state()
c = s.abi_contract(serpent_code)

o = c.deposit(value=1000, sender=tester.k0)
if o == 1:
	print("1000 wei successfully desposited to tester.k0's account")
else:
	print("Failed to deposit 1000 wei into tester.k0's account")

o = c.withdraw(1000, sender=tester.k0)
if o == 1:
	print("1000 wei successfully withdrawn from tester.k0's account")
else:
	print("Failed to witdraw 1000 wei into tester.k0's account")

o = c.withdraw(1000, sender=tester.k1)
if o == 1:
	print("1000 wei successfully withdrawn from tester.k1's account")
else:
	print("Failed to witdraw 1000 wei into tester.k1's account")

o = c.deposit(value=1000, sender=tester.k0)
if o == 1:
	print("1000 wei successfully desposited to tester.k0's account")
else:
	print("Failed to deposit 1000 wei into tester.k0's account")

o = c.transfer(500, public_k1, sender=tester.k0)
if o == 1:
	print("500 wei successfully transfered from tester.k0's account to tester.k1's account")
else:
	print("Failed to transfer 500 wei from tester.k0's account to tester.k1's account")

o = c.balance(sender=tester.k0)
print("tester_k0 has a balance of " + str(o))

o = c.balance(sender=tester.k1)
print("tester_k1 has a balance of " + str(o))
