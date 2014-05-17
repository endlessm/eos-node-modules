#!/usr/bin/env python

import subprocess

_SYSPACKAGES = ['npm']


def _node_module_dependencies(package):
    """Get all the dependencies for @package that appear to be node modules
    (start with 'node-'.)"""
    buf = subprocess.check_output(['apt-cache', 'depends', package])
    lines = buf.split('\n')
    deps = [line[len('  Depends: '):] for line in lines if line.startswith('  Depends: ')]
    deps = [dep for dep in deps if dep.startswith('node-')]
    return set(deps)


def _analyze_dependencies_recursive(package, sysmodules):
    """Recursing function used to implement _analyze_dependencies()."""
    deps = _node_module_dependencies(package)
    sysmodules |= deps
    for dep in sysmodules & deps:
        sysmodules |= _analyze_dependencies_recursive(dep, sysmodules)
    return sysmodules


def _analyze_dependencies(packages):
    """Return a set of all the node module dependencies for @packages."""
    sysmodules = set()
    for package in packages:
        sysmodules |= _analyze_dependencies_recursive(package, sysmodules)
    return sysmodules


def system_node_modules():
    """Return a list of all the node.js modules (without the 'node-' prefix)
    that are dependencies of node.js utilities that need to be installed on the
    system. Currently the only such utility is npm."""
    return [module[len('node-'):] for module in _analyze_dependencies(_SYSPACKAGES)]

print ' '.join(system_node_modules())
