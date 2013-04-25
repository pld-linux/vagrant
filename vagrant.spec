# NOTE:
# - release notes: https://github.com/mitchellh/vagrant/blob/master/CHANGELOG.md
Summary:	Provisioning and deployment of virtual instances
Name:		vagrant
Version:	1.2.2
Release:	0.27
License:	MIT
Group:		Applications/Emulators
Source0:	https://github.com/mitchellh/vagrant/archive/v%{version}.tar.gz?/%{name}-%{version}.tgz
# Source0-md5:	68d2caa329b314982266e45be38c928b
Patch0:		source_root.patch
Patch1:		rubygems.patch
Patch2:		no-warning.patch
URL:		http://vagrantup.com/
BuildRequires:	ruby-contest >= 0.1.2
BuildRequires:	ruby-minitest >= 2.5.1
BuildRequires:	ruby-mocha
BuildRequires:	ruby-rake
BuildRequires:	ruby-rspec-core >= 2.11.0
BuildRequires:	ruby-rspec-expectations >= 2.11.0
BuildRequires:	ruby-rspec-mocks >= 2.11.0
Requires:	ruby-childprocess >= 0.3.7
Requires:	ruby-erubis >= 2.7.0
Requires:	ruby-i18n >= 0.6.0
Requires:	ruby-json < 1.8.0
Requires:	ruby-json >= 1.5.1
Requires:	ruby-log4r >= 1.1.9
Requires:	ruby-net-scp >= 1.1.0
Requires:	ruby-net-ssh >= 2.6.6
Requires:	ruby-rubygems
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir	%{_datadir}/%{name}

%define		vg_home	/home/vagrant
%define		vg_root	/vagrant

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

%package -n bash-completion-%{name}
Summary:	bash-completion for %{name}
Group:		Applications/Shells
Requires:	%{name}
Requires:	bash-completion
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n bash-completion-%{name}
bash-completion for %{name}.

%package guest
Summary:	Vagrant guest
Group:		Development/Building
URL:		http://docs-v1.vagrantup.com/v1/docs/base_boxes.html
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	/etc/pld-release
Requires:	kernel(vboxsf)
Requires:	openssh-server
Requires:	sudo
Requires:	which
Provides:	group(vagrant)
Provides:	user(vagrant)
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description guest
This is the package to be installed in Vagrant guest.

WARNING: This package installs insecure keypair to vagant user. Do not
install this package in a box that is accessible others but you.

These keys are the "insecure" public/private keypair we offer to base
box creators for use in their base boxes so that vagrant installations
can automatically SSH into the boxes.

See: <https://github.com/mitchellh/vagrant/tree/master/keys/>.

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
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{ruby_vendorlibdir},%{_bindir},%{_appdir}}
cp -a bin/* $RPM_BUILD_ROOT%{_bindir}
cp -a lib/* $RPM_BUILD_ROOT%{ruby_vendorlibdir}
cp -a config plugins templates $RPM_BUILD_ROOT%{_appdir}

install -d $RPM_BUILD_ROOT/etc/bash_completion.d
mv contrib/bash/completion.sh $RPM_BUILD_ROOT/etc/bash_completion.d/%{name}.sh

# guest
install -d $RPM_BUILD_ROOT/etc/sudoers.d
echo 'vagrant ALL=(ALL) NOPASSWD: ALL' > $RPM_BUILD_ROOT/etc/sudoers.d/%{name}

install -d $RPM_BUILD_ROOT{%{vg_root},%{vg_home}/.ssh}
cp -a /etc/skel/.bash*  $RPM_BUILD_ROOT%{vg_home}

# Since Vagrant only supports key-based authentication for SSH, we must
# set up the vagrant user to use key-based authentication. We can get the
# public key used by the Vagrant gem directly from its Github repository.
cp -p keys/vagrant.pub $RPM_BUILD_ROOT%{vg_home}/.ssh/authorized_keys

%clean
rm -rf $RPM_BUILD_ROOT

%pre guest
%groupadd -g 291 vagrant
%useradd -u 291 -g vagrant -G wheel -c "Vagrant user" -s /bin/bash -d %{vg_home} vagrant

%postun guest
if [ "$1" = "0" ]; then
	%userremove vagrant
	%groupremove vagrant
fi

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/vagrant
%{ruby_vendorlibdir}/vagrant.rb
%{ruby_vendorlibdir}/vagrant
%{_appdir}

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
/etc/bash_completion.d/*

%files guest
%defattr(644,root,root,755)
%attr(440,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sudoers.d/%{name}
%dir %attr(750,vagrant,vagrant) %{vg_home}
%dir %attr(700,vagrant,vagrant) %{vg_home}/.ssh
%attr(600,vagrant,vagrant) %config(noreplace) %verify(not md5 mtime size) %{vg_home}/.ssh/authorized_keys
%dir %attr(640,vagrant,vagrant) %{vg_home}/.bash*
%dir %attr(700,root,root) %{vg_root}

%if 0
%files doc
%defattr(644,root,root,755)
%doc %{gem_docdir}
%endif
