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
    python3-pip \
    python3-sawtooth-sdk

RUN pip3 install --upgrade pip

RUN pip3 install \
    psycopg2-binary

WORKDIR /project/sawtooth-water-grant

ENV PATH $PATH:/project/sawtooth-water-grant/bin
