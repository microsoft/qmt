# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from setuptools import setup, find_packages

setup(name='qmt',
      version='1.0',
      description='Qubit Modeling Tools (QMT) for computational modeling of quantum devices',
      url='https://github.com/Microsoft/qmt',
      author='Andrey Antipov, John Gamble, Jan Gukelberger, Donjan Rodic, Kevin van Hoogdalem, Georg Winkler',
      author_email='john.gamble@microsoft.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
