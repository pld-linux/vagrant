Summary:	Provisioning and deployment of virtual instances
Name:		vagrant
Version:	1.1.2
Release:	0.4
License:	MIT
Group:		Applications/Emulators
URL:		http://vagrantup.com/
Source0:	http://files.vagrantup.com/packages/67bd4d30f7dbefa7c0abc643599f0244986c38c8/vagrant_i686.rpm?/%{name}-%{version}.i686.rpm
# Source0-md5:	83093a71588f97a9eb69fa7fe07418b9
Source1:	http://files.vagrantup.com/packages/67bd4d30f7dbefa7c0abc643599f0244986c38c8/vagrant_x86_64.rpm?/%{name}-%{version}.x86_64.rpm
# Source1-md5:	3efa3ac73988c565e6b3236da6867557
BuildRequires:	pkgconfig
BuildRequires:	rpm-pythonprov
BuildRequires:	rpm-utils
BuildRequires:	ruby
BuildRequires:	sed >= 4.0
BuildRequires:	which
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir	%{_libdir}/%{name}

%define		_enable_debug_packages		0
%define		no_install_post_strip		1
%define		no_install_post_check_so	1
%define		no_install_post_chrpath		1

%description
Vagrant offers scripted provisioning and deployment of virtual
instances. While VirtualBox is the main target, future versions may
support other hypervizors as well.

The vision of the project is to create a tool to transparently manage
all the complex parts of modern development within a virtual
environment without affecting the everyday workflow of the developer
too much. A long term goal is moving all development into virtualized
environments by making it easier to do so than not to. Additionally,
work is ongoing to have Vagrant run identically on every major
consumer OS platform (Linux, Mac OS X, and Windows).

%package doc
Summary:	Documentation for %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description doc
Ruby documentation for %{gem_name}

%prep
%setup -qcT
%ifarch %{ix86}
SOURCE=%{S:0}
%endif
%ifarch %{x8664}
SOURCE=%{S:1}
%endif

V=$(rpm -qp --nodigest --nosignature --qf '%{V}' $SOURCE)
test "$V" = "%{version}"

rpm2cpio $SOURCE | cpio -i -d

mv opt/vagrant/* .

grep -rl /tmp/vagrant-temp embedded | xargs sed -i -e 's,/tmp/vagrant-temp,%{_appdir},'

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_appdir}}

cp -a bin embedded $RPM_BUILD_ROOT%{_appdir}
ln -s %{_appdir}/bin/%{name} $RPM_BUILD_ROOT%{_bindir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/vagrant

%defattr(-,root,root,-)
%{_appdir}

%if 0
%files doc
%defattr(644,root,root,755)
%doc %{gem_docdir}
%endif
