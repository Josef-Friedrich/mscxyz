.. image:: http://img.shields.io/pypi/v/mscxyz.svg
    :target: https://pypi.python.org/pypi/mscxyz
    :alt: This package on the Python Package Index

.. image:: https://travis-ci.org/Josef-Friedrich/mscxyz.svg?branch=master
    :target: https://travis-ci.org/Josef-Friedrich/mscxyz
    :alt: Continuous integration

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


mscxyz
======

.. code-block:: text

  usage: mscx-manager [-h] [-V] [-b] [-c] [-d] [-g GENERAL_GLOB] [-m] [-v]
                      {clean,meta,lyrics,rename,export,help} ... path
  
  A command line tool to manipulate the XML based "*.mscX" and "*.mscZ" files of
  the notation software MuseScore.
  
  positional arguments:
    path                  Path to a "*.mscx" file or a folder which contains
                          "*.mscx" files. In conjunction with the subcommand
                          "help" this positional parameter accepts the names of
                          all other subcommands or the word "all".
  
  optional arguments:
    -h, --help            show this help message and exit
    -V, --version         show program's version number and exit
    -b, --backup          Create a backup file.
    -c, --colorize        Colorize the command line print statements.
    -d, --dry-run         Simulate the actions.
    -g GENERAL_GLOB, --glob GENERAL_GLOB
                          Handle only files which matches against Unix style
                          glob patterns (e. g. "*.mscx", "* - *"). If you omit
                          this option, the standard glob pattern "*.mscx" is
                          used.
    -m, --mscore          Open and save the XML file in MuseScore after
                          manipulating the XML with lxml to avoid differences in
                          the XML structure.
    -v, --verbose         Make commands more verbose. You can specifiy multiple
                          arguments (. g.: -vvv) to make the command more
                          verbose.
  
  Subcommands:
    {clean,meta,lyrics,rename,export,help}
                          Run "subcommand --help" for more informations.
      clean               Clean and reset the formating of the "*.mscx" file
      meta                Deal with meta data informations stored in the
                          MuseScore file.
      lyrics              Extract lyrics. Without any option this subcommand
                          extracts all lyrics verses into separate mscx files.
                          This generated mscx files contain only one verse. The
                          old verse number is appended to the file name, e. g.:
                          score_1.mscx.
      rename              Rename the "*.mscx" files.
      export              Export the scores to PDFs or to the specified
                          extension.
      help                Show help. Use “mscx-manager help all” to show help
                          messages of all subcommands. Use “mscx-manager help
                          <subcommand>” to show only help messages for the given
                          subcommand.
  

Subcommands
===========


mscx-manager clean
------------------

.. code-block:: text

  usage: mscx-manager clean [-h] [-s CLEAN_STYLE]
  
  optional arguments:
    -h, --help            show this help message and exit
    -s CLEAN_STYLE, --style CLEAN_STYLE
                          Load a "*.mss" style file and include the contents of
                          this file.
  

mscx-manager meta
-----------------

