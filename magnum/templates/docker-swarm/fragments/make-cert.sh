#!/bin/sh

# Copyright 2014 The Kubernetes Authors All rights reserved.
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

set -o errexit
set -o nounset
set -o pipefail

. /etc/sysconfig/heat-params

cert_ip=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
sans="IP:${cert_ip},IP:${NODE_IP},IP:127.0.0.1"
MASTER_HOSTNAME=${MASTER_HOSTNAME:-}
if [[ -n "${MASTER_HOSTNAME}" ]]; then
  sans="${sans},DNS:${MASTER_HOSTNAME}"
fi

cert_dir=/etc/docker
cert_conf_dir=${cert_dir}/conf
cert_group=root

mkdir -p "$cert_dir"
mkdir -p "$cert_conf_dir"

# TODO(apmelton) - replace with call to Magnum CA API to get CA Cert
echo 01 > "$cert_dir/ca.srl"
echo "Generating CA key and certs"
openssl genrsa -out "${cert_dir}/ca.key" 4096
openssl req -new -x509 -days 1000 \
        -key "${cert_dir}/ca.key" -out "${cert_dir}/ca.crt" \
        -subj "/CN=${cert_ip}@`date +%s`"

echo "Generating Server key and cert"
cat > ${cert_conf_dir}/server.conf <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions     = req_ext
x509_extensions    = req_ext
prompt = no
copy_extensions = copyall
[req_distinguished_name]
CN = swarm.invalid
[req_ext]
subjectAltName = ${sans}
extendedKeyUsage = clientAuth,serverAuth
EOF

openssl genrsa -out "${cert_dir}/server.key" 4096
openssl req -new -days 1000 \
        -key "${cert_dir}/server.key" \
        -out "${cert_dir}/server.csr" \
        -reqexts req_ext \
        -extensions req_ext \
        -config "${cert_conf_dir}/server.conf"
# TODO(apmelton) - replace with call to Magnum CA API to get csr signed
openssl x509 -req -days 1000 \
        -in "${cert_dir}/server.csr" \
        -out "${cert_dir}/server.crt" \
        -CAkey "${cert_dir}/ca.key" \
        -CA "${cert_dir}/ca.crt" \
        -CAserial "${cert_dir}/ca.srl" \
        -extensions req_ext \
        -extfile "${cert_conf_dir}/server.conf"


# TODO(apmelton) - remove and let Magnum generate client key/cert
echo "Generating Client key and cert"
cat > ${cert_conf_dir}/magnum-conductor.conf <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions     = req_ext
x509_extensions    = req_ext
prompt = no
copy_extensions = copyall
[req_distinguished_name]
CN = conductor.invalid
[req_ext]
extendedKeyUsage = clientAuth
EOF
openssl genrsa -out "${cert_dir}/magnum-conductor.key" 4096
openssl req -new -days 1000 \
        -key "${cert_dir}/magnum-conductor.key" \
        -out "${cert_dir}/magnum-conductor.csr" \
        -subj '/CN=magnum-conductor' \
        -reqexts req_ext \
        -extensions req_ext \
        -config "${cert_conf_dir}/magnum-conductor.conf"
openssl x509 -req -days 1000 \
        -in "${cert_dir}/magnum-conductor.csr" \
        -out "${cert_dir}/magnum-conductor.crt" \
        -CAkey "${cert_dir}/ca.key" \
        -CA "${cert_dir}/ca.crt" \
        -CAserial "${cert_dir}/ca.srl" \
        -extensions req_ext \
        -extfile "${cert_conf_dir}/magnum-conductor.conf"

# Make server certs accessible to apiserver.
chgrp $cert_group "${cert_dir}/server.key" "${cert_dir}/server.crt" "${cert_dir}/ca.crt"
chmod 600 "${cert_dir}/ca.key"
chmod 660 "${cert_dir}/server.key"
chmod 664 "${cert_dir}/ca.crt" "${cert_dir}/server.crt"
