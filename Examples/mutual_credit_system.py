import serpent
from pyethereum import tester, utils, abi

#A mutual credit system will zero out when all debts are paid.

serpent_code = '''
#addr is the public key of the party we are sending the money to
#value is the value of currency we are sending. 
def transfer(addr, value):
    #We are going to max out debt at 1000 credits per person
    if self.storage[msg.sender] - value < -1000:
        return(-1)
    else:
        #If they have not exceeded their debt limit, we do the transaction
        self.storage[msg.sender] -= value
        self.storage[addr] += value
        return(1)

#Simply return the balance at that address
def balance(addr):
    return(self.storage[addr])

'''
public_k0 = utils.privtoaddr(tester.k0)
public_k1 = utils.privtoaddr(tester.k1)

s = tester.state()
c = s.abi_contract(serpent_code)

o = c.balance(public_k0)
print("tester.k0's current balance is " + str(o))

o = c.balance(public_k1)
print("tester.k1's current balance is " + str(o))

o = c.transfer(public_k0, 500, sender=tester.k1)
if o == 1:
	print("500 credits sent to tester_k1 from tester_k0")
else:
	print("Failed to send 500 credits to tester_k1 from tester_k0")

o = c.balance(public_k0)
print("tester.k0's current balance is " + str(o))

o = c.balance(public_k1)
print("tester.k1's current balance is " + str(o))

o = c.transfer(public_k0, 1500, sender=tester.k1)
if o == 1:
	print("1500 credits sent to tester_k1 from tester_k0")
else:
	print("Failed to send 1500 credits to tester_k1 from tester_k0")

o = c.transfer(public_k0, 500, sender=tester.k1)
if o == 1:
    print("500 credits sent to tester_k1 from tester_k0")
else:
    print("Failed to send 500 credits to tester_k1 from tester_k0")

o = c.balance(public_k0)
print("tester.k0's current balance is " + str(o))

o = c.balance(public_k1)
print("tester.k1's current balance is " + str(o))

