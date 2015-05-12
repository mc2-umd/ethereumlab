import serpent
from pyethereum import tester, utils, abi

serpent_code = '''
def init():
	#Initialiaze the contract creator with 10000 fake dollars
	self.storage[msg.sender] = 10000

def send_currency_to(value, destination):
	#If the sender has enough money to fund the transaction, complete it
	if self.storage[msg.sender] >= value:
		self.storage[msg.sender] = self.storage[msg.sender]  - value
		self.storage[destination] = self.storage[destination] + value
		return(1)
	return(-1)

def balance_check(addr):
	#Balance Check
	return(self.storage[addr])

'''
#Generate public keys
public_k0 = utils.privtoaddr(tester.k0)
public_k1 = utils.privtoaddr(tester.k1)

#Generate state and add contract to block chain
s = tester.state()
print("Tester state created")
c = s.abi_contract(serpent_code)
print("Code added to block chain")

#Test Contract
o = c.send_currency_to(1000, public_k1)
if o == 1:
	print("$1000 sent to tester_k1 from tester_k0")
else:
	print("Failed to send $1000 to tester_k1 from tester_k0")

o = c.send_currency_to(10000, public_k1)
if o == 1:
	print("$10000 sent to tester_k1 from tester_k0")
else:
	print("Failed to send $10000 to tester_k1 from tester_k0")

o = c.balance_check(public_k0)
print("tester_k0 has a balance of " + str(o))

o = c.balance_check(public_k1)
print("tester_k1 has a balance of " + str(o))