#!/bin/bash
url="http://192.168.0.2:5000/configNode"
curl -d '{"id":"s001","ip":"192.168.0.2","port":5000}' -H "Content-Type: application/json" -X POST $url
read -p "# Pulsa cualquier tecla para continuar... #"

url="http://192.168.0.3:5000/configNode"
curl -d '{"id":"s002","ip":"192.168.0.3","port":5000}' -H "Content-Type: application/json" -X POST $url
read -p "# Pulsa cualquier tecla para continuar... #"

url="http://192.168.0.4:5000/configNode"
curl -d '{"id":"s003","ip":"192.168.0.4","port":5000}' -H "Content-Type: application/json" -X POST $url
read -p "# Pulsa cualquier tecla para continuar... #"

curl -d '{"networkList":[{"id":"serverInfo","num":3},{"id":"s001","ip":"192.168.0.2"},{"id":"s002","ip":"192.168.0.3"},{"id":"s003","ip":"192.168.0.4"},{"id":"ca","ip":"192.168.0.6"}]}' -H "Content-Type: application/json" -X POST http://192.168.0.2:5000/configNetwork
read -p "# Pulsa cualquier tecla para continuar... #"
curl -d '{"networkList":[{"id":"serverInfo","num":3},{"id":"s001","ip":"192.168.0.2"},{"id":"s002","ip":"192.168.0.3"},{"id":"s003","ip":"192.168.0.4"},{"id":"ca","ip":"192.168.0.6"}]}' -H "Content-Type: application/json" -X POST http://192.168.0.3:5000/configNetwork
read -p "# Pulsa cualquier tecla para continuar... #"
curl -d '{"networkList":[{"id":"serverInfo","num":3},{"id":"s001","ip":"192.168.0.2"},{"id":"s002","ip":"192.168.0.3"},{"id":"s003","ip":"192.168.0.4"},{"id":"ca","ip":"192.168.0.6"}]}' -H "Content-Type: application/json" -X POST http://192.168.0.4:5000/configNetwork 
read -p "# Pulsa cualquier tecla para continuar... #"
curl -X GET http://192.168.0.2:5000/getCertificates
read -p "# Pulsa cualquier tecla para continuar... #"
curl -X GET http://192.168.0.3:5000/getCertificates
read -p "# Pulsa cualquier tecla para continuar... #"
curl -X GET http://192.168.0.4:5000/getCertificates 
read -p "# Pulsa cualquier tecla para continuar... #"
curl -d '{"server1":"s001","server2":"s002","server3":"s003","port":9000}' -H "Content-Type: application/json" -X POST http://192.168.0.2:5000/generateKeys/o001/10
read -p "# Pulsa cualquier tecla para continuar... #"
curl -d '{"server1":"s001","server2":"s002","server3":"s003","port":9000}' -H "Content-Type: application/json" -X POST http://192.168.0.3:5000/generateKeys/o001/10
read -p "# Pulsa cualquier tecla para continuar... #"
curl -d '{"server1":"s001","server2":"s002","server3":"s003","port":9000}' -H "Content-Type: application/json" -X POST http://192.168.0.4:5000/generateKeys/o001/10 