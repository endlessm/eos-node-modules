all-local: npm.stamp

npm.stamp: package.json
	npm install
	npm dedupe
	touch $@

# Adding 'npm dedupe' after 'npm install' consolidates some dependencies, and
# brings the XZ dist tarball size down by about 100k; the effect on the
# package's installed size is more dramatic, about 1.5M.
#
# It comes at the cost of some complexity; when adding packages you have to
# check whether their dependencies get consolidated into the top level, and add
# appropriate install rules to the debian/*.install files, and add them to
# Conflicts: in debian/control.

CLEANFILES = npm.stamp sysmodules-cache.txt
EXTRA_DIST = npm.stamp sysmodules.py node_modules

# Use $(prefix)/lib/nodejs instead of $(libdir)/nodejs; nodejs will not look for
# modules in /usr/lib/i386-linux-gnu/nodejs, for example.

installdirs-local:
	$(INSTALL_DATA) -d $(DESTDIR)$(prefix)/lib/nodejs;

install-data-local: installdirs
	export system_modules="@eos_node_system_modules@"; \
	for module in node_modules/*; do \
		module_name=`basename $$module`; \
		if [ "$${system_modules/$$module_name}" = "$$system_modules" ]; then \
			echo "Installing $$module_name..."; \
			cp -R $$module $(DESTDIR)$(prefix)/lib/nodejs; \
		else \
			echo "Skipping system module $$module_name..."; \
		fi \
	done