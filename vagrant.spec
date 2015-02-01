# NOTE:
# - release notes: https://github.com/mitchellh/vagrant/blob/master/CHANGELOG.md
Summary:	Provisioning and deployment of virtual instances
Name:		vagrant
Version:	1.7.1
# NOTE: test that it actually works before doing rel "1"
Release:	0.9
License:	MIT
Group:		Applications/Emulators
Source0:	https://github.com/mitchellh/vagrant/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	6bfb1440145f943e7b683ac99d06adec
Source1:	%{name}.sh
Patch0:		source_root.patch
Patch1:		rubygems.patch
Patch2:		no-warning.patch
Patch3:		Vagrantfile.patch
Patch4:		version.patch
Patch5:		no-gems.patch
Patch6:		checkpoint.patch
URL:		http://www.vagrantup.com/
BuildRequires:	bash
BuildRequires:	rpm-rubyprov
BuildRequires:	ruby > 1:2.0
%if %{with tests}
BuildRequires:	ruby-contest >= 0.1.2
BuildRequires:	ruby-minitest >= 2.5.1
BuildRequires:	ruby-mocha
BuildRequires:	ruby-rake
BuildRequires:	ruby-rspec >= 2.14.0
%endif
Requires:	VirtualBox
Requires:	bsdtar
Requires:	curl
Requires:	ruby-bundler >= 1.5.2
Requires:	ruby-childprocess >= 0.5.0
Requires:	ruby-erubis >= 2.7.0
Requires:	ruby-i18n >= 0.6.0
Requires:	ruby-json
Requires:	ruby-listen >= 2.7.1
Requires:	ruby-log4r < 1.1.11
Requires:	ruby-log4r >= 1.1.9
Requires:	ruby-net-scp >= 1.1.0
Requires:	ruby-net-ssh < 2.8.0
Requires:	ruby-net-ssh >= 2.6.6
Requires:	ruby-rubygems
Suggests:	VirtualBox-gui
Suggests:	rdesktop
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir	%{_datadir}/%{name}
%define		bash_compdir	%{_datadir}/bash-completion/completions

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
Requires:	bash-completion >= 2.0

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
Requires:	sudo >= 1.7.4p3-2
Requires:	which
Provides:	group(vagrant)
Provides:	user(vagrant)

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

%description doc
Ruby documentation for %{gem_name}

%prep
%setup -q
#%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

VERSION=$(cat version.txt)
sed -i -e "s/__VERSION__/$VERSION/" lib/vagrant/version.rb

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%build
# make gemspec self-contained
ruby -r rubygems -e 'spec = eval(File.read("%{name}.gemspec"))
	File.open("%{name}-%{version}.gemspec", "w") do |file|
	file.puts spec.to_ruby_for_cache
end'

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{ruby_gemdir}/gems/%{name}-%{version},%{ruby_specdir},%{_bindir}}
cp -a lib bin keys plugins templates $RPM_BUILD_ROOT%{ruby_gemdir}/gems/%{name}-%{version}
cp -p %{name}-%{version}.gemspec $RPM_BUILD_ROOT%{ruby_specdir}
install -p %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/%{name}

install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p contrib/bash/completion.sh $RPM_BUILD_ROOT%{bash_compdir}/%{name}

# guest
install -d $RPM_BUILD_ROOT/etc/sudoers.d
echo 'vagrant ALL=(ALL) NOPASSWD: ALL' > $RPM_BUILD_ROOT/etc/sudoers.d/%{name}

install -d $RPM_BUILD_ROOT{%{vg_root},%{vg_home}/.ssh}
cp -p /etc/skel/.bash*  $RPM_BUILD_ROOT%{vg_home}

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
#%{ruby_vendorlibdir}/vagrant.rb
#%{ruby_vendorlibdir}/vagrant
#%{_appdir}

%dir %{ruby_gemdir}/gems/%{name}-%{version}
%dir %{ruby_gemdir}/gems/%{name}-%{version}/bin
%attr(755,root,root) %{ruby_gemdir}/gems/%{name}-%{version}/bin/*
%{ruby_gemdir}/gems/%{name}-%{version}/keys
%{ruby_gemdir}/gems/%{name}-%{version}/lib
%{ruby_gemdir}/gems/%{name}-%{version}/plugins
%{ruby_gemdir}/gems/%{name}-%{version}/templates

%{ruby_specdir}/%{name}-%{version}.gemspec

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/%{name}

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
