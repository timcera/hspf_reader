.. image:: https://github.com/timcera/hspf_reader/actions/workflows/python-package.yml/badge.svg
    :alt: Tests
    :target: https://github.com/timcera/hspf_reader/actions/workflows/python-package.yml
    :height: 20

.. image:: https://img.shields.io/coveralls/github/timcera/hspf_reader
    :alt: Test Coverage
    :target: https://coveralls.io/r/timcera/hspf_reader?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/hspf_reader.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/hspf_reader/
    :height: 20

.. image:: http://img.shields.io/pypi/l/hspf_reader.svg
    :alt: BSD-3 clause license
    :target: https://pypi.python.org/pypi/hspf_reader/
    :height: 20

.. image:: http://img.shields.io/pypi/dd/hspf_reader.svg
    :alt: hspf_reader downloads
    :target: https://pypi.python.org/pypi/hspf_reader/
    :height: 20

.. image:: https://img.shields.io/pypi/pyversions/hspf_reader
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/hspf_reader/
    :height: 20

hspf_reader - Quick Guide
=========================
The hspf_reader is a pure Python module and command line script to read HSPF
time-series from WDM files, HSPF binary files, and HSPF plotgen files.

Use "wdmtoolbox" to create, examine, read, and write to WDM files.

Use "hspfbintoolbox" to catalog and read HSPF binary output files.

Installation
------------
Should be as easy as running ``pip install hspf_reader`` at any command line.

Usage - Command Line
--------------------
Just run 'hspf_reader --help' to get a list of subcommands::


    usage: hspf_reader [-h]
                     {wdm, hbn, plotgen, about} ...

    positional arguments:
      {wdm, hbn, plotgen, about}

    wdm
        Read HSPF WDM files.
    hbn
        Read HSPF binary files.
    plotgen
        Read HSPF plotgen files.
    about
        Display version number and system information.

    optional arguments:
      -h, --help            show this help message and exit

The output time-series data is printed to the screen and you can then redirect
to a file.

Usage - API
-----------
You can use all of the command line subcommands as functions.  The function
signature is identical to the command line subcommands.  The return is always
a PANDAS DataFrame.

Simply import hspf_reader::

    from hspf_reader import hspf_reader

    # Then you could call the functions
    ntsd = hspf_reader.wdm('wdm_file.wdm', 202)

    # Once you have a PANDAS DataFrame you can use that as input to other
    # hspf_reader functions.
    ntsd = hspf_reader.hbn('hbn_file.hbn', "yearly", [,,,"TAET"])
