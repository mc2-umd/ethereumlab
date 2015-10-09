from ethereum import tester
from ethereum import utils
from ethereum import slogging
import rlp

file_chunks = [
 "A  purely peer-to-peer",
 "version of electronic",
 "cash would allow online",
 "payments to be sent directly",
 "from one party to another",
 "without going through a",
 "financial institution.",
 "Digital signatures provide",
 "part of the solution, but",
 "the main benefits are lost",
 "if a trusted third party",
 "is still required to prevent",
 "double-spending. We propose",
 "a solution to the double",
 "-spending problem using a",
 "peer-to-peer network."]

zfill = lambda s: (32-len(s))*'\x00' + s
file_chunks = map(zfill, file_chunks)

contract_code = """

root = 0x{}

macro hash_node($h, $sibling, $bit):
    if $bit == 0:
        sha3([$h, $sibling], items=2)
    else:
        sha3([$sibling, $h], items=2)

def check_index(x:bytes32, bits:uint8[4], siblings:bytes32[4]):
    h = hash_node(x, siblings[0], bits[0])
    return(h:bytes32)
"""

# Build the merkle tree
layer_1 = [utils.sha3(file_chunks[2*i+0] + file_chunks[2*i+1])
           for i in range(8)]
layer_2 = [utils.sha3(layer_1[2*i+0] + layer_1[2*i+1])
           for i in range(4)]
layer_3 = [utils.sha3(layer_2[2*i+0] + layer_2[2*i+1])
           for i in range(2)]
root_hash = utils.sha3(layer_3[0] + layer_3[1])


def index_to_bits(ind):
    bits = []
    for i in range(4):
        bits.append(ind % 2)
        ind /= 2
    return bits

def get_siblings(bits):
    assert len(bits) == 4
    if bits[3] == 0: sibling3 = layer_3[1]
    else: sibling3 = layer_3[0]

    offset = bits[3]*2
    if bits[2] == 0: sibling2 = layer_2[offset+1]
    else: sibling2 = layer_2[offset]

    offset = 2*offset + bits[2]*2
    if bits[1] == 0: sibling1 = layer_1[offset+1]
    else: sibling1 = layer_1[offset]

    offset = 2*offset + bits[1]*2
    if bits[0] == 0: sibling0 = file_chunks[offset+1]
    else: sibling0 = file_chunks[offset]

    return [sibling0, sibling1, sibling2, sibling3]

s = tester.state()
c = s.abi_contract(contract_code.format(root_hash.encode('hex')))

o = c.check_index(file_chunks[0], [0,0,0,0], [file_chunks[1]]*4)
print o.encode('hex')
