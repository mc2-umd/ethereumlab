import serpent
from ethereum import utils, abi
from ethereum.tools import tester

serpent_code = '''
def register(key, value):
	#If not already registered, register it!
	if not self.storage[key]:
		self.storage[key] = value
		return(1)
	else:
		return(-1)

def get(key):
	#Returns -1 if not registered, returns value if registered
	if not self.storage[key]:
		return(-1)
	else:
		return(self.storage[key])
'''

#Create public key
public_k1 = utils.privtoaddr(tester.k1)

#Generate state and add contract to block chain
s = tester.Chain()
print("Tester state created")
c = s.contract(serpent_code,language='serpent')
print("Code added to block chain")

#Test contract
o = c.get("Bob")
if o == -1:
	print("No value has been stored at key \"Bob\"")
else:
	print("The value stored with key \"Bob\" is " + str(o))

o = c.register("Bob", 10)
if(o == 1):
	print("Key \"Bob\" and value 10 was stored!")
else:
	print("Key \"Bob\" has already been assigned")

o = c.register("Bob", 15)
if(o == 1):
	print("Key \"Bob\" and value 10 was stored!")
else:
	print("Key \"Bob\" has already been assigned")

o = c.get("Bob")
if o == -1:
	print("No value has been stored at key \"Bob\"")
else:
	print("The value stored with key \"Bob\" is " + str(o))



