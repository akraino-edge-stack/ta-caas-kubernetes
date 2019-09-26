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

%define COMPONENT kubernetes
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 1.15.4
%define RPM_MINOR_VERSION 0
%define IMAGE_TAG %{RPM_MAJOR_VERSION}-%{RPM_MINOR_VERSION}
%define KUBERNETESPAUSE_VERSION 3.1

%define go_version 1.12.9
%define ceph_version 12.2.5
%define binary_build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/binary-save
%define docker_build_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-build
%define docker_save_dir %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-save
%define built_binaries_dir /binary-save

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service %{COMPONENT} component
License:        %{_platform_licence} and Apache License and GNU General Public License v2.0 only and GNU Lesser General Public License v2.1 only and MIT license and BSD and MIT license and ISC License and Creative Commons Attribution ShareAlike 4.0 International and Mozilla Public License and COMMON DEVELOPMENT AND DISTRIBUTION LICENSE and Lesser General Public License and Creative Commons - Public Domain and Creative Commons Public License and BSD 3-Clause License
BuildArch:      %{_arch}
Vendor:         %{_platform_vendor} and kubernetes/kubernetes unmodified
Source0:        %{name}-%{version}.tar.gz

Requires: docker-ce >= 18.09.2, rsync
BuildRequires: docker-ce-cli >= 18.09.2, xz

# more info at: https://fedoraproject.org/wiki/Packaging:Debuginfo No build ID note in Flannel
%global debug_package %{nil}

%description
This rpm contains the %{COMPONENT} container for CaaS subsystem.
This container contains the %{COMPONENT} service.

%prep
%autosetup

# Build Kubernetes binaries
%build
set -x
docker build \
  --network=host \
  --no-cache \
  --force-rm \
  --build-arg HTTP_PROXY="${http_proxy}" \
  --build-arg HTTPS_PROXY="${https_proxy}" \
  --build-arg NO_PROXY="${no_proxy}" \
  --build-arg http_proxy="${http_proxy}" \
  --build-arg https_proxy="${https_proxy}" \
  --build-arg no_proxy="${no_proxy}" \
  --build-arg KUBERNETES_VERSION="%{version}" \
  --build-arg go_version="%{go_version}" \
  --build-arg binaries="%{built_binaries_dir}" \
  --tag kubernetes-builder:%{IMAGE_TAG} \
  %{docker_build_dir}/kubernetes-builder

builder_container=$(docker run -id --rm --network=none --entrypoint=/bin/sh kubernetes-builder:%{IMAGE_TAG})
mkdir -p %{binary_build_dir}
docker cp ${builder_container}:%{built_binaries_dir}/kubelet %{binary_build_dir}/
docker cp ${builder_container}:%{built_binaries_dir}/kubectl %{binary_build_dir}/
docker cp ${builder_container}:%{built_binaries_dir}/kube-apiserver %{binary_build_dir}/
docker cp ${builder_container}:%{built_binaries_dir}/kube-controller-manager %{binary_build_dir}/
docker cp ${builder_container}:%{built_binaries_dir}/kube-proxy %{binary_build_dir}/
docker cp ${builder_container}:%{built_binaries_dir}/kube-scheduler %{binary_build_dir}/
mkdir -p %{binary_build_dir}/cni
sync
docker rm -f ${builder_container}
docker rmi kubernetes-builder:%{IMAGE_TAG}

# Build hyperkube container image
rsync -av %{binary_build_dir}/kube-apiserver %{docker_build_dir}/hyperkube/
rsync -av %{binary_build_dir}/kube-controller-manager %{docker_build_dir}/hyperkube/
rsync -av %{binary_build_dir}/kube-proxy %{docker_build_dir}/hyperkube/
rsync -av %{binary_build_dir}/kube-scheduler %{docker_build_dir}/hyperkube/
docker build \
  --network=host \
  --no-cache \
  --force-rm \
  --build-arg HTTP_PROXY="${http_proxy}" \
  --build-arg HTTPS_PROXY="${https_proxy}" \
  --build-arg NO_PROXY="${no_proxy}" \
  --build-arg http_proxy="${http_proxy}" \
  --build-arg https_proxy="${https_proxy}" \
  --build-arg no_proxy="${no_proxy}" \
  --build-arg ceph_version="%{ceph_version}" \
  --tag hyperkube:%{IMAGE_TAG} \
  %{docker_build_dir}/hyperkube
