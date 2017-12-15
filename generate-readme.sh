#! /bin/sh

cat README_header.rst > README.rst
echo >> README.rst
./bin/mscx-manager help --rst all >> README.rst
echo >> README.rst
cat README_footer.rst >> README.rst


echo 'Comande line interface
======================

' > doc/source/cli.rst

./bin/mscx-manager help --rst all >> doc/source/cli.rst
