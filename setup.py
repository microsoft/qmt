#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from setuptools import setup
import sys


if sys.version_info < (3, 6):
    print("qmt requires Python 3.6 or above.")
    sys.exit(1)


# Loads _version.py module without importing the whole package.
def get_version_and_cmdclass(package_name):
    import os
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("version", os.path.join(package_name, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.cmdclass


version, cmdclass = get_version_and_cmdclass("qmt")

setup(
    name="qmt",
    version=version,
    python_requires=">=3.6",
    cmdclass=cmdclass,
    description="Qubit Modeling Tools (QMT) for computational modeling of quantum devices",
    url="https://github.com/Microsoft/qmt",
    author="Andrey Antipov, John Gamble, Jan Gukelberger, Donjan Rodic, Kevin van Hoogdalem, Georg Winkler",
    author_email="john.gamble@microsoft.com",
    license="MIT",
    # install_requires=requirements, packages=find_packages(),
    zip_safe=False,
)
