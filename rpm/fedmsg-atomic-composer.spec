%global modname fedmsg_atomic_composer

Name:           fedmsg-atomic-composer
Version:        0.0.1
Release:        1%{?dist}
Summary:        Composes atomic trees when Fedora repositories are updated

License:        GPLv3
URL:            https://github.com/lmacken/fedmsg-atomic-composer
Source0:        %{name}-%{version}.tar.bz2
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-mock

Requires:       fedmsg-hub
Requires:       rpm-ostree-toolbox

# Version requirement for specifying a list of topics
Requires:       python-moksha-hub >= 1.4.4

%description
This is a Fedmsg consumer that listens for when the Fedora
updates/rawhide/branched repositories sync with the master mirror, and
then triggers Atomic OSTree composes.

%prep
%setup -q


%build
%{__python} setup.py build


%check
%{__python} test.py


%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
install -D -m644 fedmsg.d/config.py %{buildroot}%{_sysconfdir}/fedmsg.d/%{modname}.py

for repo in rawhide f21; do
    install -D -m644 systemd/atomic-compose-$repo.service %{buildroot}%{_sysconfdir}/systemd/system/atomic-compose-${repo}.service
    install -D -m644 config/$repo.ini %{buildroot}/srv/fedora-atomic/$repo/config.ini
done


%files
%doc README.rst LICENSE ansible
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{modname}*.egg-info
%config(noreplace) %{_sysconfdir}/fedmsg.d/%{modname}.py*
%{_sysconfdir}/systemd/system/atomic-compose-*.service
/srv/fedora-atomic/


%changelog
* Mon Oct 20 2014 Luke Macken <lmacken@redhat.com> - 0.0.1-1
- Initial package
