#!/usr/bin/python

import random
import math
import gmpy
import time

import asn1
import binascii
import subprocess
from subprocess import Popen
import sys
from twisted.internet.defer import inlineCallbacks, returnValue

from optparse import OptionParser
from twisted.internet import reactor

from viff.field import GF
from viff.runtime import Runtime, create_runtime, gather_shares, make_runtime_class, Share
from viff.comparison import ComparisonToft07Mixin, Toft05Runtime
from viff.config import load_config
from viff.util import rand, find_prime
from viff.equality import ProbabilisticEqualityMixin

class Protocol:

	def import_params(self):
		# Importar los parametros particulares de cada parte: N y d (necesarios para firmar)
		if self.runtime.id == 1:
			f = open("/viff/apps/key" + sys.argv[2] + "/values-1.txt", "r")
		elif self.runtime.id == 2:
			f = open("/viff/apps/key" + sys.argv[2] + "/values-2.txt", "r")
		elif self.runtime.id == 3:
			f = open("/viff/apps/key" + sys.argv[2] + "/values-3.txt", "r")
	
		self.n_revealed = int(f.readline())
		self.d = int(f.readline())
		f.close()

		print "N: " + str(self.n_revealed)
		print "d: " + str(self.d)

		# Importar el mensaje guardado en buffer que se quiere firmar
		f = open("/viff/apps/key" + sys.argv[2] + "/buffer.txt", "r")
		self.message = int(f.readline())
		f.close()
		print "Hash: " + str(self.message)
		
		self.signature(self.message)


	def get_primes(self, min, max):
		primes = []
		while True:
			prime = int(gmpy.next_prime(min))
			if prime <= max:
				primes += [prime]
				min = prime
			else:
				return primes

		
	def signature(self, message):
		if self.runtime.id == 1:
			message = gmpy.divm(1, message, self.n_revealed)
		
		base = gmpy.mpz(message)
		
		if self.runtime.id == 1:
			power = gmpy.mpz(-self.d)
		else:
			power = gmpy.mpz(self.d)
			
		modulus = gmpy.mpz(self.n_revealed)
		c_i = int(pow(base, power, modulus))
		
		c1, c2, c3 = self.runtime.shamir_share([1, 2, 3], self.Zp, c_i)
		c_tot = c1 * c2 * c3
		open_c_tot = self.runtime.open(c_tot)
		
		results = gather_shares([open_c_tot])
		results.addCallback(self.check_signature)
		
	
	def check_signature(self, results):
		self.signature = results[0].value % self.n_revealed
		print "\nSignature for message M is C = " + str(self.signature)	
		
		file_name = "/viff/apps/key" + sys.argv[2] + "/buffer.txt"
		f = open(file_name, "w+")
		f.write(str(self.signature) + "\n")
		f.close()

		self.runtime.shutdown()
		
	def __init__(self, runtime):
		
		# CHANGEABLE VARIABLES
		#*******************
		
		self.rounds = 1
		self.decrypt_benchmark_active = True
		self.decrypt_rounds = 1
		self.bits_N = 32
		self.m = 2
		self.cyphertext = 0
		self.bound1 = 12
		self.bound2_p1 = 15000
		self.bound2_p2 = 17500
		self.bound2_p3 = 20000
		
		# VARIABLES NOT TO BE CHANGED
		#*******************				
		
		self.time1 = time.clock()
		self.time2 = 0
		self.completed_rounds = 0
		self.times = []
		self.correct_decryptions = 0
		self.decrypt_time1 = 0
		self.decrypt_time2 = 0
		self.decrypt_times = []
		self.decrypt_tries = 0
		self.runtime = runtime
		self.bit_length = int(self.bits_N / 2) - 2
		self.numeric_length = int((2**self.bit_length) / 4)
		self.prime_list_b1 = self.get_primes(2, self.bound1)		
		
		
		
		print "bit_length = " + str(self.bit_length)
		print "numeric_length = " + str(self.numeric_length) 
		
		if self.runtime.id == 1:
			self.prime_list_b2 = self.get_primes(self.bound1, self.bound2_p1)
		elif self.runtime.id == 2:
			self.prime_list_b2 = self.get_primes(self.bound2_p1, self.bound2_p2)
		else:
			self.prime_list_b2 = self.get_primes(self.bound2_p2, self.bound2_p3)
		
		print "length of list b2 = " + str(len(self.prime_list_b2))
		
		self.prime_pointer = 0
		
		self.function_count = [0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0]
		self.function_count_names = ["generate_p", "generate_q", 
		"trial_division_p", "check_trial_division_p",
		"trial_division_q", "check_trial_division_q", 
		"check_n", "primality_test_N", "check_primality_test_N", 
		"generate_g", "check_g", "check_v", "generate_z", 
		"check_z", "generate_l", "generate_d", "check_decrypt"]
		
		l = int(self.bits_N * 3.5)
		k = runtime.options.security_parameter
		
		self.Zp = GF(find_prime(2**(l + 1) + 2**(l + k + 1), blum = True))
		print "Zp:"
		print self.Zp.modulus
		
		self.import_params()
		

parser = OptionParser()
Runtime.add_options(parser)
options, args = parser.parse_args()

if len(args) == 0:
	parser.error("you must specify a config file")
else:
	id, players = load_config(args[0])
	
runtime_class = make_runtime_class(mixins = [ComparisonToft07Mixin])
pre_runtime = create_runtime(id, players, 1, options, runtime_class)
pre_runtime.addCallback(Protocol)

reactor.run()	

