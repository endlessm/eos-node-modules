#!/usr/bin/env python

import subprocess
import sys
import argparse
import json
import os

_SYSPACKAGES = ['npm']

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--intersect',
                    help='path to package.json file requiring intersection',
                    type=str, dest='path')
parser.add_argument('-f', '--format',
                    help='how to format the module names. Either debian or node',
                    type=str, default='node', dest='fmt')


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


def system_node_modules(pkg_json_path):
    """Return a set of all the node.js modules that are dependencies of node.js
    utilities that need to be installed on the system. If a pkg_json_path is
    specified, it will instead return the modules that pkg_json_path has in
    common with the system"""
    system_modules = _analyze_dependencies(_SYSPACKAGES)

    if pkg_json_path is not None:
        with open(pkg_json_path) as json_file:
            # load the package.json file
            node_pkg_data = json.load(json_file)
            all_deps = set()

            # for dependencies and devDependencies, collect the module names
            # and convert them into package names (by prepending 'node-')
            if 'dependencies' in node_pkg_data:
                node_deps = node_pkg_data['dependencies'].keys()
                pkg_deps = ['node-' + module for module in node_deps]
                all_deps |= set(pkg_deps)
            if 'devDependencies' in node_pkg_data:
                node_dev_deps = node_pkg_data['devDependencies'].keys()
                pkg_dev_deps = ['node-' + module for module in node_dev_deps]
                all_deps |= set(pkg_dev_deps)

            # return the debian package names for all shared node modules in
            # package.json and existing system modules
            return all_deps & system_modules
    return system_modules


def main(fmt, pkg_json_path):
    pkg_names = system_node_modules(pkg_json_path)

    if fmt == 'node':
        # strip the 'node-' prefix from the package names
        pkg_names = [pkg[len('node-'):] for pkg in pkg_names]
        print ' '.join(pkg_names)
    elif fmt == 'deb':
        print ', '.join(pkg_names)

if __name__ == '__main__':
    args = parser.parse_args()
    if args.fmt not in ('node', 'deb'):
        print 'Invalid format: %s' % str(args.fmt)
        sys.exit(1)
    if args.path and not os.path.isfile(args.path):
        print 'Nonexistent package.json at path: %s' % args.path
        sys.exit(1)
    main(args.fmt, args.path)
