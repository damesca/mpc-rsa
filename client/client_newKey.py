from certbuilder import generate_pair_mpc

f = open("orqIp.txt", "r")
orq_ip = f.read()
f.close()

keyPairInfo = generate_pair_mpc("http://" + orq_ip + ":5000/generateKeys")
print keyPairInfo