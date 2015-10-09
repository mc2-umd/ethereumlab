code = """

constant alice = {}
constant bob = {}
constant deadline = {}



def refund():
   if msg.sender != alice:
      log(type=Notice, text("refund called by other-than-Alice"))
      return(-1)

   if block.blocknumber < deadline: 
      log(type=Notice, text("Too soon for Alice to claim refund"))
      return(-1)

   send(alice, self.balance)


def finalize(sig, amount):
   if msg.sender != bob:
      log(type=Notice, text("finalize called by other-than-Bob"))
      return(-1)

   if !check_signature(alice, sig, amount):
      log(type=Notice, text("bad signature!"))
      return(-1)

   send(bob, amount)
   send(alice, self.balance)

"""



# What are the cases?

# - Bob can choos

# - Bob does not call finalize, Alice claims refund

# - 
