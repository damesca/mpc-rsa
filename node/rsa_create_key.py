#!/usr/bin/python

import random
import math
import gmpy
import time

import asn1
import binascii
from binascii import hexlify, unhexlify
import subprocess
from subprocess import Popen
import sys

from optparse import OptionParser
from twisted.internet import reactor

from viff.field import GF
from viff.runtime import Runtime, create_runtime, gather_shares, make_runtime_class, Share
from viff.comparison import ComparisonToft07Mixin, Toft05Runtime
from viff.config import load_config
from viff.util import rand, find_prime
from viff.equality import ProbabilisticEqualityMixin

class Protocol:

	def export_params(self):
		print "## EXPORTANDO PARAMETROS ##"
		# Guardar parametros de las claves en ficheros
			
		if self.runtime.id == 1:
			file_name = sys.argv[2] + "/values-1.txt"
			f = open(file_name, "w+")
			f.write(str(self.n_revealed) + "\n")
			f.write(str(self.d) + "\n")
			f.close()

		elif self.runtime.id == 2:
			file_name = sys.argv[2] + "/values-2.txt"
			f = open(file_name, "w+")
			f.write(str(self.n_revealed) + "\n")
			f.write(str(self.d) + "\n")
			f.close()

		elif self.runtime.id == 3:
			file_name = sys.argv[2] + "/values-3.txt"
			f = open(file_name, "w+")
			f.write(str(self.n_revealed) + "\n")
			f.write(str(self.d) + "\n")
			f.close()

		#
		print "## FIN EXPORTAR PARAMETROS ##"
		self.export_public()

	
	def export_public(self):
		print "## EXPORTANDO CLAVE PUBLICA ##"

		args = "python /viff/apps/pub_key_encoder.py " + str(self.n_revealed) + " " + str(self.e) + " " + sys.argv[2]
		p = subprocess.call(args, shell=True)
			
		self.runtime.shutdown()
	'''
        def export_public(self):
		if self.runtime.id == 1:
			args = "python file-writer.py pub_key.txt" + " " + str(self.n_revealed) + " " + str(self.e)
			p = Popen(args, shell=True)
			p.wait()
		self.runtime.shutdown()
	'''

	def get_primes(self, min, max):
		primes = []
		while True:
			prime = int(gmpy.next_prime(min))
			if prime <= max:
				primes += [prime]
				min = prime
			else:
				return primes
				
	def generate_p(self):
		self.function_count[0] += 1
		if self.runtime.id == 1:
			self.p = 4*random.randint(1, self.numeric_length-1) + 3
		else:
			self.p = 4*random.randint(1, self.numeric_length-1)
		# print "my p = " + str(self.p)	
		self.trial_division_p()
		
	def generate_q(self):
		self.function_count[1] += 1
		if self.runtime.id == 1:
			self.q = 4*random.randint(1, self.numeric_length-1) + 3
		else:
			self.q = 4*random.randint(1, self.numeric_length-1)
		# print "my q = " + str(self.q)	
		self.trial_division_q()	
		
	def trial_division_p(self):
		self.function_count[2] += 1
		prime_num = self.prime_list_b1[self.prime_pointer]
		p_trial = self.p % prime_num
		#print "my p_trial = " + str(p_trial) + "for prime_num = " + str(prime_num)
		r_trial = random.randint(1, self.Zp.modulus - 1)
		#print "my random r_trial = " + str(r_trial)
		
		p_trial1, p_trial2, p_trial3 = self.runtime.shamir_share([1, 2, 3], self.Zp, p_trial)
		p_r_trial1, p_r_trial2, p_r_trial3 = self.runtime.shamir_share([1, 2, 3], self.Zp, r_trial)
	
		p_trial_tot = (p_trial1 + p_trial2 + p_trial3)
		r_trial_tot = (p_r_trial1 + p_r_trial2 + p_r_trial3)
	
		trial_reveal = p_trial_tot * (p_trial_tot - prime_num) * (p_trial_tot - 2 * prime_num) * r_trial_tot
	
		open_trial_reveal = self.runtime.open(trial_reveal)
		results = gather_shares([open_trial_reveal])
	
		results.addCallback(self.check_trial_division_p)
	
	def check_trial_division_p(self, results):
		self.function_count[3] += 1
		rev_trial = results[0].value
		#print "rev_trial = " + str(rev_trial)
		
		if rev_trial == 0:
			self.prime_pointer = 0
			print "generating p again"
			self.generate_p()
		else:
			self.prime_pointer += 1
			
			if self.prime_pointer >= len(self.prime_list_b1):
				self.prime_pointer = 0
				self.generate_q()
			else:
				self.trial_division_p()
				
	def trial_division_q(self):
		self.function_count[4] += 1
		prime_num = self.prime_list_b1[self.prime_pointer]
		q_trial = self.q
		#print "my q_trial = " + str(q_trial) + " for prime_num = " + str(prime_num)
		r_trial = random.randint(1, self.Zp.modulus - 1)
		#print "my random r_trial = " + str(r_trial)
		
		q_trial1, q_trial2, q_trial3 = self.runtime.shamir_share([1, 2, 3], self.Zp, q_trial)
		q_r_trial1, q_r_trial2, q_r_trial3 = self.runtime.shamir_share([1, 2, 3], self.Zp, r_trial)
		
		q_trial_tot = (q_trial1 + q_trial2 + q_trial3)
		r_trial_tot = (q_r_trial1 + q_r_trial2 + q_r_trial3)
		trial_reveal = q_trial_tot * (q_trial_tot - prime_num) * (q_trial_tot - 2 * prime_num) * r_trial_tot
		
		open_trial_reveal = self.runtime.open(trial_reveal)
		results = gather_shares([open_trial_reveal])
		
		results.addCallback(self.check_trial_division_q)
		
	def check_trial_division_q(self, results):	
		self.function_count[5] += 1
		rev_trial = results[0].value
		#print "rev_trial = " + str(rev_trial)
		
		if rev_trial == 0:
			self.prime_pointer = 0
			print "generating q again"
			self.generate_q()
		else:
			self.prime_pointer += 1
			
			if self.prime_pointer >= len(self.prime_list_b1):
				self.prime_pointer = 0
				
				p1, p2, p3 = self.runtime.shamir_share([1, 2, 3], self.Zp, self.p)
				self.ptot = (p1 + p2 + p3)
				
				q1, q2, q3 = self.runtime.shamir_share([1, 2, 3], self.Zp, self.q)
				self.qtot = (q1 + q2 + q3)
								
				n = self.ptot * self.qtot
				open_n = self.runtime.open(n)
				
				# DEBUGGING #
				open_ptot = self.runtime.open(self.ptot)
				open_qtot = self.runtime.open(self.qtot)
				#******#
				
				results = gather_shares([open_n, open_ptot, open_qtot])
				results.addCallback(self.check_n)
				
			else:
				self.trial_division_q()
				
	def check_n(self, results):
		self.function_count[6] += 1
		print "n = " + str(results[0])
		
		self.n_revealed = results[0].value
		self.phi = (self.ptot - 1) * (self.qtot - 1)
		print "completed rounds: " + str(self.completed_rounds) + " / " + str(self.rounds)
		print "\nn_revealed = " + str(self.n_revealed)
		
		print "p_revealed = " + str(results[1].value)
		print "q_revealed = " + str(results[2].value)
		
		print "#bits in N = " + str(math.ceil(math.log(self.n_revealed, 2)))
		
		self.primality_test_N()
		
	def primality_test_N(self):
		self.function_count[7] += 1
		test_failed = 0
		for i in self.prime_list_b2:
			#print "N mod " + str(i) + " = "  str(self.n_revealed % i)
			
			if self.n_revealed % i == 0:
				#print "failed..." + str(i) + " divides " + str(self.n_revealed)
				test_failed = 1
				break
		
		failed1, failed2, failed3 = self.runtime.shamir_share([1, 2, 3], self.Zp, test_failed)
		
		failed_tot = failed1 + failed2 + failed3
		open_failed_tot = self.runtime.open(failed_tot)
		
		results = gather_shares([open_failed_tot])
		results.addCallback(self.check_primality_test_N)
		
	def check_primality_test_N(self, results):
		self.function_count[8] += 1
		
		if results[0].value == 0:
			#print "primality test for N is OK, generate g"
			self.generate_g()
			
		else:
			#print "primality test for N failed, start generating p"
			self.generate_p()
			
	def generate_g(self):
		self.function_count[9] += 1
		
		if self.runtime.id == 1:
			self.g = random.randint(1, self.n_revealed - 1)
			#print "g = " + str(self.g)
			self.g = self.runtime.shamir_share([1], self.Zp, self.g)
		
		else:
			self.g = self.runtime.shamir_share([1], self.Zp)
			
		self.open_g = self.runtime.open(self.g)
		results = gather_shares([self.open_g])
		results.addCallback(self.check_g)
		
	def check_g(self, results):
		self.function_count[10] += 1
		#print "g = " + str(results[0].value)
		self.g = results[0].value
		jacobi = gmpy.jacobi(self.g, self.n_revealed) % self.n_revealed
		#print "jacobi = " + str(jacobi)
		
		if jacobi == 1:
			if self.runtime.id == 1:
				self.phi_i = self.n_revealed - self.p - self.q + 1
				print "((N)): " + str(self.n_revealed)
				print "((p)): " + str(self.p)
				print "((q)): " + str(self.q)
				print "<<phi_i>>: " + str(self.phi_i)
				base = gmpy.mpz(self.g)
				power = gmpy.mpz(self.phi_i / 4)
				print "<<power>>: " + str(power)
				modulus = gmpy.mpz(self.n_revealed)
				self.v = int(pow(base, power, modulus))
				#self.v = self.powermod(self.g, (self.n_revealed - self.p - self.q + 1) / 4, self.n_revealed)
				
			else:
				self.phi_i = -(self.p + self.q)
				self.inverse_v = int(gmpy.divm(1, self.g, self.n_revealed))
				
				base = gmpy.mpz(self.inverse_v)
				power = gmpy.mpz(-self.phi_i / 4)
				modulus = gmpy.mpz(self.n_revealed)
				self.v = int(pow(base, power, modulus))
			
			#print "self.phi_i = " + str(self.phi_i)
		
		else:
			self.generate_g()
			return
			
		#print "self.v = " + str(self.v)
		
		v1, v2, v3 = self.runtime.shamir_share([1, 2, 3], self.Zp, self.v)
		
		v_tot = v1 * v2 * v3
		self.open_v = self.runtime.open(v_tot)
		results = gather_shares([self.open_v])
		results.addCallback(self.check_v)
		
	def check_v(self, results):
		self.function_count[11] += 1
		v = results[0].value % self.n_revealed
		#print "v = " + str(v)
		
		if v == 1 or v == self.n_revealed - 1:
			self.generate_z()
		else:
			self.prime_pointer = 0
			self.generate_p()
			
	def generate_z(self):
		self.function_count[12] += 1
		self.r_z = random.randint(1, self.n_revealed - 1)
		r1, r2, r3 = self.runtime.shamir_share([1, 2, 3], self.Zp, self.r_z)
		z = (r1 + r2 + r3) * (-1 + (self.ptot + self.qtot))
		
		self.open_z = self.runtime.open(z)
		results = gather_shares([self.open_z])
		results.addCallback(self.check_z)
		
	def check_z(self, results):
		self.function_count[13] += 1
		z = results[0].value % self.n_revealed
		#print "z = " + str(z)
		
		z_n = gmpy.gcd(z, self.n_revealed)
		
		if z_n == 1:
			#print "gcd(z, N) = 1, start generating e,d"
			self.e = 2**16 + 1
			#print "e = " + str(self.e)
			self.generate_l()
		else:
			#print "gcd(z, N) != 1, restart with generating p"
			self.prime_pointer = 0
			self.generate_p()
			
																
	def generate_l(self):
		self.function_count[14] += 1
		self.l = self.phi_i % self.e
		print "\n\nPRIVATE VARIABLES"
		print "self.l = " + str(self.l)
		l1, l2, l3 = self.runtime.shamir_share([1, 2, 3], self.Zp, self.l)
		l_tot = l1 + l2 + l3
		
		open_l_tot = self.runtime.open(l_tot)
		results = gather_shares([open_l_tot])
		results.addCallback(self.generate_d)
		
	def generate_d(self, results):
		self.function_count[15] += 1
		l_tot = results[0].value % self.e
		#print "l_tot = " + str(l_tot)
		
		try:
			zeta = gmpy.divm(1, l_tot, self.e)
		except:
			print "not invertable mod e"
			self.generate_p()
			
		#print "zeta (inv) = " + str(zeta)
		
		self.d = int(-(zeta*self.phi_i)/self.e)
		print "self.p = " + str(self.p)
		print "self.q = " + str(self.q)
		print "self.d = " + str(self.d)
		print "self.e = " + str(self.e)
		print "N (public) = " + str(self.n_revealed)
		print "Total bits in N = " + str(math.log(self.n_revealed, 2))
		
		base = gmpy.mpz(self.m)
		power = gmpy.mpz(self.e)
		modulus = gmpy.mpz(self.n_revealed)
		self.c = int(pow(base, power, modulus))
		print ">> self.cypher = " + str(self.c)
		
		if self.runtime.id == 1:
			self.c = gmpy.divm(1, self.c, self.n_revealed)
		
		base = gmpy.mpz(self.c)
		
		if self.runtime.id == 1:
			power = gmpy.mpz(-self.d)
		else:
			power = gmpy.mpz(self.d)
			
		modulus = gmpy.mpz(self.n_revealed)
		
		self.decrypt = int(pow(base, power, modulus))
		print "self.decrypt (c^di mod N) = " + str(self.decrypt)
		
		c1, c2, c3 = self.runtime.shamir_share([1, 2, 3], self.Zp, self.decrypt)
		
		open_c1 = self.runtime.open(c1)
		open_c2 = self.runtime.open(c2)
		open_c3 = self.runtime.open(c3)
		
		results = gather_shares([open_c1, open_c2, open_c3])
		results.addCallback(self.check_decrypt)
		
		
	def check_decrypt(self, results):
		self.function_count[16] += 1
		
		if self.runtime.id == 3:
			c1 = results[0].value
			c2 = results[1].value
			c3 = results[2].value
			
			for i in range(0, 3):
				tmp_decrypt = c1 * c2 * c3 % self.n_revealed
				print "Decryption = " + str(tmp_decrypt)
				
				if(tmp_decrypt == self.m):
					print "d found, with +r = " + str(i)
					self.correct_decryptions += 1
					print "Correct decryptions: " + str(self.correct_decryptions) + " / " + str(self.rounds)
					break
				else:
					self.d += 1
					base = gmpy.mpz(self.c)
					power = gmpy.mpz(self.d)
					modulus = gmpy.mpz(self.n_revealed)
					c3 = int(pow(base, power, modulus))
					
		self.time2 = time.clock()
		self.completed_rounds += 1
		print "Completed rounds: " + str(self.completed_rounds) + " / " + str(self.rounds)
		self.times += [self.time2 - self.time1]
		
		if self.completed_rounds == self.rounds:
			print "\n\nBENCHMARKS FOR VALID KEY GENERATION"
			print "times = " + str(self.times)
			print "Average: " + str(sum(self.times) / (self.rounds))
			print "Correct decryptions: " + str(self.correct_decryptions) + " / " + str(self.rounds)
			print "\n"
			
			for i in range(len(self.function_count)):
				print str(self.function_count_names[i]) + ": " + str(self.function_count[i]) + ", avg: " + str(int(self.function_count[i] / self.rounds))
			
			if self.decrypt_benchmark_active == True:
				self.decrypt_benchmark()
				return
			else:
				self.runtime.shutdown()
				
		
		else:
			self.prime_pointer = 0
			self.decrypt_tries = 0
			self.time1 = time.clock()
			self.generate_p()
			
	def decrypt_benchmark(self):
		self.decrypt_time1 = time.clock()
		
		base = gmpy.mpz(self.m)
		power = gmpy.mpz(self.e)
		modulus = gmpy.mpz(self.n_revealed)
		self.c = int(pow(base, power, modulus))
		
		if self.runtime.id == 1:
			self.c = gmpy.divm(1, self.c, self.n_revealed)
		
		base = gmpy.mpz(self.c)
		
		if self.runtime.id == 1:
			power = gmpy.mpz(-self.d)
		else:
			power = gmpy.mpz(self.d)
			
		modulus = gmpy.mpz(self.n_revealed)
		self.decrypt = int(pow(base, power, modulus))
		
		c1, c2, c3 = self.runtime.shamir_share([1, 2, 3], self.Zp, self.decrypt)
		
		c_tot = c1 * c2 * c3
		open_c_tot = self.runtime.open(c_tot)
		
		results = gather_shares([open_c_tot])
		results.addCallback(self.check_decrypt_benchmark)
		
	def check_decrypt_benchmark(self, results):
		for i in range(0, 3):
			tmp_decrypt = results[0].value % self.n_revealed
			
			if tmp_decrypt == self.m:
				self.decrypt_time2 = time.clock()
				self.decrypt_tries += 1
				self.decrypt_times += [self.decrypt_time2 - self.decrypt_time1]
				print "correct decryption for m = " + str(self.m)
				
				if self.decrypt_tries < self.decrypt_rounds:
					self.m += 1
					self.decrypt_benchmark()
					return
				else:
					print "\n\nBENCHMARK FOR DECRYPTION"
					print "times = " + str(self.decrypt_times)
					print "average decrypt time = " + str(sum(self.decrypt_times) / self.decrypt_rounds)

					self.export_params()
					return

		
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
		
		self.generate_p()
		

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
					
