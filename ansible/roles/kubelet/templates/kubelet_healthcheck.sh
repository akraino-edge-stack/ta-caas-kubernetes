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

error=0

while true
do
  set +e
  result="$(curl 127.0.0.1:{{ kubelet_healthcheck_port }}/healthz)"
  set -e
  if [ "$result" == "ok" ]
  then
    echo "Healtcheck success."
    error=0
    set +e
    uncordonresult="$(/usr/bin/kubectl uncordon {{ ansible_host }} 2>&1)"
    set -e
    echo "$uncordonresult"
  else
    echo "Healtcheck failed."
    error=$(($error+1))
  fi
  if [ "$error" -ge "5" ]
  then
    activeState="$(systemctl show -p ActiveState --value kubelet)"
    if [[ "$activeState" == "deactivating" ]] || [[ "$activeState" == "activating" ]]
    then
      echo "Kubelet is possibly restarting."
      error=0
    else
      echo "Error with kubelet (Healtcheck failed 5 times) restarting it."
      systemctl restart kubelet.service
    fi
  fi
  sleep 1
done
