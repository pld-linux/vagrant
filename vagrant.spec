
#
# Missing deps in Fedora:
#
# rubygem-log4r >= 1.1.9 < 2.0.0
#   Fix: Build new package, bz905240
#
# rubygem-childprocess >=0.3.1 < 0.4.0 (0.3.6 in rawhide)
#   Fix: Grab 0.3.6 package from rawhide
#
# rubygem-json >= 1.5.1, < 1.6.0 (1.6.5 in f18, 1.9.1 in rawhide)
#   Fix: Build rubygem-json15, roughly based on current package
#
# rubygem-net-ssh >= 2.2.2 < 2.3.0 (2.2.1 in rawhide)
#   Fix: Build 2.2.2 package based on current package
#

%define	gem_name	vagrant
%define	rubyabi		1.9.1
Summary:	Provisioning and deployment of virtual instances
Name:		vagrant
Version:	1.0.6
Release:	0.1
License:	MIT
Group:		Applications/Emulators
URL:		http://vagrantup.com/
Source0:	http://rubygems.org/downloads/%{gem_name}-%{version}.gem
# Source0-md5:	c84c240a9e62853336bd3f0f2532ad8a
BuildRequires:	git-core
BuildRequires:	ruby(abi) = %{rubyabi}
#BuildRequires:	rubygem(contest) >= 0.1.2
BuildRequires:	rubygem(minitest) >= 2.5.1
BuildRequires:	rubygem(mocha)
BuildRequires:	rubygem(rake)
BuildRequires:	rubygem(rspec-core) >= 2.8.0
BuildRequires:	rubygem(rspec-expectations) >= 2.8.0
BuildRequires:	rubygem(rspec-mocks) >= 2.8.0
BuildRequires:	rubygems-devel
Requires:	ruby(abi) = %{rubyabi}
Requires:	ruby(rubygems)
Requires:	rubygem(archive-tar-minitar) = 0.5.2
Requires:	rubygem(childprocess) >= 0.3.1
Requires:	rubygem(erubis) >= 2.7.0
Requires:	rubygem(i18n) >= 0.6.0
Requires:	rubygem(log4r) >= 1.1.9
Requires:	rubygem(net-scp) >= 1.0.4
Requires:	rubygem(net-ssh) >= 2.2.2
Requires:	rubygem-json15
BuildArch:	noarch

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
gem unpack %{SOURCE0}
%setup -q -D -T -n %{gem_name}-%{version}

gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec

%build
mkdir -p ./%{gem_dir}

# Create the gem as gem install only works on a gem file
gem build %{gem_name}.gemspec

export CONFIGURE_ARGS="--with-cflags='%{rpmcflags}'"
# gem install compiles any C extensions and installs into a directory
# We set that to be a local directory so that we can move it into the
# buildroot in %%install
gem install -V \
		--local \
		--install-dir ./%{gem_dir} \
		--bindir ./%{_bindir} \
		--force \
		--rdoc \
		%{SOURCE0}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{gem_dir}

# Remove a few oddments
rm .%{gem_instdir}/.gitignore
rm .%{gem_instdir}/.yardopts

# Just copy these out for putting in default fedora doc location later
cp .%{gem_instdir}/LICENSE .
cp .%{gem_instdir}/README.md .
cp .%{gem_instdir}/CHANGELOG.md .

# Programs/scripts
install -d $RPM_BUILD_ROOT%{_bindir}
mv -v ./bin/* $RPM_BUILD_ROOT%{_bindir}
mv -v .%{gem_instdir}/bin/* $RPM_BUILD_ROOT%{_bindir}
chmod +x .%{gem_instdir}/test/*/scripts/*.sh

# Wrap up the rest
cp -a ./%{gem_dir}/* $RPM_BUILD_ROOT%{gem_dir}/

%if %{with tests}
cd .%{gem_instdir}

# Just a hack, rspec misses this .gitignore(!)
touch $RPM_BUILD_ROOT%{gem_instdir}/.gitignore
rspec $RPM_BUILD_ROOT%{gem_instdir}/%{gem_name}.gemspec
rm $RPM_BUILD_ROOT%{gem_instdir}/.gitignore
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/vagrant
%{gem_spec}
%{gem_cache}
%{gem_instdir}/lib
%{gem_instdir}/test
%{gem_instdir}/keys
%{gem_instdir}/tasks
%{gem_instdir}/contrib
%{gem_instdir}/Gemfile
%{gem_instdir}/Rakefile
%{gem_instdir}/%{gem_name}.gemspec
%config %{gem_instdir}/config

# Put something in the default fedora documentation location
%doc LICENSE
%doc README.md
%doc CHANGELOG.md

# Ruby devs probably panic if these are not in place here as well
%doc %{gem_instdir}/LICENSE
%doc %{gem_instdir}/README.md
%doc %{gem_instdir}/CHANGELOG.md

%doc %{gem_instdir}/templates

%files doc
%defattr(644,root,root,755)
%doc %{gem_docdir}
