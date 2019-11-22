from Crypto.Util.asn1 import DerSequence, DerBitString
from binascii import hexlify, unhexlify
import sys


'''
Formato DER para codificar una clave RSA:
	SEQUENCE (2 elem)
		SEQUENCE (2 elem)
			OBJECT IDENTIFIER 1.2.840.113549.1.1.1
			NULL
		BIT STRING (1 elem)
			SEQUENCE (2 elem)
				INTEGER modulus
				INTEGER exponent
'''

print sys.argv[1]
print sys.argv[2]

modulus = int(sys.argv[1])
exponent = int(sys.argv[2])

# Codificacion HEX-DER del SEQUENCE(OID, NULL)
oid_seq = '300d06092a864886f70d0101010500'

# Codificacion DER del SEQUENCE(INTEGER, INTEGER)
int_seq = DerSequence()
int_seq.append(modulus)
int_seq.append(exponent)
int_seq = int_seq.encode()

# Codificacion DER del BIT STRING(...)
bs_der = DerBitString(int_seq)
bs_der = bs_der.encode()

# Codificacion DER del SEQUENCE(SEQUENCE, BIT STRING)
rsa_seq = DerSequence()
rsa_seq.append(unhexlify(oid_seq))
rsa_seq.append(bs_der)
rsa_seq = rsa_seq.encode()

# Exportar la clave publica formateada en hexadecimal a un fichero
f = open(sys.argv[3] + "/pub_key.txt", "w+")
f.write(hexlify(bytearray(rsa_seq)))
f.close()

