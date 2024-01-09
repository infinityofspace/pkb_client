VERSION       = 1.2
RELEASE       = 1

# system paths
RESULT_PATH   = target
RPMBUILD_PATH = ~/rpmbuild

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

# file generators

python3-pkb-client.spec:
	@mkdir -p ${RESULT_PATH}/
	@printf '[INFO] generating python3-pkb-client.spec\n' | tee -a ${RESULT_PATH}/build.log
	@printf '%%global modname pkb_client\n\n'                         >  python3-pkb-client.spec
	@printf 'Name:           python3-pkb-client\n'                             >> python3-pkb-client.spec
	@printf 'Version:        '${VERSION}'\n'                                   >> python3-pkb-client.spec
	@printf 'Release:        '${RELEASE}'\n'                                   >> python3-pkb-client.spec
	@printf 'Obsoletes:      %%{name} <= %%{version}\n'                        >> python3-pkb-client.spec
	@printf 'Summary:        Unofficial client for the Porkbun API\n\n'        >> python3-pkb-client.spec
	@printf 'License:        MIT License\n'                                    >> python3-pkb-client.spec
	@printf 'URL:            https://github.com/infinityofspace/pkb_client/\n' >> python3-pkb-client.spec
	@printf 'Source0:        %%{name}-%%{version}.tar.xz\n\n'                  >> python3-pkb-client.spec
	@printf 'BuildArch:      noarch\n'                                         >> python3-pkb-client.spec
	@printf 'BuildRequires:  python3-setuptools\n'                             >> python3-pkb-client.spec
	@printf 'BuildRequires:  python3-rpm-macros\n'                             >> python3-pkb-client.spec
	@printf 'BuildRequires:  python3-py\n\n'                                   >> python3-pkb-client.spec
	@printf '%%?python_enable_dependency_generator\n\n'                        >> python3-pkb-client.spec
	@printf '%%description\n'                                                  >> python3-pkb-client.spec
	@printf 'Unofficial client for the Porkbun API\n\n'                        >> python3-pkb-client.spec
	@printf '%%prep\n'                                                         >> python3-pkb-client.spec
	@printf '%%autosetup -n %%{modname}_v%%{version}\n\n'                      >> python3-pkb-client.spec
	@printf '%%build\n'                                                        >> python3-pkb-client.spec
	@printf '%%py3_build\n\n'                                                  >> python3-pkb-client.spec
	@printf '%%install\n'                                                      >> python3-pkb-client.spec
	@printf '%%py3_install\n\n'                                                >> python3-pkb-client.spec
	@printf '%%files\n'                                                        >> python3-pkb-client.spec
	@printf '%%doc Readme.md\n'                                                >> python3-pkb-client.spec
	@printf '%%license License\n'                                              >> python3-pkb-client.spec
	@printf '%%{_bindir}/pkb-client\n'                                         >> python3-pkb-client.spec
	@printf '%%{python3_sitelib}/%%{modname}/\n'                               >> python3-pkb-client.spec
	@printf '%%{python3_sitelib}/%%{modname}-%%{version}*\n\n'                 >> python3-pkb-client.spec
	@printf '%%changelog\n'                                                    >> python3-pkb-client.spec
	@printf '...\n'                                                            >> python3-pkb-client.spec
	@printf '\n'                                                               >> python3-pkb-client.spec

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

