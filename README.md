# Introduction
This is a MultyParty Computation System Prototipe wich provides distributed RSA key management (key pair creation and signing operations, but can be extended to decryption too). 
It is based on Atle Mauland work, which integrate the distributed RSA protocol into VIFF code (VIFF is a Python framework for MPC).

-[Distributed RSA protocol](https://www.researchgate.net/publication/266524261_Realizing_Distributed_RSA_using_Secure_Multiparty_Computations)

-[VIFF - Virtual Ideal Functionality Framework](http://viff.dk/)

The objective of this contribution is to provide a test environment, wich can be easyly deployed, emulating a cloud server architecture wich provides a service for clients. In this way, a client entity (one user or domain), can take advantage of the key management service offered via an orchestrator element. The key management service provides a virtual Hardware Security Module, thanks to MPC properties.

## Architecture

<img src="https://github.com/dmoralesescalera/RSA-MPC-server/blob/master/pics/architecture.jpg" width="600" height="500">

The system architecure is built over three tiers. On top, there are the servers, with a flat design, meaning they do not develop the logic that make the system works. This is the orchestrator function, on second tier, which translate client requests and coordinates the servers.
The servers use the information provided by orchestrator to start a MPC operation. Clients are thaught in abstract way, meaning they can perform any desired operation.

A client example has been developed, for certificate signing operations with the certbuilder Python library:

-[Certbuilder client with MPC](https://github.com/dmoralesescalera/certbuilder)

## Working Instructions

1. Create network: <br/>
  `docker network create --subnet 10.10.10.0/24 rsa-net`
 
2. (Optional - for changes in code) Re-build images: <br/>
  `docker build -t node ./node` <br/>
  `docker build -t orchestrator ./orchestrator`
  
3. Run compose file (scale can change between 3 and 9): <br/>
  `docker-compose up --scale node=5`
  
4. Configure nodes: <br/>
  `python config_nodes.py`
  
  ![](https://github.com/dmoralesescalera/RSA-MPC-server/blob/master/pics/config_nodes.gif)
  
5. Build and run client: <br/>
  `docker build -t client ./client` <br/>
  `docker run -it --network rsa-net client`
  
6. Client actions: <br/>
  `python /certbuilder/client_newKey.py` <br/>
  `python /certbuilder/client_buildCert.py keyId`
  
  ![](https://github.com/dmoralesescalera/RSA-MPC-server/blob/master/pics/build_cert.gif)
