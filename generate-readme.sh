#! /bin/sh

cat README_header.rst > README.rst
echo >> README.rst
./bin/mscx-manager help --rst all >> README.rst
echo >> README.rst
cat README_footer.rst >> README.rst
