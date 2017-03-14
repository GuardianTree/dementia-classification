project-skeleton
================

This project skeleton provides the starting point for your student project.

Clone the repository, go to the repo root directory and find + replace all appearances
of "AUTHOR" and "project_name".

Additionally, you have to modify the setup.py file according to your wishes.

The main components of this skeleton are the test and quality checks.

In order to run the tests:

.. code-block:: shell

    make && make test

Run the code quality checks:

.. code-block:: shell

    make && make quality
    
Alternatively, you can run tests and quality checks from the repo root without docker:

.. code-block:: shell
    
    python -m unittest

    flake8 project_name
    pylint project_name
    
However, this assumes you have everything installed locally (e.g. flake8 & pylint).

Remarks for admin
----------------

In order to set up a new student project, fork the project to the ise-squad namespace.

There change the project name and path for the new project.

Make sure the ise-squad-runner is enabled.