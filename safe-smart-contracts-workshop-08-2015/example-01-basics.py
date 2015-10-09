from ethereum import tester

# Logging (change to "trace" to see more)
#from ethereum import slogging
#slogging.set_level('eth.pb.tx', 'warning')
#slogging.set_level('eth.vm.op', 'warning')

# Serpent code
contract_code = """
event Notice(x:str)

def test_function(x):
   log(type=Notice, text("Hello World!"))

   self.storage[0] = x
   self.storage[0xDEAD] = 0xBEEF
   self.storage["Hello"] = "World!"
   self.storage[1] = 10 + 1245 + 320   # 1575 = 0x0627

"""

s = tester.state()

# Create the contract
full_code = contract_code
contract = s.abi_contract(full_code)

# Invoke a method (in the local "mempool", to go in the next block)
contract.test_function("C0FFEEBABE".decode('hex'))

# Mine blocks
s.mine(10)

# Inspect the contract storage
def simplify_trie(trie):
    return dict((k.encode('hex'), v[1:].encode('hex')) 
                for k,v in trie.to_dict().iteritems())

for k,v in simplify_trie(s.block.get_storage(contract.address)).iteritems():
    print k,v

# Print the balance of Alice
#print "[1] Alice' balance", s.block.get_balance(alice)
#s.send(tester.k0, contract.address, 1)
#print "[2] Alice' balance", s.block.get_balance(alice)


# Look at compiled code
# print serpent.pretty_compile(contract_code)

# Look at intermediate LLL language
# print serpent.pretty_compile(contract_code)
