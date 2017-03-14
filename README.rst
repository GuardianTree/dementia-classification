Subtype Identification
--------------

Before doing anything (like running tests or the actual program)
you need to build the container:

.. code-block:: shell

    make


**Before running any of the following commands you need to build the container first**


Run the tracking:

.. code-block:: shell

    make run


Running tests requires a TTY(hint: you have one, the gitlab-ci server does not):

.. code-block:: shell

    make test


To run the test without a TTY(as for example on the gitlab-ci server):

.. code-block:: shell

    make test_server


Run the code quality control tools:

.. code-block:: shell

    make quality

