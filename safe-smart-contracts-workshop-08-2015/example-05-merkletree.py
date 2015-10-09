from ethereum import tester
from ethereum import utils
from ethereum import slogging
import bitcoin

ecrecover_code = """

data gStr[]
data pos

#macro check_pubkey($address, $pubkey):
#    def parseTransaction(rawTx:str, outNum):
#    save(self.gStr[0], $hexStr, chars=len($hexStr))

# ecrecover already returns the address, in 'int' form
macro verify_signature($addr, $h, $v, $r, $s):
    $addr == ecrecover($h, $v, $r, $s)

"""
