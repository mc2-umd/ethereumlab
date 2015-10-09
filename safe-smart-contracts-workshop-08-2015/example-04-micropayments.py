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

def finalize((v,r,s), amount):
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
                                 deadline=100)
print full_code
contract = s.abi_contract(full_code)

# zfill: left-pads a string with 0's until 32 bytes
zfill = lambda s: (32-len(s))*'\x00' + s

# Both parties deposit money
#s.mine(3)
#contract.load_money(value=int(10E21), sender=tester.k0) # Alice
#contract.load_money(value=int(10E21), sender=tester.k1) # Bob

# Mine some blocks
#s.block.extra_data = os.urandom(20) # Add actual randomness
#s.mine(3)

# Run the cash_out 
#contract.cash_out()

#print 'Final balances:'
#print 'Alice: %.2f' % (float(s.block.get_balance(alice)) / 10E21)
#print '  Bob: %.2f' % (float(s.block.get_balance(bob)) / 10E21)






# What are the cases?

# - Bob can choos

# - Bob does not call finalize, Alice claims refund

# - 