.. code-block:: text

  usage: mscx-manager meta [-h] [-c META_CLEAN] [-D]
                           [-d SOURCE_FIELDS FORMAT_STRING] [-j]
                           [-l DESTINATION FORMAT_STRING] [-s]
                           [-S DESTINATION_FIELD FORMAT_STRING]
  
  MuseScore can store meta data informations in different places:
  
  # metatag
  
  ## XML structure of a meta tag:
  
      <metaTag name="tag"></metaTag>
  
  ## All meta tags:
  
      - arranger
      - composer
      - copyright
      - creationDate
      - lyricist
      - movementNumber
      - movementTitle
      - platform
      - poet
      - source
      - translator
      - workNumber
      - workTitle
  
  # vbox
  
  ## XML structure of a vbox tag:
  
      <VBox>
        <Text>
          <style>Title</style>
          <text>Some title text</text>
          </Text>
  
  ## All vbox tags:
  
      - Title
      - Subtitle
      - Composer
      - Lyricist
  
  This command line tool bundles some meta data informations:
  
  # Combined meta data fields:
  
      - title (1. vbox_title 2. metatag_work_title)
      - subtitle (1. vbox_subtitle 2. metatag_movement_title)
      - composer (1. vbox_composer 2. metatag_composer)
      - lyricist (1. vbox_lyricist 2. metatag_lyricist)
  
  You have access to all this metadata fields through following fields:
  
      - combined_composer
      - combined_lyricist
      - combined_subtitle
      - combined_title
      - metatag_arranger
      - metatag_composer
      - metatag_copyright
      - metatag_creation_date
      - metatag_lyricist
      - metatag_movement_number
      - metatag_movement_title
      - metatag_platform
      - metatag_poet
      - metatag_source
      - metatag_translator
      - metatag_work_number
      - metatag_work_title
      - vbox_composer
      - vbox_lyricist
      - vbox_subtitle
      - vbox_title
  
  optional arguments:
    -h, --help            show this help message and exit
    -c META_CLEAN, --clean META_CLEAN
                          Clean the meta data fields. Possible values: „all“ or
                          „field_one,field_two“.
    -D, --delete-duplicates
                          Deletes combined_lyricist if this field is equal to
                          combined_composer. Deletes combined_subtitle if this
                          field is equal tocombined_title. Move
                          combined_subtitle to combimed_title if combined_title
                          is empty.
    -d SOURCE_FIELDS FORMAT_STRING, --distribute-fields SOURCE_FIELDS FORMAT_STRING
                          Distribute source fields to target fields applying a
                          format string on the source fields. It is possible to
                          apply multiple --distribute-fields options.
                          SOURCE_FIELDS can be a single field or a comma
                          separated list of fields: field_one,field_two. The
                          program tries first to match the FORMAT_STRING on the
                          first source field. If this fails, it tries the second
                          source field ... an so on.
    -j, --json            Additionally write the meta data to a json file.
    -l DESTINATION FORMAT_STRING, --log DESTINATION FORMAT_STRING
                          Write one line per file to a text file. e. g. --log
                          /tmp/mscx-manager.log '$title $composer'
    -s, --synchronize     Synchronize the values of the first vertical frame
                          (vbox) (title, subtitle, composer, lyricist) with the
                          corresponding metadata fields
    -S DESTINATION_FIELD FORMAT_STRING, --set-field DESTINATION_FIELD FORMAT_STRING
                          Set value to meta data fields.
  

mscx-manager lyrics
-------------------

.. code-block:: text

  usage: mscx-manager lyrics [-h] [-e LYRICS_EXTRACT] [-r LYRICS_REMAP] [-f]
  
  optional arguments:
    -h, --help            show this help message and exit
    -e LYRICS_EXTRACT, --extract LYRICS_EXTRACT
                          The lyric verse number to extract or "all".
    -r LYRICS_REMAP, --remap LYRICS_REMAP
                          Remap lyrics. Example: "--remap 3:2,5:3". This example
                          remaps lyrics verse 3 to verse 2 and verse 5 to 3. Use
                          commas to specify multiple remap pairs. One remap pair
                          is separated by a colon in this form: "old:new": "old"
                          stands for the old verse number. "new" stands for the
                          new verse number.
    -f, --fix             Fix lyrics: Convert trailing hyphens ("la- la- la") to
                          a correct hyphenation ("la - la - la")
  

mscx-manager rename
-------------------

