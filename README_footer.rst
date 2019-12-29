

Configuration file
==================

``/etc/mscxyz.ini``

.. code-block:: ini

    [general]
    executable = /usr/bin/mscore3
    colorize = True

    [rename]
    format = '$combined_title ($combined_composer)'

Development
===========

Test
----

::

    tox


Publish a new version
---------------------

::

    git tag 1.1.1
    git push --tags
    python setup.py sdist upload


Package documentation
---------------------

The package documentation is hosted on
`readthedocs <http://mscxyz.readthedocs.io>`_.

Generate the package documentation:

::

    python setup.py build_sphinx
