#! /bin/sh

echo '.. image:: http://img.shields.io/pypi/v/mscxyz.svg
    :target: https://pypi.python.org/pypi/mscxyz

.. image:: https://travis-ci.org/Josef-Friedrich/mscxyz.svg?branch=master
    :target: https://travis-ci.org/Josef-Friedrich/mscxyz' > README.rst
./bin/mscx-manager help --rst all >> README.rst
