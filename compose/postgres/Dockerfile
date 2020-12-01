FROM postgres:12.4-alpine

ARG DUMPS_DIR
ENV DUMPS_DIR=${DUMPS_DIR}

ADD ./compose/postgres/postgresql.conf /etc/postgresql/postgresql.conf

WORKDIR ${DUMPS_DIR}

ADD ./compose/postgres/dump.sh /root/dump.sh