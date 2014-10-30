#!/usr/bin/env python

import subprocess
import sys
import argparse
import json
import os

_SYSPACKAGES = ['npm']

parser = argparse.ArgumentParser()
parser.add_argument('package_manifest_path', type=str, nargs='?',
                    help='path to the package.json file')
parser.add_argument('-i', '--intersect',
                    help='print the intersection of system modules and package.json modules',
                    action='store_true')
parser.add_argument('-d', '--diff',
                    help='print the set difference of (DEDUPED NODE MODULES) - (SYSTEM MODULES)',
                    choices=['prod', 'dev'], type=str, dest='diff_type')
parser.add_argument('-f', '--format',
                    help='how to format the module names',
                    choices=['deb', 'node', 'install'], type=str,
                    default='node', dest='fmt')


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
    """Return a set of all the node.js modules that are dependencies of node.js
    utilities that need to be installed on the system."""
    system_modules = _analyze_dependencies(_SYSPACKAGES)

    return system_modules

def package_manifest_modules(pkg_json_path):
    with open(pkg_json_path) as json_file:
        # load the package.json file
        node_pkg_data = json.load(json_file)
        if 'dependencies' in node_pkg_data:
            node_deps = node_pkg_data['dependencies'].keys()
            pkg_deps = ['node-' + module for module in node_deps]
        if 'devDependencies' in node_pkg_data:
            node_dev_deps = node_pkg_data['devDependencies'].keys()
            pkg_dev_deps = ['node-' + module for module in node_dev_deps]

    return pkg_deps, pkg_dev_deps

def toplevel_deduped_modules(pkg_json_path):
    # get the output of calling ls-dedupe, which is all node modules installed
    # after calling "node install && node dedupe"
    buf = subprocess.check_output(['./ls-dedupe'])

    # get an array of these modules, prepended with 'node-'
    nonempty = lambda name: name != ''
    all_modules = ['node-' + module for module in filter(nonempty, buf.split('\n'))]

    # get the set of modules in the manifest (i.e. contents of package.json)
    prod_pkgs, dev_pkgs = package_manifest_modules(pkg_json_path)
    all_manifest_modules = set(prod_pkgs) | set(dev_pkgs)

    # the set of modules which exist only because of deduping is:
    # (contents of node_modules after deduping) - (modules listed in manifest)
    deduped_only = set(all_modules) - all_manifest_modules
    return deduped_only

def main(action, fmt, pkg_json_path):
    if action == 'intersect':
        sysdeps = system_node_modules()
        prod_pkgs, dev_pkgs = package_manifest_modules(pkg_json_path)
        deduped_only = toplevel_deduped_modules(pkg_json_path)

        to_be_installed = set(prod_pkgs) | set(dev_pkgs) | set(deduped_only)

        pkg_names = to_be_installed & sysdeps
    elif action == 'sysmodules':
        pkg_names = system_node_modules()
    elif action == 'dev' or action == 'prod':
        prod_pkgs, dev_pkgs = package_manifest_modules(pkg_json_path)
        node_pkgs = prod_pkgs if action == 'prod' else dev_pkgs
        sys_pkgs = system_node_modules()

        if action == 'prod':
            node_pkgs = set(node_pkgs) | set(toplevel_deduped_modules(pkg_json_path))

        pkg_names = set(node_pkgs) - set(sys_pkgs)

    if fmt == 'node':
        # strip the 'node-' prefix from the package names
        pkg_names = [pkg[len('node-'):] for pkg in pkg_names]
        print ' '.join(pkg_names)
    elif fmt == 'deb':
        print ', '.join(map(lambda name: name.replace('_', '-'), pkg_names))
    elif fmt == 'install':
        install_prefix = 'usr/lib/nodejs'
        pkg_names = [pkg[len('node-'):] for pkg in pkg_names]
        pkg_paths = [os.path.join(install_prefix, pkg) for pkg in pkg_names]
        print '\n'.join(pkg_paths)

if __name__ == '__main__':
    args = parser.parse_args()
    if args.package_manifest_path and not os.path.isfile(args.package_manifest_path):
        print 'Nonexistent package.json at package_manifest_path: %s' % args.package_manifest_path
        sys.exit(1)

    if args.intersect:
        main('intersect', args.fmt, args.package_manifest_path)
    elif args.diff_type:
        main(args.diff_type, args.fmt, args.package_manifest_path)
    else:
        main('sysmodules', args.fmt, args.package_manifest_path)
