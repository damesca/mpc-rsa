from oscrypto import asymmetric
from certbuilder import CertificateBuilder, pem_armor_certificate
from binascii import hexlify, unhexlify
import socket
import requests
from asn1crypto import keys, core
import json
import sys

f = open("orqIp.txt", "r")
orq_ip = f.read()
f.close()

keyId = sys.argv[1]

r = requests.get("http://" + orq_ip + ":5000/getKey/" + keyId)
response = dict(json.loads(r.text))
pub_key = response["pubKey"]
asn1PublicKey = core.Asn1Value.load(unhexlify(pub_key))
publicKey = keys.PublicKeyInfo.wrap(asn1PublicKey, u'rsa')

builder = CertificateBuilder(
	{
		u'country_name': u'SP',
		u'state_or_province_name': u'Malaga',
		u'locality_name': u'Malaga',
		u'organization_name': u'NICS Lab',
		u'common_name': u'Certificacion Raiz'
	},
	publicKey
)
builder.self_signed = True
builder.ca = True

root_ca_certificate = builder.build_mpc(int(keyId), orq_ip, "5000")

with open('certificado_raiz.crt', 'wb') as f:
	f.write(pem_armor_certificate(root_ca_certificate))

