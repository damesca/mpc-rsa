from flask import Flask, jsonify, abort, make_response, request, url_for, redirect
#from flask_httpauth import HTTPTokenAuth
#from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import requests
import json
import ssl
import OpenSSL
import random
from threading import Lock, Thread
from OpenSSL import crypto

app = Flask(__name__)

########################
### AUXILIAR METHODS ###
########################

def create_cert(req, issuer_cert, issuer_sk, serial, valid=365, digest="sha1"):
	"""Generate a certificate given a certificate request."""
	cert = crypto.X509()
	cert.set_serial_number(serial)
	cert.gmtime_adj_notBefore(0)
	cert.gmtime_adj_notAfter(valid * 60 * 60 * 24)
	cert.set_issuer(issuer_cert.get_subject())
	cert.set_subject(req.get_subject())
	cert.set_pubkey(req.get_pubkey())
	cert.sign(issuer_sk, digest)
	return cert

def load_key(filename):
	"""Open a key saved as a PEM file."""
	fp = open(filename, "r")
	dump_key = fp.read()
	fp.close()
	priv_key = crypto.load_privatekey(crypto.FILETYPE_PEM, dump_key)
	return priv_key

def load_cert(filename):
	"""Open a certificate saved as a PEM file."""
	fp = open(filename, "r")
	dump_cert = fp.read()
	fp.close()
	cert = crypto.load_certificate(crypto.FILETYPE_PEM, dump_cert)
	return cert

########################
### REQUEST METHODS  ###
########################

@app.route('/createCertificates', methods=['POST'])
def handler_getCert():

	# Get cert_request from Node
	serial = request.json['serial']
	reqs = request.json['req']
	if len(reqs) != 3:
		print "ERROR - Bad requests array len"
		return json.dumps({ "status": "certError" })
	else:
		obj_req = []
		for dump_req in reqs:
			obj_req.append(crypto.load_certificate_request(crypto.FILETYPE_PEM, dump_req))
			
		# Load CA key and cert
		ca_key = load_key("/ca.key")
		ca_cert = load_cert("/ca.cert")
		dump_ca_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert)

		# Create Node certificates
		dump_certs = []
		for req in obj_req:
			cert = create_cert(req, ca_cert, ca_key, serial)
			dump_certs.append(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

		return json.dumps({ "status": "certOK", "ca_cert": dump_ca_cert, "certs": dump_certs })


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)