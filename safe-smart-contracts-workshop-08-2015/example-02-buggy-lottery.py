from ethereum import tester
import os

contract_code = """
event Notice(x:str)

alice = 0x{alice}
bob = 0x{bob}

def load_money():
   # Must pay before time #1
   if block.number > 1: 
      log(type=Notice, text("load_money: called after block 1"))
      return(0)

   if msg.value != 10*(10**21):
      log(type=Notice, text("load_money: wrong amount"))
      return(0)

   if msg.sender == alice:
      log(type=Notice, text("load_money: Alice OK!"))

   if msg.sender == bob:
      log(type=Notice, text("load_money: Bob OK!"))

   # Mark user as having paid
   self.storage[msg.sender] = 1 

def cash_out():
   # Critical block is #2
   # Must wait for block #3 to cash out
   if block.number < 3:
      log(type=Notice, text("cash_out: called before block 3"))
      return(0)

   if not self.storage[alice]:
      log(type=Notice, text("cash_out: Alice didn't pay!"))
      send(bob, self.balance)
      return(0)

   if not self.storage[bob]:
      log(type=Notice, text("cash_out: Bob didn't pay!"))
      send(alice, self.balance)
      return(0)

   block2 = block.prevhash(block.number - 2)
   if block2 % 2 == 0:
      log(type=Notice, text("cash_out: Alice won!"))
      send(alice, self.balance)

   else:
      log(type=Notice, text("cash_out: Bob won!"))
      send(bob, self.balance)

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
                                 bob=bob.encode('hex'))
contract = s.abi_contract(full_code)

# Both parties deposit money
contract.load_money(value=int(10E21), sender=tester.k0) # Alice
contract.load_money(value=int(10E21), sender=tester.k1) # Bob

# Mine some blocks
s.block.extra_data = os.urandom(20) # Add actual randomness
s.mine(3)

# Run the cash_out 
contract.cash_out()

print 'Final balances:'
print 'Alice: %.2f' % (float(s.block.get_balance(alice)) / 10E21)
print '  Bob: %.2f' % (float(s.block.get_balance(bob)) / 10E21)
