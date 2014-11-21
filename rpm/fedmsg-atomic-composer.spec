%global modname fedmsg_atomic_composer

Name:           fedmsg-atomic-composer
Version:        0.0.1
Release:        2%{?dist}
Summary:        Composes atomic trees when Fedora repositories are updated

License:        GPLv3
URL:            https://github.com/fedora-infra/fedmsg-atomic-composer
Source0:        %{name}-%{version}.tar.bz2
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools

Requires:       mock
Requires:       python-mako
Requires:       python-click

%description
This is a Fedmsg consumer that listens for when the Fedora
updates/rawhide/branched repositories sync with the master mirror, and
then triggers Atomic OSTree composes.

%package consumer
Summary:        A fedmsg-driven atomic tree composer

# Version requirement for specifying a list of topics
Requires:       python-moksha-hub >= 1.4.4
Requires:       fedmsg-hub

%description consumer
This sub-package contains a fedmsg consumer that triggers Atomic tree composes
when new Fedora repositories sync to the master mirror.

%prep
%setup -q


%build
%{__python} setup.py build


%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
mkdir -p %{buildroot}/srv/fedora-atomic/

mkdir -p %{buildroot}%{_sysconfdir}/fedmsg.d
ln -sf %{python_sitelib}/%{modname}/config.py %{buildroot}%{_sysconfdir}/fedmsg.d/%{modname}.py

%if 0%{?rhel} && 0%{?rhel} <= 6
install -D -m644 systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
%endif

%files
%doc README.rst LICENSE ansible
%{_bindir}/%{name}-cli
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{modname}*.egg-info
%attr(755, rpmostreecompose, rpmostreecompose) /srv/fedora-atomic/

%files consumer
%config(noreplace) %{_sysconfdir}/fedmsg.d/%{modname}.py*
%if 0%{?rhel} && 0%{?rhel} <= 6
%{_unitdir}/%{name}.service
%endif


%changelog
* Tue Nov 18 2014 Luke Macken <lmacken@redhat.com> - 0.0.1-2
- Create a consumer subpackage

* Mon Oct 20 2014 Luke Macken <lmacken@redhat.com> - 0.0.1-1
- Initial package
