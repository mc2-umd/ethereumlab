from ethereum import tester, utils
import bitcoin
import os

contract_code = """
event Notice(x:str)

alice = 0x{alice}
bob = 0x{bob}
deadline = {deadline}

macro verify_signature($addr, $h, $v, $r, $s):
    $addr == ecrecover($h, $v, $r, $s)

def refund():
   if msg.sender != alice:
      log(type=Notice, text("refund called by other-than-Alice"))
      return(-1)

   if block.number < deadline: 
      log(type=Notice, text("Too soon for Alice to claim refund"))
      return(-1)

   send(alice, self.balance)

def finalize(v,r,s, amount):
   if msg.sender != bob:
      log(type=Notice, text("finalize called by other-than-Bob"))
      return(-1)

   if !verify_signature(alice, sha3(amount), v, r, s):
      log(type=Notice, text("bad signature!"))
      return(-1)

   send(bob, amount)
   send(alice, self.balance)

"""

s = tester.state()

# Use default addresses for Alice and Bob
alice = tester.a0
bob = tester.a1

print 'Initial balances:'
print 'Alice: %.2f' % (float(s.block.get_balance(alice)) / 10E21)
print '  Bob: %.2f' % (float(s.block.get_balance(bob)) / 10E21)

# Create the contract
full_code = contract_code.format(alice=alice.encode('hex'),
                                 bob=bob.encode('hex'),
                                 deadline=10)
contract = s.abi_contract(full_code)

# zfill: left-pads a string with 0's until 32 bytes
zfill = lambda s: (32-len(s))*'\x00' + s


# Alice deposit 30
s.mine(3)
s.send(tester.k0, contract.address, int(30*10E21))
print 'After Deposit Balances:'
print 'Alice: %.2f' % (float(s.block.get_balance(alice)) / 10E21)
print '  Bob: %.2f' % (float(s.block.get_balance(bob)) / 10E21)
print 'Contract: %.2f' % ( float(s.block.get_balance(contract.address)) / 10E21 )

# The payment signature
def sigamt(amount, priv=tester.k0):
   amount = utils.int_to_bytes(amount)
   amount = zfill(amount)
   pub = bitcoin.privtopub(priv)
   amthash = utils.sha3(amount)
   V, R, S = bitcoin.ecdsa_raw_sign(amthash, priv)
   assert bitcoin.ecdsa_raw_verify(amthash, (V,R,S), pub)
   return V,R,S

# first payment
pay5 = sigamt(int(5*10E21))
# second payment
pay10 = sigamt(int(10*10E21))

# Bob calls finalize
V,R,S = pay10
fval = int(10*10E21)
contract.finalize(V,R,S, fval, sender=tester.k1)

s.mine(3)
print 'Finalized Balanced:'
print 'Alice: %.2f' % (float(s.block.get_balance(alice)) / 10E21)
print '  Bob: %.2f' % (float(s.block.get_balance(bob)) / 10E21)
print 'Contract: %.2f' % ( float(s.block.get_balance(contract.address)) / 10E21 )




# What are the cases?

# - Bob can choos

# - Bob does not call finalize, Alice claims refund

# - 
