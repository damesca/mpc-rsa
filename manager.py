import argparse
import requests
import ipaddress
import json
from subprocess import Popen

parser = argparse.ArgumentParser()
parser.add_argument("nodes", help="number of nodes to run (max 10)", type=int)
parser.add_argument("subnet", help="subnet in CIDR format (192.168.0.0/24)")
parser.add_argument("ca", help="internal ca ip, for certificates generation")
args = parser.parse_args()

network_ip = ipaddress.ip_network(unicode(args.subnet))
network_hosts = list(network_ip.hosts())

compose_file = open("docker-compose.yml", "r")
content = list()
for line in compose_file:
	content.append(line)
compose_file.close()

# Configura las ips de CA y TEST, ademas de la red interna
content[16] = "                ipv4_address: " + args.ca + "\n"
content[24] = "                ipv4_address: " + str(ipaddress.ip_address(unicode(args.ca))+1) + "\n"
content[32] = "                - subnet: \"" + args.subnet + "\"\n"

compose_file = open("docker-compose.yml", "w")
for line in content:
	compose_file.write(line)
compose_file.close()

# Pasa al nodo test las ips necesarias para configurar a los nodos
test_file = open("./test/ips.txt", "w")
for i in range(1, args.nodes+1):
	host = str(network_hosts[i]) + "\n"
	test_file.write(host)
ca_info = "ca: " + args.ca + "\n"
test_file.write(ca_info)
test_file.close()		

path = "docker-compose up --scale node=" + str(args.nodes)
Popen(path, shell=True)

#target = "http://10.10.10.2:5000/configNode"
#payload = { "id":"s001", "ip": "10.10.10.2", "port": 5000 }
#headers = { "content-type": "application/json" }
#
#r = requests.post(target, data=json.dumps(payload), headers=headers)
#
#for i in range(1,args.nodes+1):
#	target = "http://192.168.1." + str(i+1) + ":5000/configNode"
#	payload = { "id": "s00" + str(i), "ip": "192.168.1." + str(i), "port": 5000 }
#	headers = { "content-type": "application/json" }
#	print target
#	print payload
#	print headers
#
#	r = requests.post(target, data=json.dumps(payload), headers=headers)