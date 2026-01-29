VERSION       = 2.2.0
RELEASE       = 1

# system paths
RESULT_PATH   = ${PWD}/target

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


BuildArch:      noarch

BuildRequires:  python3-devel

%description
Python client for the Porkbun API.

%prep
%autosetup -n %{modname}_v%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install

%files
%license License
%doc Readme.md
%{_bindir}/pkb-client
%{python3_sitelib}/%{modname}/
%{python3_sitelib}/%{modname}-*.dist-info/

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
	@cp -r pkb_client pyproject.toml requirements.txt setup.py License Readme.md \
		${RESULT_PATH}/pkb_client_v${VERSION}/
	@cd ${RESULT_PATH}; tar -I "pxz -9" -cf python3-pkb-client-${VERSION}.tar.xz pkb_client_v${VERSION}

${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm: ${RESULT_PATH}/python3-pkb-client-${VERSION}.tar.xz python3-pkb-client.spec
	@printf '[INFO] building python3-pkb-client-'${VERSION}-${RELEASE}'.src.rpm\n' | tee -a ${RESULT_PATH}/build.log
	@rpmbuild -D "_topdir ${RESULT_PATH}" -D "_sourcedir %{_topdir}" -bs python3-pkb-client.spec &>> ${RESULT_PATH}/build.log
	@mv ${RESULT_PATH}/SRPMS/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm ${RESULT_PATH}/

${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.noarch.rpm: ${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm
	@printf '[INFO] building python3-pkb-client-'${VERSION}-${RELEASE}'.noarch.rpm\n' | tee -a ${RESULT_PATH}/build.log
	@rpmbuild -D "_topdir ${RESULT_PATH}" --rebuild ${RESULT_PATH}/python3-pkb-client-${VERSION}-${RELEASE}.src.rpm &>> ${RESULT_PATH}/build.log
	@mv ${RESULT_PATH}/RPMS/noarch/python3-pkb-client-${VERSION}-${RELEASE}.noarch.rpm ${RESULT_PATH}/


