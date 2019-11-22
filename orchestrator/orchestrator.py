from flask import Flask, jsonify, abort, make_response, request, url_for, redirect
from threading import Lock, Thread
import requests
import json
import random


#########################
### INITIAL VARIABLES ###
#########################

app = Flask(__name__)

orqId = "o001"

networkList_gen = None

keyList = [
	{
		"keyId": 9999,
		"publicKey": "30819e300d06092a864886f70d010101050003818c003081880281803af1017d70a6bb7f93e0cc369648cb4a3b3079877a5f00f8f6d76a1347291afea0c139b085724a35cf8e060b69070cc4470e327199fd72b5015f1845f21cfdd69fa235ac8129dd2c785cff47f36721238866d128ec4b27284e2750609f44e0ee93d7b0891aa2fa7303c2e638dfb9c0b94c5586c4d436a28cb64d84041951d4b10203010001",
		"server1": "s001",
		"server2": "s002",
		"server3": "s003"
	}
]

"""
keyList = [
	{
		"keyId": Integer,
		"publicKey": String,
		"server1": String,
		"server2": String,
		"server3": String
	}
]
"""

responses = []

lock = Lock()

########################
### AUXILIAR METHODS ###
########################

def pretty_print(char, text):
	print ""	
	print char*40
	print text
	print char*40
	print ""

def make_public_resource(resource):
	new_resource = {}
	for field in resource:
		if field == "id":
			new_resource["uri"] = url_for("get_resource", resource_title=resource["title"], _external=True)
		else:
			new_resource[field] = resource[field]
	return new_resource

def select_servers():
	networkList = load_config_files()

	num = 0
	for item in networkList:
		num = num + 1	
	print "num = " + str(num)	

	server1 = networkList[random.randrange(0, num-1, 1)]
	while server1["id"] == "ca":
		server1 = networkList[random.randrange(0, num-1, 1)]

	server2 = networkList[random.randrange(0, num-1, 1)]
	while server2["id"] == "ca" or server2 == server1:
		server2 = networkList[random.randrange(0, num-1, 1)]

	server3 = networkList[random.randrange(0, num-1, 1)]
	while server3["id"] == "ca" or server3 == server1 or server3 == server2:
		server3 = networkList[random.randrange(0, num-1, 1)]

	server1["id"].encode('ascii')
	server2["id"].encode('ascii')
	server3["id"].encode('ascii')

	print "(Server1) : " + str(server1)
	print "(Server2) : " + str(server2)
	print "(Server3) : " + str(server3)

	return [server1, server2, server3]

def gen_key_post(target, payload, headers):
	print "/// Init thread ///"	
	global responses
	r = requests.post(target, data=json.dumps(payload), headers=headers)
	lock.acquire()
	responses.append(dict(json.loads(r.text)))
	pretty_print('$', responses)
	lock.release()
	print "/// Finish thread ///"

def sign_hash_get(target):
	print "/// Init thread ///"
	global responses
	r = requests.get(target)
	lock.acquire()
	responses.append(dict(json.loads(r.text)))
	pretty_print('$', responses)
	lock.release()
	print "/// Finish thread ///"

def verify_keyId(keyId):
	for item in keyList:
		if item["keyId"] == keyId:
			return item
	return None

def get_ListItem(item, itemList):
	for this in itemList:
		if this == item:
			return this
	return None

def load_config_files():
	with open("/networkList.json", "r") as json_file:
		data = json_file.read()
	data2 = json.loads(data)
	networkList = data2["networkList"]
	json_file.close()
	
	return networkList	

#############################
### HTTP REQUEST METHODS  ###
#############################

@app.route('/configNetwork', methods=['POST'])
def handler_configNetwork():
	if not request.json:
		abort(400)	

	networkList = json.dumps(request.json)
	with open("/networkList.json", "w+") as json_file:
		json_file.write(networkList)
	json_file.close()
	global networkList_gen
	networkList_gen = True

	print networkList

	return json.dumps({ "status" : "ok-orch" })

@app.route('/generateKeys', methods=['GET'])
def handler_generateKeys():	
	pretty_print('*', "[Orquestrator] generateKeys")
	
	# Generate random keyId and verify it does not exist
	keyId = random.randrange(0, 9999, 1)
	existingKey = verify_keyId(keyId)
	while(existingKey != None):
		keyId = random.randrange(0, 9999, 1)
		existingKey = verify_keyId(keyId)
		
	# Select servers randomly
	selectedServers = select_servers()

	# Select available common port on the 3 servers (Must check if there is no coincidence)
	port_responses = []
	for serv in selectedServers:
		#port_req = "http://" + str(serv["ip"]) + ":" + str(serv["port"]) + "/getPorts"
		port_req = "http://" + str(serv["ip"]) + ":5000/getPorts"
		port_responses.append(requests.get(port_req))
	
	selected_port = 0
	index = 0
	while(selected_port == 0 
		and 
	index < len(json.loads(port_responses[0].text)["availablePorts"])):
		selected_port = json.loads(port_responses[0].text)["availablePorts"][index]
		portServ2 = get_ListItem(selected_port, json.loads(port_responses[1].text)["availablePorts"])
		portServ3 = get_ListItem(selected_port, json.loads(port_responses[2].text)["availablePorts"])
		if(portServ2 == None or portServ3 == None):
			selected_port = 0
			++index
	pretty_print('#', "Selected Port: " + str(selected_port))
		
	# Build the requests for the 3 servers
	req = []

	
	payload = {
		"server1": str(selectedServers[0]["id"].encode('ascii')), 
		"server2": str(selectedServers[1]["id"].encode('ascii')), 
		"server3": str(selectedServers[2]["id"].encode('ascii')), 
		"port": selected_port
	}
	"""
	payload = {
		"server1":"s003",
		"server2":"s004",
		"server3":"s005",
		"port":9000
	}
	"""
	pretty_print('%', payload)
	print payload
	headers = {"content-type": "application/json"}


	for serv in selectedServers:
		#req.append("http://" + str(serv["ip"]) + ":" + str(serv["port"]) + "/generateKeys/" + orqId + "/" + str(keyId))
		req.append("http://" + str(serv["ip"]) + ":5000/generateKeys/" + orqId + "/" + str(keyId))

	# Threading management for the requests
	threads = []
	for target in req:
		t = Thread(target=gen_key_post, args=(target, payload, headers))
		threads.append(t)
		t.start()
	for t in threads:		
		t.join()

	# Check if responses bodies are ok for the differente servers
	okResponses = True
	for resp in responses:
		if resp["status"] != "generatingKeys":
			okResponses = False

	# If responses are ok, save formatted data and send response to client
	if okResponses:
		
		keyItem = {
			"keyId": keyId,
			"server1": selectedServers[0]["id"],
			"server2": selectedServers[1]["id"],
			"server3": selectedServers[2]["id"],
			"port": selected_port
		}
		keyList.append(keyItem)
		
		for i in range(0,3):
			responses.pop()
		print "responses: " + str(responses)

		return json.dumps({"status": "generatingKeys", "keyId": keyId})
	else:
		return json.dumps({"status": "error"})	

