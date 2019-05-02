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

DOCKER_ARGS="--tlsverify --tlscacert=${CLIENT_CA_CERT} --tlscert=${CLIENT_CERT} --tlskey=${CLIENT_KEY} -H ${DOCKER_HOST}"

# check if kubelet is running
kubelet_is_running=$( ps -aux | grep "/kubelet " | grep -v color | wc -l )
if [[ "$kubelet_is_running" -ge "1" ]]
then
  # stop kubelet by force
  kubeletpid=$( ps -aux | grep "/kubelet " | grep -v color | awk -F' ' '{ print $2 }' )
  kill -9 $kubeletpid
fi

for D in /var/lib/kubelet/pods/*
do
  if [ -d "${D}" ]
  then
    rm -rf /var/lib/kubelet/pods/${D} || echo "Can not remove directory, skipping it"
  fi
done

echo "Pre kubelet start ended."
