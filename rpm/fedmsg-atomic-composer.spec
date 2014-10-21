%global modname fedmsg_atomic_composer

Name:           fedmsg-atomic-composer
Version:        0.0.1
Release:        1%{?dist}
Summary:        Composes atomic trees when Fedora repositories are updated

License:        GPLv3
URL:            https://github.com/lmacken/fedmsg-atomic-composer
Source0:        %{name}-%{version}.tar.bz2

BuildRequires:  python-devel
BuildRequires:  python-mock

Requires:       fedmsg-hub
Requires:       rpm-ostree-toolbox

%description
This is a Fedmsg consumer that listens for when the Fedora
updates/rawhide/branched repositories sync with the master mirror, and
then triggers Atomic OSTree composes.

%prep
%setup -q


%build
%{__python} setup.py build


%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
install -D fedmsg.d/config.py %{buildroot}%{_sysconfdir}/fedmsg.d/%{modname}.py


%files
%doc README.rst LICENSE
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{modname}*.egg-info
%{_sysconfdir}/fedmsg.d/%{modname}.py*


%changelog
* Mon Oct 20 2014 Luke Macken <lmacken@redhat.com>
- Initial package
