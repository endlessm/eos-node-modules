all-local: npm.stamp

npm.stamp: package.json
	npm install
	npm dedupe
	touch $@

# Adding 'npm dedupe' after 'npm install' consolidates some dependencies, and
# the effect on the package's installed size is dramatic, about 1.5M.
#
# It comes at the cost of some complexity; when adding packages you have to
# check whether their dependencies get consolidated into the top level, and add
# appropriate install rules to the debian/*.install files, and add them to
# Conflicts: in debian/control.

CLEANFILES = sysmodules-cache.txt .ls-dedupe-cache
DISTCLEANFILES = npm.stamp
EXTRA_DIST = node-pkg-info.py ls-dedupe

# Use $(prefix)/lib/nodejs instead of $(libdir)/nodejs; nodejs will not look for
# modules in /usr/lib/i386-linux-gnu/nodejs, for example.

installdirs-local:
	$(INSTALL_DATA) -m 755 -d $(DESTDIR)$(prefix)/lib/nodejs;

install-data-local: installdirs
	export system_modules="`echo "@eos_node_system_modules@" | sed "s/ /\n/g"`"; \
	for module in node_modules/*; do \
		module_name=`basename $$module`; \
		module_regexp="^$$module_name$$"; \
		if ! echo "$$system_modules" | grep -q -G "$$module_regexp"; then \
			echo "Installing $$module_name..."; \
			cp -R $$module $(DESTDIR)$(prefix)/lib/nodejs; \
		else \
			echo "Skipping system module $$module_name..."; \
		fi \
	done

uninstall-local:
	export system_modules="`echo "@eos_node_system_modules@" | sed "s/ /\n/g"`"; \
	for module in node_modules/*; do \
		module_name=`basename $$module`; \
		module_regexp="^$$module_name$$"; \
		if ! echo "$$system_modules" | grep -q -G "$$module_regexp"; then \
			echo "Uninstalling $$module_name..."; \
			rm -rf $(DESTDIR)$(prefix)/lib/nodejs/$$module_name; \
		fi \
	done

distclean-local:
	rm -rf node_modules
