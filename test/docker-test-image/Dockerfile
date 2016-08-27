FROM ubuntu:latest
MAINTAINER Josef Friedrich <josef@friedrich.rocks>

RUN export DEBIAN_FRONTEND='noninteractive' && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
	build-essential \
	libxml2-dev \
	libxslt1-dev \
	musescore \
	python-doc \
	python-dev \
	python-pip \
	python-setuptools \
	python-wheel \
	zlib1g-dev \
	&& \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*

WORKDIR /test