.. code-block:: text

  usage: mscx-manager rename [-h] [-f RENAME_FORMAT] [-A] [-a] [-n] [-s FIELDS]
                             [-t RENAME_TARGET]
  
  Fields and functions you can use in the format string (-f, --format):
  
  Fields
  ======
  
      - combined_composer
      - combined_lyricist
      - combined_subtitle
      - combined_title
      - metatag_arranger
      - metatag_composer
      - metatag_copyright
      - metatag_creation_date
      - metatag_lyricist
      - metatag_movement_number
      - metatag_movement_title
      - metatag_platform
      - metatag_poet
      - metatag_source
      - metatag_translator
      - metatag_work_number
      - metatag_work_title
      - readonly_abspath
      - readonly_basename
      - readonly_dirname
      - readonly_extension
      - readonly_filename
      - readonly_relpath
      - readonly_relpath_backup
      - vbox_composer
      - vbox_lyricist
      - vbox_subtitle
      - vbox_title
  
  Functions
  =========
  
      alpha
      -----
  
      %alpha{text}
          This function first ASCIIfies the given text, then all non alphabet
          characters are replaced with whitespaces.
  
      alphanum
      --------
  
      %alphanum{text}
          This function first ASCIIfies the given text, then all non alpanumeric
          characters are replaced with whitespaces.
  
      asciify
      -------
  
      %asciify{text}
          Translate non-ASCII characters to their ASCII equivalents. For
          example, “café” becomes “cafe”. Uses the mapping provided by the
          unidecode module.
  
      delchars
      --------
  
      %delchars{text,chars}
          Delete every single character of “chars“ in “text”.
  
      deldupchars
      -----------
  
      %deldupchars{text,chars}
          Search for duplicate characters and replace with only one occurrance
          of this characters.
  
      first
      -----
  
      %first{text} or %first{text,count,skip} or
      %first{text,count,skip,sep,join}
          Returns the first item, separated by ; . You can use
          %first{text,count,skip}, where count is the number of items (default
          1) and skip is number to skip (default 0). You can also use
          %first{text,count,skip,sep,join} where sep is the separator, like ; or
          / and join is the text to concatenate the items.
  
      if
      --
  
      %if{condition,truetext} or %if{condition,truetext,falsetext}
          If condition is nonempty (or nonzero, if it’s a number), then returns
          the second argument. Otherwise, returns the third argument if
          specified (or nothing if falsetext is left off).
  
      ifdef
      -----
  
      %ifdef{field}, %ifdef{field,text} or %ifdef{field,text,falsetext}
          If field exists, then return truetext or field (default). Otherwise,
          returns falsetext. The field should be entered without $.
  
      ifdefempty
      ----------
  
      %ifdefempty{field,text} or %ifdefempty{field,text,falsetext}
          If field exists and is empty, then return truetext. Otherwise, returns
          falsetext. The field should be entered without $.
  
      ifdefnotempty
      -------------
  
      %ifdefnotempty{field,text} or %ifdefnotempty{field,text,falsetext}
          If field is not empty, then return truetext. Otherwise, returns
          falsetext. The field should be entered without $.
  
      initial
      -------
  
      %initial{text}
          Get the first character of a text in lowercase. The text is converted
          to ASCII. All non word characters are erased.
  
      left
      ----
  
      %left{text,n}
          Return the first “n” characters of “text”.
  
      lower
      -----
  
      %lower{text}
          Convert “text” to lowercase.
  
      nowhitespace
      ------------
  
      %nowhitespace{text,replace}
          Replace all whitespace characters with replace. By default: a dash (-)
          %nowhitespace{$track,_}
  
      num
      ---
  
      %num{number,count}
          Pad decimal number with leading zeros.
          %num{$track,3}
  
      replchars
      ---------
  
      %replchars{text,chars,replace}
          Replace the characters “chars” in “text” with “replace”.
          %replchars{text,ex,-} > t--t
  
      right
      -----
  
      %right{text,n}
          Return the last “n” characters of “text”.
  
      sanitize
      --------
  
      %sanitize{text}
          Delete in most file systems not allowed characters.
  
      shorten
      -------
  
      %shorten{text} or %shorten{text,max_size}
          Shorten “text” on word boundarys.
          %shorten{$title,32}
  
      time
      ----
  
      %time{date_time,format,curformat}
          Return the date and time in any format accepted by strftime. For
          example, to get the year some music was added to your library, use
          %time{$added,%Y}.
  
      title
      -----
  
      %title{text}
          Convert “text” to Title Case.
  
      upper
      -----
  
      %upper{text}
          Convert “text” to UPPERCASE.
  
  optional arguments:
    -h, --help            show this help message and exit
    -f RENAME_FORMAT, --format RENAME_FORMAT
                          Format string.
    -A, --alphanum        Use only alphanumeric characters.
    -a, --ascii           Use only ASCII characters.
    -n, --no-whitespace   Replace all whitespaces with dashes or sometimes
                          underlines.
    -s FIELDS, --skip-if-empty FIELDS
                          Skip rename action if FIELDS are empty. Separate
                          FIELDS using commas: combined_composer,combined_title
    -t RENAME_TARGET, --target RENAME_TARGET
                          Target directory
  

mscx-manager export
-------------------

.. code-block:: text

  usage: mscx-manager export [-h] [-e EXPORT_EXTENSION]
  
  optional arguments:
    -h, --help            show this help message and exit
    -e EXPORT_EXTENSION, --extension EXPORT_EXTENSION
                          Extension to export. If this option is omitted, then
                          the default extension is "pdf".
  

mscx-manager help
-----------------

.. code-block:: text

  usage: mscx-manager help [-h] [-m] [-r]
  
  optional arguments:
    -h, --help      show this help message and exit
    -m, --markdown  Show help in markdown format. This option enables to
                    generate the README file directly form the command line
                    output.
    -r, --rst       Show help in reStructuresText format. This option enables to
                    generate the README file directly form the command line
                    output.
  

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
