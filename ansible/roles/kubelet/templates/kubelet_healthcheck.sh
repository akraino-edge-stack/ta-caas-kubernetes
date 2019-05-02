#!/bin/bash
# Copyright 2019 Nokia
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

wait_for_file () {
  while [[ ! -f $1 ]]
  do
    echo "Waiting for file $1"
    sleep 1
  done
}


CERT_AUTH="/etc/openssl/ca.pem"
CLIENT_CER="/etc/kubernetes/ssl/kubelet-server.pem"
CLIENT_KEY="/etc/kubernetes/ssl/kubelet-server-key.pem"
wait_for_file $CERT_AUTH
wait_for_file $CLIENT_CER
wait_for_file $CLIENT_KEY


keepdoing="true"
error=0

while true
do
  if [[ "$keepdoing" == "true" ]]
  then
    echo "Waiting for kubernetes node to become ready..."
    uncordon_ready=$( /usr/bin/kubectl get node --show-labels | grep -i "{{ nodename }}" | grep -i "ready" | grep -i "SchedulingDisabled" | wc -l )
    if [[ "$uncordon_ready" -eq "1" ]]
    then
      keepdoing="false"
      /usr/bin/kubectl uncordon {{ ansible_host }} || echo "Post start kubelet, this node was never cordoned."
      echo "Node uncordoned, and ready!"
    fi
    node_ready=$( /usr/bin/kubectl get node --show-labels | grep -i "{{ nodename }}" |  grep -i " ready " | wc -l )
    if [[ "$node_ready" -eq "1" ]]
    then
      keepdoing="false"
      echo "Node become ready."
    fi
  fi
  set +e
  result="$(wget --timeout 10 --tries 5 --ca-certificate $CERT_AUTH --certificate $CLIENT_CER --private-key $CLIENT_KEY --spider https://{{ ansible_host }}:10250/healthz 2>&1 | grep 'HTTP' | grep -E -o '[[:digit:]]{3}')"

  set -e
  if [ "$result" == "200" ]
  then
    echo "Healtcheck success"
    error=0
  else
    echo "Healtcheck failed"
    error=$(($error+1))
  fi
  if [ "$error" -ge "5" ]
  then
    echo "Error with kubelet (Healtcheck failed 5 times) restarting it"
    systemctl restart kubelet.service
  fi
  sleep 30
done
