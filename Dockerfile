FROM jfloff/alpine-python

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

MAINTAINER GRP-BRU-ICT-SysApp "grp-bru-ict-appsupport@msf.org"

RUN apk add libxml2-dev libxslt-dev unzip && \
    pip install --upgrade pip && pip install wheel && \
    pip install uwsgi Flask==1.1.2 Flask-HTTPAuth==4.2.0 secure_delete Flask-Limiter \
    pip install keepercommander==4.61

RUN mkdir op && cd op && wget https://cache.agilebits.com/dist/1P/op/pkg/v1.8.0/op_linux_amd64_v1.8.0.zip

RUN unzip -o -d op/ ./op/*.zip

COPY src/ app/

RUN mkdir op/config && chmod 700 op/config

COPY bin/launch.sh launch.sh

EXPOSE 8081

ENTRYPOINT [ "/bin/bash", "/launch.sh"]
