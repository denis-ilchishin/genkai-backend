FROM python:3.8-alpine

# Build args and env vars
ARG USER=container
ARG USER_ID=1000
ARG HOME_DIR=/home/${USER}
ARG APP_DIR=${HOME_DIR}/app
ARG SOURCE_DIR=${APP_DIR}/src
ARG ENTRYPOINTS_DIR=${HOME_DIR}/entrypoints

ENV PYTHONUNBUFFERED=1
ENV ENTRYPOINTS_DIR=${ENTRYPOINTS_DIR}
ENV SOURCE_DIR=${SOURCE_DIR}

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

RUN mkdir $HOME_DIR && \
    useradd -u $USER_ID -d $HOME_DIR $USER && \
    mkdir -p ${APP_DIR} && \ 
    mkdir -p ${SOURCE_DIR} && \ 
    mkdir -p ${ENTRYPOINTS_DIR} && \
    chown -R ${USER}:${USER} ${HOME_DIR} && \
    chown -R ${USER}:${USER} ${ENTRYPOINTS_DIR} && \
    chown -R ${USER}:${USER} ${APP_DIR} && \
    chown -R ${USER}:${USER} ${SOURCE_DIR}

# Copy and install pip reqs
ADD ./compose/backend/prod/requirements.txt .
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

# Copy entrypoints
COPY --chown=${USER}:${USER} ./compose/backend/entrypoints ${ENTRYPOINTS_DIR}

# Activate new user
USER $USER

# Set docker workdir
WORKDIR ${SOURCE_DIR}

# Copy our application's source code
COPY --chown=${USER}:${USER} ./src .