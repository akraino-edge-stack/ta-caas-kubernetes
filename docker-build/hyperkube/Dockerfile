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

FROM centos:7.6.1810
MAINTAINER Krisztian Lengyel <krisztian.lengyel@nokia.com>

ARG ceph_version

# These packages explicitly needed to install specified ceph-common version
ARG ceph_packages="ceph-common-$ceph_version librados2-$ceph_version libradosstriper1-$ceph_version"

COPY kube-apiserver /kube-apiserver
COPY kube-controller-manager /kube-controller-manager
COPY kube-proxy /kube-proxy
COPY kube-scheduler /kube-scheduler

RUN useradd -u 144 -M -s /sbin/nologin kube \
&&  yum install -y https://download.ceph.com/rpm-luminous/el7/noarch/ceph-release-1-1.el7.noarch.rpm \
&&  yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
&&  yum install -y --setopt=skip_missing_names_on_install=False \
      ${ceph_packages} \
      conntrack-tools \
\
# Install kubernetes
&&  chmod a+x /kube-apiserver \
&&  chmod a+x /kube-controller-manager \
&&  chmod a+x /kube-proxy \
&&  chmod a+x /kube-scheduler \
# Clean up
&&  yum erase -y ceph-release \
&&  yum autoremove -y \
&&  yum clean all -y \
