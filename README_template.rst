.. image:: http://img.shields.io/pypi/v/mscxyz.svg
    :target: https://pypi.python.org/pypi/mscxyz
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/mscxyz/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/mscxyz/actions/workflows/tests.yml
    :alt: Tests

.. image:: https://readthedocs.org/projects/mscxyz/badge/?version=latest
    :target: https://mscxyz.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

======
mscxyz
======

Manipulate the XML based mscx files of the notation software MuseScore.

Installation
============

From Github
-----------

.. code:: Shell

    git clone https://github.com/Josef-Friedrich/mscxyz.git
    cd mscxyz
    python setup.py install

From PyPI
---------

.. code:: Shell

    pip install mscxyz
    easy_install mscxyz

Usage
=====

{{ cli('mscx-manager help --rst all') }}

API Usage
=========

``MscoreMetaInterface``
------------------------

.. code-block:: Python

    from mscxyz import MscoreMetaInterface
    score = MscoreMetaInterface('score.mscx')
    score.metatag.composer = 'Mozart'
    score.save()

``MscoreStyleInterface``
------------------------

Change all font faces (MuseScore3 only)

.. code-block:: Python

    from mscxyz import MscoreStyleInterface
    score = MscoreStyleInterface('score.mscx')
    for element in score.style:
        if 'FontFace' in element.tag:
            element.text = 'Alegreya'
    score.save()

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
