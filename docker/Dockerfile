FROM jaaql/jaaql-middleware-python:4.33.9

ENV INSTALL_PATH /JAAQL-sentinel-middleware
ENV SENTINEL_URL _
COPY . $INSTALL_PATH

VOLUME $INSTALL_PATH/vault

RUN mv $INSTALL_PATH/docker/entrypoint_sentinel.sh entrypoint_sentinel.sh
RUN mkdir -p $INSTALL_PATH/log

RUN dos2unix entrypoint_sentinel.sh

ENTRYPOINT ["/bin/bash", "entrypoint_sentinel.sh"]
