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

ARG CENTOS_BASE
FROM $CENTOS_BASE
MAINTAINER Krisztian Lengyel <krisztian.lengyel@nokia.com>

ARG KUBERNETES_VERSION
ARG go_version
ARG go_install_dir="/usr/local/go"
ENV GOPATH="/build"
ARG binaries
ARG build_packages="gcc gcc-c++ glibc-devel make autoconf git which libtool"
ENV GOROOT_BOOTSTRAP="$go_install_dir"
ENV GOOS=linux
ENV PATH="$GOPATH/bin:$go_install_dir/bin:$PATH"

RUN set -x \
&& env \
&&  yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
&&  yum install -y --setopt=skip_missing_names_on_install=False \
      ${build_packages} \
      bash \
      golang \
      curl \
      binutils \
      file \
      rsync \
      tar \
      coreutils \
      grep \
      util-linux \
&&  mkdir -p ${go_install_dir} \
&&  if [ $(uname -m) == 'aarch64' ]; then HOST_ARCH=arm64; else HOST_ARCH=amd64; fi \
&&  curl -fsSL -k https://dl.google.com/go/go${go_version}.linux-${HOST_ARCH}.tar.gz | tar zx --strip-components=1 -C ${go_install_dir} \
#
# Build Kubernetes
#
&&  mkdir -p ${GOPATH}/src/github.com/kubernetes/kubernetes \
&&  curl -fsSL https://github.com/kubernetes/kubernetes/archive/v${KUBERNETES_VERSION}.tar.gz | tar zx --strip-components=1 -C ${GOPATH}/src/github.com/kubernetes/kubernetes \
&&  cd ${GOPATH}/src/github.com/kubernetes/kubernetes \
&&  make WHAT="cmd/kubelet" \
&&  make WHAT="cmd/kubectl" \
&&  make WHAT="cmd/kube-apiserver" \
&&  make WHAT="cmd/kube-controller-manager" \
&&  make WHAT="cmd/kube-proxy" \
&&  make WHAT="cmd/kube-scheduler" \
&&  mkdir -p ${binaries} \
&&  mv ./_output/local/bin/linux/amd64/{kubelet,kubectl,kube-apiserver,kube-controller-manager,kube-proxy,kube-scheduler} ${binaries}/ \
