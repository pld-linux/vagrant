# NOTE:
# - release notes: https://github.com/mitchellh/vagrant/blob/master/CHANGELOG.md
#
# Conditional build:
%bcond_without	vagrant	# build vagrant package

Summary:	Provisioning and deployment of virtual instances
Name:		vagrant
Version:	1.1.5
Release:	0.18
License:	MIT
Group:		Applications/Emulators
URL:		http://vagrantup.com/
Source0:	http://files.vagrantup.com/packages/64e360814c3ad960d810456add977fd4c7d47ce6/vagrant_i686.rpm?/%{name}-%{version}.i686.rpm
# Source0-md5:	d62c19378ca3e731b1a76bc6336d7b53
Source1:	http://files.vagrantup.com/packages/64e360814c3ad960d810456add977fd4c7d47ce6/vagrant_x86_64.rpm?/%{name}-%{version}.x86_64.rpm
# Source1-md5:	b4a7d312e5f0c279dbadd86fe12df4e6
Source2:	https://raw.github.com/mitchellh/vagrant/master/keys/%{name}.pub
# Source2-md5:	b440b5086dd12c3fd8abb762476b9f40
BuildRequires:	bash
BuildRequires:	file
BuildRequires:	pkgconfig
BuildRequires:	rpm-pythonprov
BuildRequires:	rpm-utils
BuildRequires:	ruby
BuildRequires:	sed >= 4.0
BuildRequires:	which
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir	%{_libdir}/%{name}

%define		vg_home	/home/vagrant
%define		vg_root	/vagrant

# no Provides from private modules
%define		_noautoprovfiles	%{_appdir}
# do not require libs provided by this package
%define		_noautoreq		libffi.so.6 libcrypto.so.1.0.0 libruby.so.1.9 libssl.so.1.0.0 libutil.so.1 libyaml-0.so.2 libz.so.1

%define		no_install_post_check_so	1

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

# causes chrpath on th-i686  to fail
rm embedded/rgloader/rgloader*.freebsd*.so
%ifarch %{ix86}
rm embedded/rgloader/rgloader*.x86_64.so
%endif

%build
# update RPATH, not to contain insecure /tmp/vagrant-temp/embedded (insecure,
# because /tmp is world writable dir) for the rest, just substitute with sed
# (so shebangs would be correct)
grep -r '/tmp/vagrant-temp/embedded' . -l | xargs -r file -i | while read path mime; do
	path=${path%:}
	case "$mime" in
	text/*)
		sed -i -e 's,/tmp/vagrant-temp/embedded,%{_appdir}/embedded,' "$path"
	;;
	application/x-executable*|application/x-sharedlib*)
		rpath=$(chrpath -l $path) || continue
		rpath=${rpath#$path: RPATH=}
		[ "$rpath" ] || continue

		case "$rpath" in
		'${ORIGIN}/../lib:/tmp/vagrant-temp/embedded/lib' | \
		'/tmp/vagrant-temp/embedded/lib:${ORIGIN}/../lib')
			rpath=%{_appdir}/embedded/lib
			chrpath -r "$rpath" $path
		;;
		esac
	;;
	esac
done

%install
rm -rf $RPM_BUILD_ROOT
%if %{with vagrant}
install -d $RPM_BUILD_ROOT{%{_bindir},%{_appdir}}
cp -a bin embedded $RPM_BUILD_ROOT%{_appdir}
ln -s %{_appdir}/bin/%{name} $RPM_BUILD_ROOT%{_bindir}
%endif

cd $RPM_BUILD_ROOT%{_appdir}/embedded/gems/gems/vagrant-%{version}

install -d $RPM_BUILD_ROOT/etc/bash_completion.d
mv contrib/bash/completion.sh $RPM_BUILD_ROOT/etc/bash_completion.d/%{name}.sh

# guest
install -d $RPM_BUILD_ROOT{%{vg_root},%{vg_home}/.ssh}
cp -a /etc/skel/.bash*  $RPM_BUILD_ROOT%{vg_home}

# Since Vagrant only supports key-based authentication for SSH, we must
# set up the vagrant user to use key-based authentication. We can get the
# public key used by the Vagrant gem directly from its Github repository.
mv keys/vagrant.pub $RPM_BUILD_ROOT%{vg_home}/.ssh/authorized_keys

%clean
rm -rf $RPM_BUILD_ROOT

%pre guest
# FIXME: register user in uid_gid.db.txt
%groupadd -g 2000 vagrant
%useradd -u 2000 -g vagrant -G wheel -c "Vagrant user" -s /bin/bash -d %{vg_home} vagrant

%postun guest
if [ "$1" = "0" ]; then
	%userremove vagrant
	%groupremove vagrant
fi

%if %{with vagrant}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/vagrant

%defattr(-,root,root,-)
%{_appdir}
%endif

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
/etc/bash_completion.d/*

%files guest
%defattr(644,root,root,755)
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
