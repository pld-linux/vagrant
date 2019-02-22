#!/bin/sh
#
# This is a wrapper to properly execute Vagrant so that it sees system gems and
# merges with it's own gems.
#
# This sets up proper environmental variables so that everything loads and
# compiles to proper directories.

# Set the path to the Ruby executable
RUBY_EXECUTABLE="/usr/bin/ruby"

GEM_PATH=$($RUBY_EXECUTABLE -r rubygems -e 'puts Gem.respond_to?(:default_dirs) ? Gem.default_dirs[:system][:gem_dir] : Gem.path.first')
export GEM_PATH

# Export gem paths so it can find vagrant own gem
export GEM_HOME="${GEM_PATH}"

# Unset any RUBYOPT and RUBYLIB, we don't want these bleeding into our
# runtime.
unset RUBYOPT
unset RUBYLIB

# Find the Vagrant executable
for needle in "${GEM_PATH}/gems/vagrant-"*; do
	if [ -f "${needle}/lib/vagrant/version.rb" ]; then
		VAGRANT_GEM_PATH="${needle}"
	fi
done

VAGRANT_EXECUTABLE="${VAGRANT_GEM_PATH}/bin/vagrant"

# Call the actual Vagrant bin with our arguments
exec "$RUBY_EXECUTABLE" -r rubygems "$VAGRANT_EXECUTABLE" "$@"