@app.route('/getKey/<int:keyId>', methods=['GET'])
def handler_getKey(keyId):
	
	pretty_print('*', "[Orquestrator] getKey")

	networkList = load_config_files()

	key = verify_keyId(keyId)
	if key != None:
		
		# Ask the 3 servers to get the generated Key

		for server in networkList:
			if server["id"] == key["server1"]:
				target = "http://" + server["ip"] + ":" + str(server["port"]) + "/getKey/" + orqId + "/" + str(keyId)
				r = requests.get(target)
				serverResponse1 = dict(json.loads(r.text))
			elif server["id"] == key["server2"]:
				target = "http://" + server["ip"] + ":" + str(server["port"]) + "/getKey/" + orqId + "/" + str(keyId)
				r = requests.get(target)
				serverResponse2 = dict(json.loads(r.text))
			elif server["id"] == key["server3"]:
				target = "http://" + server["ip"] + ":" + str(server["port"]) + "/getKey/" + orqId + "/" + str(keyId)
				r = requests.get(target)
				serverResponse3 = dict(json.loads(r.text))
	
		if serverResponse1["status"] == "generated" and serverResponse2["status"] == "generated" and serverResponse3["status"] == "generated":
			if serverResponse1["pubKey"] == serverResponse2["pubKey"] and serverResponse1["pubKey"] == serverResponse3["pubKey"]:
				return json.dumps({"status": "generated", "pubKey": serverResponse1["pubKey"]})
			else:
				return json.dumps({"status": "errorBadPublicKey"})	
			
		else:
			return json.dumps({"status": "generatingKeys"})
	else:
		return json.dumps({"status": "errorKeyId"})
	
	

@app.route('/signMessage/<int:keyId>', methods=['GET'])
def handler_signMessage(keyId):
	pretty_print('*', "[Orquestrator] signMessage")

	networkList = load_config_files()

	# Get message query	
	hashValue = request.args['message']
	
	# Verify if key exists in keyList
	keyItem = verify_keyId(keyId)
	if keyItem != None:

		# Select available common port on the 3 servers (Must check if there is no coincidence)
		selectedServersIds = [keyItem["server1"], keyItem["server2"], keyItem["server3"]]
		selectedServers = []
		for serv in networkList:
			for this in selectedServersIds:
				if this == serv["id"]:
					selectedServers.append(serv)			
		
		port_responses = []
		for serv in selectedServers:
			port_req = "http://" + str(serv["ip"]) + ":" + str(serv["port"]) + "/getPorts"
			port_responses.append(requests.get(port_req))
		
		selected_port = 0
		index = 0
		while(selected_port == 0 
			and 
		index < len(json.loads(port_responses[0].text)["availablePorts"])):
			selected_port = json.loads(port_responses[0].text)["availablePorts"][index]
			portServ2 = get_ListItem(selected_port, json.loads(port_responses[1].text)["availablePorts"])
			portServ3 = get_ListItem(selected_port, json.loads(port_responses[2].text)["availablePorts"])
			if(portServ2 == None or portServ3 == None):
				selected_port = 0
				++index

		# Build requests
		req = []	
		selectedServers = [keyItem["server1"], keyItem["server2"], keyItem["server3"]]
		for serv in selectedServers:
			for server in networkList:
				if server["id"] == serv:
					req.append("http://" + str(server["ip"]) + ":" + str(server["port"]) + "/signMessage/" + str(orqId) + "/" + str(keyId) + "?port=" + str(selected_port) + "&message=" + str(hashValue))
					
		
		# Threading management for the requests
		threads = []
		for url in req:
			t = Thread(target=sign_hash_get, args=(url,))
			threads.append(t)
			t.start()
		for t in threads:
			t.join()

		okResponse = False
		if responses[0] == responses[1] and responses[0] == responses[2]:
			okResponse = True
			resp = responses[0]
		
		for i in range(0, 3):
			responses.pop()
		
		if okResponse:
			return json.dumps({"status": "signedCorrectly", "sign": resp["sign"]})
		else:
			return json.dumps({"status": "badResponse"})
	else:
		return json.dumps({"status": "errorKeyId"})

######################
### ERROR HANDLER  ###
######################

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000,debug=True)

