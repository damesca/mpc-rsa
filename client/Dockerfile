FROM ubuntu:18.04

# Install required packages for the app to work
RUN \
	apt-get update && \
	apt-get install -y python-pip && \
	apt-get install -y git && \
	apt-get install -y nano && \
	apt-get install -y systemd && \
	pip install pyOpenSSL && \
	pip install requests && \
	pip install asn1 && \
	pip install pycryptodome

RUN \
	git clone https://github.com/dmoralesescalera/certbuilder.git && \
	pip install certbuilder

COPY client_newKey.py /certbuilder
COPY client_buildCert.py /certbuilder
COPY orqIp.txt /certbuilder