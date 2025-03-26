VERSION       = 2.0.0
RELEASE       = 1

# system paths
RESULT_PATH   = target
RPMBUILD_PATH = ~/rpmbuild

#------------------------------------------------------------------------------
# COMMANDS
#------------------------------------------------------------------------------

all: help

help:
	@printf '\nusuage make ...\n'
	@printf '  clean        -> remove results\n'
	@printf '  package      -> package archive for deploy .tar.xz\n'
	@printf '  build-spec   -> build python3-pkb-client.spec\n'
	@printf '  build-srpm   -> build python3-pkb-client-'${VERSION}-${RELEASE}'.src.rpm\n'
	@printf '  build-rpm    -> build python3-pkb-client-'${VERSION}-${RELEASE}'.noarch.rpm\n'

# helper commands

clean:
	@printf '[INFO] removing '${RESULT_PATH}/'\n'
	@rm -rf python3-pkb-client.spec ${RESULT_PATH}/

package: ${RESULT_PATH}/python3-pkb-client-${VERSION}.tar.xz

build-spec: python3-pkb-client.spec

build-srpm: ${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm

build-rpm: ${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.noarch.rpm


#------------------------------------------------------------------------------
# FILE GENERATORs
#------------------------------------------------------------------------------

define _spec_generator
cat << EOF
%global modname pkb_client

Name:           python3-pkb-client
Version:        ${VERSION}
Release:        ${RELEASE}
Obsoletes:      %{name} <= %{version}
Summary:        Python client for the Porkbun API

License:        MIT License
URL:            https://github.com/infinityofspace/pkb_client/
Source0:        %{name}-%{version}.tar.xz

Requires:       python3-requests
Requires:       python3-dns
Requires:       python3-responses

BuildArch:      noarch
BuildRequires:  python3-setuptools
BuildRequires:  python3-rpm-macros
BuildRequires:  python3-py

%?python_enable_dependency_generator

%description
Python client for the Porkbun API

%%prep
%autosetup -n %{modname}_v%{version}

%build
%py3_build

%install
%py3_install

%files
%doc Readme.md
%license License
%{_bindir}/pkb-client
%{python3_sitelib}/%{modname}/
%{python3_sitelib}/%{modname}-%{version}*

%changelog
...

EOF
endef
export spec_generator = $(value _spec_generator)

python3-pkb-client.spec:
	@mkdir -p ${RESULT_PATH}/
	@printf '[INFO] generating python3-pkb-client.spec\n' | tee -a ${RESULT_PATH}/build.log
	@ VERSION=${VERSION} RELEASE=${RELEASE} eval "$$spec_generator" > python3-pkb-client.spec

${RESULT_PATH}/python3-pkb-client-${VERSION}.tar.xz:
	@mkdir -p ${RESULT_PATH}/
	@printf '[INFO] packing python3-pkb-client-'${VERSION}'.tar.xz\n' | tee -a ${RESULT_PATH}/build.log
	@mkdir -p ${RESULT_PATH}/pkb_client_v${VERSION}
	@cp -r pkb_client requirements.txt setup.py License Readme.md \
		${RESULT_PATH}/pkb_client_v${VERSION}/
	@cd ${RESULT_PATH}; tar -I "pxz -9" -cf python3-pkb-client-${VERSION}.tar.xz pkb_client_v${VERSION}

${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm: ${RESULT_PATH}/python3-pkb-client-${VERSION}.tar.xz python3-pkb-client.spec
	@printf '[INFO] building python3-pkb-client-'${VERSION}-${RELEASE}'.src.rpm\n' | tee -a ${RESULT_PATH}/build.log
	@mkdir -p ${RPMBUILD_PATH}/SOURCES/
	@cp ${RESULT_PATH}/python3-pkb-client-${VERSION}.tar.xz ${RPMBUILD_PATH}/SOURCES/
	@rpmbuild -bs python3-pkb-client.spec &>> ${RESULT_PATH}/build.log
	@mv ${RPMBUILD_PATH}/SRPMS/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm ${RESULT_PATH}/

${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.noarch.rpm: ${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm
	@printf '[INFO] building python3-pkb-client-'${VERSION}-${RELEASE}'.noarch.rpm\n' | tee -a ${RESULT_PATH}/build.log
	@mkdir -p ${RPMBUILD_PATH}/SRPMS/
	@cp ${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm ${RPMBUILD_PATH}/SRPMS/
	@rpmbuild --rebuild ${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm &>> ${RESULT_PATH}/build.log
	@mv ${RPMBUILD_PATH}/RPMS/noarch/python3-pkb-client-${VERSION}-${RELEASE}.noarch.rpm ${RESULT_PATH}/

