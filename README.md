# Qubit Modeling Tools (QMT)
[![Build Status](https://dev.azure.com/ms-qmt/qmt/_apis/build/status/QMT%20Master%20Build%20and%20Push)](https://dev.azure.com/ms-qmt/qmt/_build/latest?definitionId=4)

Welcome to our qubit modeling tools (qmt)! This package is designed to automate
the setup of complex geometries appropriate to physical qubit simulations. This 
package is licensed with an MIT open source license.

 For python package configuration, see the yml files in qmt/deployment. Note that qmt uses python 
 3.6, but to perform computational lithography you will also need the python 2.7 environment:

    conda env create -f qmt/deployment/environment_27.yml
    conda env create -f qmt/deployment/environment_36.yml    

Another option is to run the using Docker. To use the latest 
image, see qmt/deployment/docker_python.sh. 

A significant part of the repository consists of Python functions and macros to
be executed within FreeCAD, either interactively or in batch mode. These
require the latest stable version of FreeCAD (0.17). Currently, FreeCAD only
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