mkdir -p %{docker_save_dir}
docker save hyperkube:%{IMAGE_TAG} | xz -z -T2 > "%{docker_save_dir}/hyperkube:%{IMAGE_TAG}.tar"
docker rmi hyperkube:%{IMAGE_TAG}

# Build kubernetes pause container image
docker build \
  --network=host \
  --no-cache \
  --force-rm \
  --build-arg HTTP_PROXY="${http_proxy}" \
  --build-arg HTTPS_PROXY="${https_proxy}" \
  --build-arg NO_PROXY="${no_proxy}" \
  --build-arg http_proxy="${http_proxy}" \
  --build-arg https_proxy="${https_proxy}" \
  --build-arg no_proxy="${no_proxy}" \
  --build-arg KUBERNETESPAUSE_VERSION="%{KUBERNETESPAUSE_VERSION}" \
  --tag kubernetespause:%{KUBERNETESPAUSE_VERSION} \
  %{docker_build_dir}/kubernetespause
mkdir -p %{docker_save_dir}
docker save kubernetespause:%{KUBERNETESPAUSE_VERSION} | xz -z -T2 > "%{docker_save_dir}/kubernetespause:%{KUBERNETESPAUSE_VERSION}.tar"
docker rmi kubernetespause:%{KUBERNETESPAUSE_VERSION}

%install
mkdir -p %{buildroot}/%{_caas_container_tar_path}
rsync -av %{docker_save_dir}/* %{buildroot}/%{_caas_container_tar_path}/

mkdir -p %{buildroot}/%{_roles_path}
rsync -av ansible/roles/* %{buildroot}/%{_roles_path}/

mkdir -p %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/* %{buildroot}/%{_playbooks_path}/

mkdir -p %{buildroot}/usr/bin/
install -D -m 0755 %{binary_build_dir}/kubectl %{buildroot}/usr/bin/kubectl
install -D -m 0755 %{binary_build_dir}/kubelet %{buildroot}/usr/bin/kubelet

mkdir -p %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/* %{buildroot}/%{_playbooks_path}/

%files
%{_caas_container_tar_path}/*.tar
%{_roles_path}/
%{_playbooks_path}/
/usr/bin/kubectl
/usr/bin/kubelet

%preun

%post
mkdir -p %{_postconfig_path}
ln -s %{_playbooks_path}/bootstrap_kube_proxy.yaml          %{_postconfig_path}/
ln -s %{_playbooks_path}/bootstrap_kubelet.yaml             %{_postconfig_path}/
ln -s %{_playbooks_path}/kube_master.yaml                   %{_postconfig_path}/
ln -s %{_playbooks_path}/kube_secret_key_creation.yaml      %{_postconfig_path}/
ln -s %{_playbooks_path}/kube_secret_key_distribution.yaml  %{_postconfig_path}/
ln -s %{_playbooks_path}/kube_token_creation.yaml           %{_postconfig_path}/
ln -s %{_playbooks_path}/kube_token_distribution.yaml       %{_postconfig_path}/
ln -s %{_playbooks_path}/kubernetes_ceph.yaml               %{_postconfig_path}/
ln -s %{_playbooks_path}/master_kube_proxy.yaml             %{_postconfig_path}/
ln -s %{_playbooks_path}/master_kubelet.yaml                %{_postconfig_path}/
ln -s %{_playbooks_path}/service_account_creation.yaml      %{_postconfig_path}/
ln -s %{_playbooks_path}/service_account_distribution.yaml  %{_postconfig_path}/

%postun
if [ $1 -eq 0 ]; then
  rm -f %{_postconfig_path}/bootstrap_kube_proxy.yaml
  rm -f %{_postconfig_path}/bootstrap_kubelet.yaml
  rm -f %{_postconfig_path}/kube_master.yaml
  rm -f %{_postconfig_path}/kube_secret_key_creation.yaml
  rm -f %{_postconfig_path}/kube_secret_key_distribution.yaml
  rm -f %{_postconfig_path}/kube_token_creation.yaml
  rm -f %{_postconfig_path}/kube_token_distribution.yaml
  rm -f %{_postconfig_path}/kubernetes_ceph.yaml
  rm -f %{_postconfig_path}/master_kube_proxy.yaml
  rm -f %{_postconfig_path}/master_kubelet.yaml
  rm -f %{_postconfig_path}/service_account_creation.yaml
  rm -f %{_postconfig_path}/service_account_distribution.yaml
fi

%clean
rm -rf ${buildroot}
