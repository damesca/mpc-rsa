FROM ubuntu:18.04

# Install required packages for the app to work
RUN \
	apt-get update && \
	apt-get install -y python-twisted-core && \
	apt-get install -y python-gmpy && \
	apt-get install -y mercurial && \
	apt-get install -y python-pip && \
	apt-get install -y git && \
	apt-get install -y nano && \
	apt-get install -y systemd && \
	apt-get install -y python-flask && \
	pip install pyOpenSSL && \
	pip install requests && \
	pip install asn1 && \
	pip install future && \
	pip install pycryptodome

# Download viff and fix runtime file error before installation
RUN \
	hg clone http://hg.viff.dk/viff/ && \
	rm /viff/viff/runtime.py

COPY runtime.py /viff/viff/

RUN \
	cd /viff && \
	python setup.py build && \
	python setup.py install

# Add the application scripts
COPY mpc_node.py /viff/apps/
COPY rsa_create_key.py /viff/apps/
COPY rsa_sign.py /viff/apps/
COPY pub_key_encoder.py /viff/apps/

# Execute the app
CMD /usr/bin/python /viff/apps/mpc_node.py