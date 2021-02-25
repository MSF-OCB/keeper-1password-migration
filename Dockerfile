FROM jfloff/alpine-python

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

MAINTAINER GRP-BRU-ICT-SysApp "grp-bru-ict-appsupport@msf.org"

RUN apk add libxml2-dev libxslt-dev && \
    pip install --upgrade pip && pip install wheel && \
    pip install uwsgi Flask==1.1.2 Flask-HTTPAuth==4.2.0 \
    pip install keepercommander==4.61

COPY src/*.py .

COPY static static
COPY templates templates

COPY bin/launch.sh launch.sh

EXPOSE 8080

ENTRYPOINT [ "/bin/bash", "/launch.sh"]
