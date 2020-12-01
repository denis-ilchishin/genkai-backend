FROM python:3.8-alpine

RUN apk update --no-cache && \ 
    apk add --no-cache \ 
    shadow \
    bash \
    git \
    gcc \
    g++ \
    make \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    libwebp-dev

# Build args and env vars
ARG USER=container
ARG USER_ID=1000
ARG HOME_DIR=/home/${USER}
ARG APP_DIR=${HOME_DIR}/app
ARG SOURCE_DIR=${APP_DIR}/src
ARG VSCODE_DIR=${HOME_DIR}/.vscode-server
ARG ENTRYPOINTS_DIR=${HOME_DIR}/entrypoints

ENV PYTHONUNBUFFERED=1
ENV ENTRYPOINTS_DIR=${ENTRYPOINTS_DIR}
ENV SOURCE_DIR=${SOURCE_DIR}

RUN mkdir $HOME_DIR && \
    useradd -u $USER_ID -d $HOME_DIR $USER && \
    mkdir -p ${APP_DIR} && \ 
    mkdir -p ${SOURCE_DIR} && \ 
    mkdir -p ${VSCODE_DIR} && \
    mkdir -p ${ENTRYPOINTS_DIR} && \
    chown -R ${USER}:${USER} ${HOME_DIR}


WORKDIR ${APP_DIR}

ADD ./compose/backend/local/requirements.txt .

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && pip install -U pip && pip install -r requirements.txt

COPY --chown=${USER}:${USER} ./compose/backend/entrypoints ${ENTRYPOINTS_DIR}

RUN chmod +x -R ${ENTRYPOINTS_DIR}

USER $USER