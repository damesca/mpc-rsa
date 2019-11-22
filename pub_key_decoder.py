import asn1
import binascii
import gmpy
import math

def os2ip(X):
	xLen = len(X)
	X = X[::-1]
	x = 0
	for i in range(xLen):
		x += int(X[i]) * 256**i
	return x
		

def encryption(m, N, e):
		
	print "m = " + str(m)
	base = gmpy.mpz(m)
	power = gmpy.mpz(e)
	modulus = gmpy.mpz(N)
		
	cyphertext = int(pow(base, power, modulus))
	print "cypher = " + str(cyphertext)


f = open("pub_key.txt", "r")

if f.mode == 'r':
	hexkey = f.read()

pubK = binascii.unhexlify(hexkey)

decoder = asn1.Decoder()
decoder.start(pubK)
tag1, N = decoder.read()
tag2, e = decoder.read()
print "N: " + str(N)
print "e: " + str(e)

hsesK = "f1c45ea1193d4c07e594cdfbef2a1a6eba2c13b0a2a1d364"
sesK = binascii.unhexlify(hsesK)
isesK = int(hsesK, 16)

print "sesK: " + hsesK
print "(int)sesK: " + str(isesK)

encryption(isesK, N, e)

print hex(isesK)




