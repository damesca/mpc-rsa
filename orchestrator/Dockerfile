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

# Add the application scripts
COPY orchestrator.py /

# Execute the app
CMD /usr/bin/python /orchestrator.py