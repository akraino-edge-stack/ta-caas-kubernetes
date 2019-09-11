#!/bin/bash -u
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


# check if node was active
# if it was and node number is greater the 1, cordon and drain for graceful shutdown
result=$( /usr/bin/kubectl get nodes | grep {{ networking.infra_internal.ip }} | wc -l )
controllernumbers=$( /usr/bin/kubectl get node --show-labels | grep -i ready | grep caas_master | wc -l )
if [[ "$result" -ge "1" ]] && [[ $controllernumbers -gt 1 ]]
then
  /usr/bin/kubectl cordon {{ networking.infra_internal.ip }}
  /usr/bin/kubectl drain {{ networking.infra_internal.ip }}  --force --ignore-daemonsets --delete-local-data --grace-period=30
fi

# check if kubelet is running
kubelet_is_still_running=$(  ps -aux | grep "/kubelet " | grep -v color | wc -l )
if [[ "$kubelet_is_still_running" -ge "1" ]]
then
  # stop kubelet by force
  kubeletpid=$( ps -aux | grep "/kubelet " | grep -v color | awk -F' ' '{ print $2 }')
  kill -9 $kubeletpid
fi

for D in {{ caas.kubelet_root_directory }}/pods/*
do
  if [ -d "${D}" ]
  then
    rm -rf {{ caas.kubelet_root_directory }}/pods/${D} || echo "Can not remove directory, skipping it"
  fi
done
