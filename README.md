eos-node-modules
================
This creates two Debian packages containing modules for node.js:

- `eos-node-modules`, with modules required in every installation of EndlessOS (runtime dependencies)
- `eos-node-modules-dev`, with additional modules required for developing EndlessOS that will not be installed on users' systems.

The modules included are controlled by the `package.json` file. See [Nodejitsu](http://package.json.nodejitsu.com/) for a cheat sheet for the syntax of this file.

Adding a module
---------------
For the most part, this is as simple as adding the module to `dependencies` or `devDependencies` in `package.json.in`. Some extra steps are needed, though:
Go through the following checklist:

- add the module and its version to `dependencies` or `devDependencies` in `package.json.in` (see Note about Versions, below.)
- run `autogen.sh` followed by `make` and make sure the module is downloaded and compiled correctly.
- run `DESTDIR=staging make install` to test installing into a staging directory.
- in line 1 of `configure.ac`, increment the *minor* version of the `eos-node-modules` package. (For example, from 0.5.0 to 0.6.0.) Your package should now depend on `eos-node-modules (>= 0.6)` (or build-depend on `eos-node-modules-dev (>= 0.6)`.)
- add the module to the Module Index at the bottom of this readme file. Specify the name of your package. Maintain alphabetical order for others' convenience.
- add the usual `Version_x.y.z` to the `master` branch and `Version_x.y.z_debian` tags to the `debian-master` branch of this `eos-node-modules` git repo.

Removing a module
-----------------
Checklist:

- check the Module Index at the bottom of this readme file. Remove your package from that module's list of packages. If you were the *only* user of that module, then you may proceed to remove it.
- remove your module from `package.json.in`.
- in line 1 of `configure.ac`, increment the *major* version of the `eos-node-modules` package. (For example, from 0.5.0 to 1.0.0.)
- add the usual `Version_x.y.z` and `Version_x.y.z_debian` tags to the git repo.

Note about Versions
-------------------
Try to be somewhat flexible with the versions that you specify.
This allows us to possibly do some consolidation in the future.
For example, instead of `~0.4.1` (any version between 0.4.1 and 0.5), you might specify `^0.4` (any version between 0.4 and the next compatibility-breaking version.)

Note that instead of a version, you can specify that you want a particular branch from a particular Github repository (useful for requiring patches that haven't been incorporated upstream yet.)

Be careful when upgrading a module to a new major version.
All EndlessOS software using node.js uses the same set of node modules, so don't break other people's packages!
Definitely don't upgrade modules just because there is a new major version available.

Module index
------------
- **autoquit**: eos-license-service
- **express**: eos-license-service
- **jscs**: eos-dev-config (dev)
- **jshint**: eos-dev-config (dev)
- **lcov-result-merger**: eos-sdk (dev)
- **systemd**: eos-license-service
