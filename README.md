# Qubit Modeling Tools (QMT)
[![Build Status](https://travis-ci.com/Microsoft/qmt.svg?token=ukrJZxPf4mQFHvy1yJ9t&branch=master)](https://travis-ci.com/Microsoft/qmt)

Welcome to our qubit modeling tools (qmt)! This package is designed to automate
the setup of complex geometries appropriate to physical qubit simulations. This 
package is licensed with an MIT open source license.

To set up your python environment, see the environment.yml file. If you are 
running Anaconda, simply run

    conda env create -f environment.yml

A significant part of the repository consists of Python functions and macros to
be executed within FreeCAD, either interactively or in batch mode. These
require the latest stable version of FreeCAD (0.16). Currently, FreeCAD only
supports Python 2.7. So while the non-FreeCAD sections of the code are designed
to work with either Python 3.6 or Python 2.7, the FreeCAD module will only run
with 2.7.

Note that this initial release does not contain examples or introductory 
documentation, which we plan to add in time. If you want to get started, feel 
free to email John Gamble at john.gamble@microsoft.com.


# Development notes

We are using GitHub Flow for the development of this code. Please see
[here](https://guides.github.com/introduction/flow/)
for a tutorial.


# Contributing

This project welcomes contributions and suggestions, but please coordinate with
the maintainers before setting out to implement significant changes or new
features. Most contributions require you to agree to a Contributor License
Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit
https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only need
to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any
additional questions or comments.
