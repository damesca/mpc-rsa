FROM ubuntu:18.04

# Install required packages for the app to work
RUN \
	apt-get update && \
	apt-get install -y python-pip && \
	pip install requests

COPY test.py /
COPY ips.txt /

# Execute the app
CMD /usr/bin/python /test.py