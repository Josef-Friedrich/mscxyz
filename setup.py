import versioneer
import os
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return open(file_path, encoding='utf8').read()


setup(
    name='mscxyz',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Josef Friedrich',
    author_email='josef@friedrich.rocks',
    description=(
        'A command line tool to manipulate the XML based *.mscX and \
        *.mscZ files of the notation software MuseScore.'),
    license='MIT',
    packages=['mscxyz'],
    keywords='audio',
    url='https://github.com/Josef-Friedrich/mscxyz',
    install_requires=[
        'lxml', 'termcolor', 'tmep>=1.1.2'
    ],
    tests_require=['mock'],
    scripts=['bin/mscx-manager'],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False,
    python_requires='>=3.6',
)
