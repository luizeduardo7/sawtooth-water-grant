# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

FROM ubuntu:bionic

RUN \
 apt-get update \
 && apt-get install -y -q curl gnupg \
 && curl -sSL 'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x8aa7af1f1091a5fd' | apt-key add -  \
 && echo 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe' >> /etc/apt/sources.list \
 && apt-get update

RUN apt-get install -y --allow-unauthenticated -q \
    curl \
    python3-pip \
    python3-sawtooth-cli \
    python3-sawtooth-sdk \
    python3-sawtooth-rest-api


# RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
#     && apt-get install -y nodejs

RUN curl -sL https://deb.nodesource.com/setup_12.x -o /tmp/nodesource_setup.sh && bash /tmp/nodesource_setup.sh \
    && apt-get install -y nodejs

RUN pip3 install --upgrade pip

RUN pip3 install \
    aiohttp==3.0.8 \
    aiopg \
    bcrypt \
    grpcio-tools \
    itsdangerous \
    nose2 \
    psycopg2-binary \
    pycrypto \
    pylint \
    pycodestyle

WORKDIR /project/sawtooth-water-grant

COPY sprinkle_app/package.json /project/sawtooth-water-grant/sprinkle_app/

RUN cd sprinkle_app/ && npm install

ENV PATH $PATH:/project/sawtooth-water-grant/bin
