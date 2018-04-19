.. image:: http://img.shields.io/pypi/v/mscxyz.svg
    :target: https://pypi.python.org/pypi/mscxyz

.. image:: https://travis-ci.org/Josef-Friedrich/mscxyz.svg?branch=master
    :target: https://travis-ci.org/Josef-Friedrich/mscxyz

======
mscxyz
======

Manipulate the XML based mscx files of the notation software MuseScore.

Installation
============

From Github
-----------

.. code:: Shell

    git clone git@github.com:Josef-Friedrich/mscxyz.git
    cd mscxyz
    python setup.py install

From PyPI
---------

.. code:: Shell

    pip install mscxyz
    easy_install mscxyz

Usage
=====


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
