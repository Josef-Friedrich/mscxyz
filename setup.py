import os

from setuptools import setup, find_packages
import versioneer


def read(file_name):
    """
    Read the contents of a text file and return its content.

    :param str file_name: The name of the file to read.

    :return: The content of the text file.
    :rtype: str
    """
    return open(
        os.path.join(os.path.dirname(__file__), file_name),
        encoding='utf-8'
    ).read()


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
    packages=find_packages(),
    keywords='audio',
    url='https://github.com/Josef-Friedrich/mscxyz',
    install_requires=[
        'lxml', 'termcolor', 'tmep>=2.0.1'
    ],
    tests_require=['mock'],
    scripts=['bin/mscx-manager'],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False,
    python_requires='>=3.6',
)
