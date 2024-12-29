.. image:: http://img.shields.io/pypi/v/mscxyz.svg
    :target: https://pypi.org/project/mscxyz
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/mscxyz/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/mscxyz/actions/workflows/tests.yml
    :alt: Tests

.. image:: https://readthedocs.org/projects/mscxyz/badge/?version=latest
    :target: https://mscxyz.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

==============================
mscxyz - The MuseScore Manager
==============================

Manipulate the XML based ``.mscz`` and ``.mscx`` files of the notation software
`MuseScore <https://musescore.org>`_.

Features
========

* Batch processing of ``.msc[zx]`` files in nested folder structures
* Rename ``.msc[zx]`` files based on meta tags
* Set, read and synchronized meta tags
* Set style properties
* Can handle MuseScore 2, 3 and 4 files
* Command line interface
* Python API

Installation
============

.. code:: Shell

    pipx install mscxyz

How to ...
==========

... specify the MuseScore files to work on?
-------------------------------------------

To find out which files are selected by the script, the ``-L, --list-files``
option can be used. The ``--list-files`` option lists as the name suggests
only the file paths and doesn’t touch the specified *MuseScore* files:

::

    musescore-manager --list-files

Without an option the script lists all MuseScore files in the current directory
in a recursive way (``musescore-manager`` = ``musescore-manager .``).
You can pass multiple file paths to the script:

::

    musescore-manager -L score1.mscz score2.mscz score3.mscz

or multiple directories:

::

    musescore-manager -L folder1 folder2 folder3

or use the path expansion of your shell:

::

    musescore-manager -L *.mscz

To apply glob patterns on the file paths, the ``--glob`` option can be used.

::

    musescore-manager -L --glob "*/folder/*.mscz"

To selection only *mscz* oder *mscx* files use the options ``--mscz`` or ``--mscx``.
Don’t mix the options ``--mscz`` and ``--mscx`` with the option ``--glob``.

The python package ``mscxyz`` exports a function named ``list_path`` which can
be used to list the paths of MuseScore files. This allows you to list score
paths in a nested folder structure in a similar way to the command line.
This folder structure is used for the following example:

::

    cd /home/xyz/scores
    find . | sort

    .
    ./level1
    ./level1/level2
    ./level1/level2/score2.mscz
    ./level1/level2/level3
    ./level1/level2/level3/score3.mscz
    ./level1/score1.mscz
    ./score0.mscz

.. code-block:: Python

    from mscxyz import list_path, Score

    score_paths = []
    for score_path in list_path(path="/home/xyz/scores", extension="mscz"):
        score = Score(score_path)
        assert score.path.exists()
        assert score.extension == "mscz"
        score_paths.append(str(score_path))

    assert len(score_paths) == 4

    assert "level1/level2/level3/score3.mscz" in score_paths[3]
    assert "level1/level2/score2.mscz" in score_paths[2]
    assert "level1/score1.mscz" in score_paths[1]
    assert "score0.mscz" in score_paths[0]

... export files to different files types?
------------------------------------------

On the command line use the option ``--export`` to export the scores to
different file types. The exported file has the same path, only the file
extension is different. Further information about the supported file formats
can be found at the MuseScore website:
`Version 2 <https://musescore.org/en/handbook/2/file-formats>`_,
`Version 3 <https://musescore.org/en/handbook/3/file-export>`_ and
`Version 4 <https://musescore.org/en/handbook/4/file-export>`_
The MuseScore binay must be installed and the script must know the location of t
his binary.

::

    musescore-manager --export pdf
    musescore-manager --export png

.. code-block:: Python

    score = Score('score.mscz')
    score.export.to_extension("musicxml")

... change the styling of a score?
----------------------------------

Set a single style by its style name ``--style``:

::

    musescore-manager --style staffDistance 7.5 score.mscz

To set mulitple styles at once specify the option ``--style`` multiple times:

::

    musescore-manager --style staffUpperBorder 5.5 --style staffLowerBorder 5.5 score.mscz

... change the font faces of a score?
-------------------------------------

Some options change mutliple font related xml elements at once:

::

    musescore-manager --text-font Alegreya score.mscz
    musescore-manager --title-font "Alegreya Sans" score.mscz
    musescore-manager --musical-symbol-font Leland score.mscz
    musescore-manager --musical-text-font "Leland Text" score.mscz

Set all font faces (using a for loop, not available in MuseScore 2):

.. code-block:: Python

    score = Score('score.mscz')
    assert score.style.get("defaultFontFace") == "FreeSerif"

    for element in score.style.styles:
        if "FontFace" in element.tag:
            element.text = "Alegreya"
    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get("defaultFontFace") == "Alegreya"

Set all text font faces (using the method ``score.style.set_text_font_faces(font_face)``,
not available in MuseScore 2):

.. code-block:: Python

    score = Score('score.mscz')
    assert score.style.get("defaultFontFace") == "FreeSerif"

    response = score.style.set_text_font_faces("Alegreya")

    assert response == [
        ...
        ("harpPedalTextDiagramFontFace", "Edwin", "Alegreya"),
        ("longInstrumentFontFace", "FreeSerif", "Alegreya"),
        ...
    ]

    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get("defaultFontFace") == "Alegreya"

... enable autocomplete support?
--------------------------------

Use one of the following autocomplete files ...

* `bash <https://github.com/Josef-Friedrich/mscxyz/blob/main/autocomplete.bash>`_
* `zsh <https://github.com/Josef-Friedrich/mscxyz/blob/main/autocomplete.zsh>`_
* `tcsh <https://github.com/Josef-Friedrich/mscxyz/blob/main/autocomplete.tcsh>`_

... or generate the autocomplete files by yourself?
---------------------------------------------------

::

    musescore-manager --print-completion bash > autocomplete.bash
    musescore-manager --print-completion zsh > autocomplete.zsh
    musescore-manager --print-completion tcsh > autocomplete.tcsh

... rename many files at once?
------------------------------

Fields
^^^^^^

- ``title``: The combined title
- ``subtitle``: The combined subtitle
- ``composer``: The combined composer
- ``lyricist``: The combined lyricist
- ``vbox_title``: The title field of the score as it appears in the center of the first vertical frame (VBox).
- ``vbox_subtitle``: The subtitle field of the score as it appears in the center of the first vertical frame (VBox).
- ``vbox_composer``: The composer field of the score as it appears in the center of the first vertical frame (VBox).
- ``vbox_lyricist``: The lyricist field of the score as it appears in the center of the first vertical frame (VBox).
- ``metatag_arranger``: The arranger field stored as project properties.
- ``metatag_audio_com_url``: The audio.com URL field stored as project properties.
- ``metatag_composer``: The composer field stored as project properties.
- ``metatag_copyright``: The copyright field stored as project properties.
- ``metatag_creation_date``: The creation date field stored as project properties.
- ``metatag_lyricist``: The lyricist field stored as project properties.
- ``metatag_movement_number``: The movement number field stored as project properties.
- ``metatag_movement_title``: The movement title field stored as project properties.
- ``metatag_msc_version``: The MuseScore version field stored as project properties.
- ``metatag_platform``: The platform field stored as project properties.
- ``metatag_poet``: The poet field stored as project properties.
- ``metatag_source``: The source field stored as project properties.
- ``metatag_source_revision_id``: The source revision ID field stored as project properties.
- ``metatag_subtitle``: The subtitle field stored as project properties.
- ``metatag_translator``: The translator field stored as project properties.
- ``metatag_work_number``: The work number field stored as project properties.
- ``metatag_work_title``: The work title field stored as project properties.
- ``version``: The MuseScore version as a floating point number, for example ``2.03``, ``3.01`` or ``4.20``.
- ``version_major``: The major MuseScore version, for example ``2``, ``3`` or ``4``.
- ``program_version``: The semantic version number of the MuseScore program, for example: ``4.2.0``.
- ``program_revision``: The revision number of the MuseScore program, for example: ``eb8d33c``.
- ``path``: The absolute path of the MuseScore file, for example ``/home/xyz/score.mscz``.
- ``backup_file``: The absolute path of the backup file. The string ``_bak`` is appended to the file name before the extension.
- ``json_file``: The absolute path of the JSON file in which the metadata can be exported.
- ``dirname``: The name of the containing directory of the MuseScore file, for example: ``/home/xyz/score_files``.
- ``filename``: The filename of the MuseScore file, for example:``score.mscz``.
- ``basename``: The basename of the score file, for example: ``score``.
- ``extension``: The extension (``mscx`` or ``mscz``) of the score file.

Functions
^^^^^^^^^

alpha
  ``%alpha{text}``:  This function first ASCIIfies the given text, then all
  non alphabet characters are replaced with whitespaces.

  **Example:** ``%alpha{a1b23c}`` → ``a b c``

alphanum
  ``%alphanum{text}``:  This function first ASCIIfies the given text, then all
  non alpanumeric characters are replaced with whitespaces.

  **Example:** ``%alphanum{après-évêque1}`` → ``apres eveque1``

asciify
  ``%asciify{text}``:  Translate non-ASCII characters to their ASCII
  equivalents. For example, “café” becomes “cafe”. Uses the mapping provided
  by the unidecode module.

  **Example:** ``%asciify{äÄöÖüÜ}`` → ``aeAeoeOeueUe``

delchars
  ``%delchars{text,chars}``:  Delete every single character of “chars“ in
  “text”.

  **Example:** ``%delchars{Schubert, ue}`` → ``Schbrt``

deldupchars
  ``%deldupchars{text,chars}``:  Search for duplicate characters and replace
  with only one occurrance of this characters.

  **Example:** ``%deldupchars{a---b___c...d}`` → ``a-b_c.d``; ``%deldupchars{a
  ---b___c, -}`` → ``a-b___c``

first
  ``%first{text}`` or ``%first{text,count,skip}`` or
  ``%first{text,count,skip,sep,join}``:  Returns the first item, separated by
  ``;``. You can use ``%first{text,count,skip}``, where count is the number of
  items (default 1) and skip is number to skip (default 0). You can also use
  ``%first{text,count,skip,sep,join}`` where ``sep`` is the separator, like
  ``;`` or ``/`` and join is the text to concatenate the items.

  **Example:** ``%first{Alice / Bob / Eve,2,0, / , & }`` → ``Alice & Bob``

if
  ``%if{condition,trueval}`` or ``%if{condition,trueval,falseval}``:  If
  condition is nonempty (or nonzero, if it’s a number), then returns the
  second argument. Otherwise, returns the third argument if specified (or
  nothing if ``falseval`` is left off).

  **Example:** ``x%if{false,foo}`` → ``x``

ifdef
  ``%ifdef{field}``, ``%ifdef{field,trueval}`` or
  ``%ifdef{field,trueval,falseval}``:  If field exists, then return
  ``trueval`` or field (default). Otherwise, returns ``falseval``. The field
  should be entered without ``$``.

  **Example:** ``%ifdef{compilation,Compilation}``

ifdefempty
  ``%ifdefempty{field,text}`` or ``%ifdefempty{field,text,falsetext}``:  If
  field exists and is empty, then return ``truetext``. Otherwise, returns
  ``falsetext``. The field should be entered without ``$``.

  **Example:** ``%ifdefempty{compilation,Album,Compilation}``

ifdefnotempty
  ``%ifdefnotempty{field,text}`` or ``%ifdefnotempty{field,text,falsetext}``:
  If field is not empty, then return ``truetext``. Otherwise, returns
  ``falsetext``. The field should be entered without ``$``.

  **Example:** ``%ifdefnotempty{compilation,Compilation,Album}``

initial
  ``%initial{text}``:  Get the first character of a text in lowercase. The
  text is converted to ASCII. All non word characters are erased.

  **Example:** ``%initial{Schubert}`` → ``s``

left
  ``%left{text,n}``:  Return the first “n” characters of “text”.

  **Example:** ``%left{Schubert, 3}`` → ``Sch``

lower
  ``%lower{text}``:  Convert “text” to lowercase.

  **Example:** ``%lower{SCHUBERT}`` → ``schubert``

nowhitespace
  ``%nowhitespace{text,replace}``:  Replace all whitespace characters with
  ``replace``. By default: a dash (``-``)

  **Example:** ``%nowhitespace{a b}`` → ``a-b``; ``%nowhitespace{a b, _}`` →
  ``a_b``

num
  ``%num{number,count}``:  Pad decimal number with leading zeros.

  **Example:** ``%num{7,3}`` → ``007``

replchars
  ``%replchars{text,chars,replace}``:  Replace the characters “chars” in
  “text” with “replace”.

  **Example:** ``%replchars{Schubert,-,ue}`` → ``Sch-b-rt``

right
  ``%right{text,n}``:  Return the last “n” characters of “text”.

  **Example:** ``%right{Schubert,3}`` → ``ert``

sanitize
  ``%sanitize{text}``:  Delete characters that are not allowed in most file
  systems.

  **Example:** ``%sanitize{x:*?<>|/~&x}`` → ``xx``

shorten
  ``%shorten{text}`` or ``%shorten{text,max_size}``:  Shorten “text” on word
  boundarys.

  **Example:** ``%shorten{Lorem ipsum dolor sit, 10}`` → ``Lorem``

time
  ``%time{date_time,format,curformat}``:  Return the date and time in any
  format accepted by ``strftime``. For example, to get the year, use
  ``%time{$added,%Y}``.

  **Example:** ``%time{30 Nov 2024,%Y,%d %b %Y}`` → ``2024``

title
  ``%title{text}``:  Convert “text” to Title Case.

  **Example:** ``%title{franz schubert}`` → ``Franz Schubert``

upper
  ``%upper{text}``:  Convert “text” to UPPERCASE.

  **Example:** ``%upper{foo}`` → ``FOO``

Template Symbols (or Variables)
  In path templates, symbols or varialbes such as ``$title``
  (any name with the prefix ``$``) are replaced by the corresponding value.

  Because ``$`` is used to delineate a field reference, you can use ``$$`` to emit
  a dollars sign. As with `Python template strings`_, ``${title}`` is equivalent
  to ``$title``; you can use this if you need to separate a field name from the
  text that follows it.

.. _Python template strings: https://docs.python.org/library/string.html#template-strings

Template Functions (or Macros)
  Path templates also support *function calls*, which can be used to transform
  text and perform logical manipulations. The syntax for function calls is like
  this: ``%func{arg,arg}``. For example, the ``upper`` function makes its argument
  upper-case, so ``%upper{lorem ipsum}`` will be replaced with ``LOREM IPSUM``.
  You can, of course, nest function calls and place variable references in
  function arguments, so ``%upper{$title}`` becomes the upper-case version of the
  title.

Syntax Details
  The characters ``$``, ``%``, ``{``, ``}``, and ``,`` are “special” in the path
  template syntax. This means that, for example, if you want a ``%`` character to
  appear in your paths, you’ll need to be careful that you don’t accidentally
  write a function call. To escape any of these characters (except ``{``, and
  ``,`` outside a function argument), prefix it with a ``$``.  For example,
  ``$$`` becomes ``$``; ``$%`` becomes ``%``, etc. The only exceptions are:

  * ``${``, which is ambiguous with the variable reference syntax (like
    ``${title}``). To insert a ``{`` alone, it's always sufficient to just type
    ``{``.
  * commas are used as argument separators in function calls. Inside of a
    function’s argument, use ``$,`` to get a literal ``,`` character. Outside of
    any function argument, escaping is not necessary: ``,`` by itself will
    produce ``,`` in the output.

  If a value or function is undefined, the syntax is simply left unreplaced. For
  example, if you write ``$foo`` in a path template, this will yield ``$foo`` in
  the resulting paths because "foo" is not a valid field name. The same is true of
  syntax errors like unclosed ``{}`` pairs; if you ever see template syntax
  constructs leaking into your paths, check your template for errors.

  If an error occurs in the Python code that implements a function, the function
  call will be expanded to a string that describes the exception so you can debug
  your template. For example, the second parameter to ``%left`` must be an
  integer; if you write ``%left{foo,bar}``, this will be expanded to something
  like ``<ValueError: invalid literal for int()>``.

The following example assumes that the folder ``/home/xyz/messy-leadsheets``
contains the following three MuseScore files: ``folsom prison blues.mscz``,
``Johnny Cash - I Walk the Line.mscz``, ``Jackson (Cash).mscz``
The files are named arbitrarily without any recognizable pattern, but they have a
title in the first vertical frame (VBox).

The files should be moved to a target directory (``--target /home/xyz/tidy-leadsheets``) and
the file names should not contain any spaces (``--no-whitespace``).
The title should be used as the file name (``--rename '$vbox_title'``).
The individual files should be stored in subdirectories named after the first
letter of the title (``--rename '%lower{%shorten{$vbox_title,1}}/...'``)

::

    musescore-manager --rename '%lower{%shorten{$vbox_title,1}}/$vbox_title' \
        --target /home/xyz/tidy-leadsheets \
        --no-whitespace \
        /home/xyz/messy-leadsheets

After executing the above command on the command line, ``find /home/xyz/tidy-leadsheets``
should show the following output:

::

    i/I-Walk-the-Line.mscz
    j/Jackson.mscz
    f/Folsom-Prison-Blues.mscz

... use the Python API?
-----------------------

Please visit the `API documentation <https://mscxyz.readthedocs.io>`_ on readthedocs.

Instantiate a ``Score`` object:

.. code-block:: Python

    from mscxyz import Score
    score = Score('score.mscz')
    assert score.path.exists()
    assert score.filename == "score.mscz"
    assert score.basename == "score"
    assert score.extension == "mscz"
    assert score.version == 4.20
    assert score.version_major == 4

Examine the most important attribute of a ``Score`` object: ``xml_root``.
It is the root element of the XML document in which MuseScore stores all information
about a score.
It’s best to take a look at the `lxml API <https://lxml.de/api.html>`_ documentation
to see what you can do with this element. So much can be revealed:
lots of interesting things.

.. code-block:: Python

    score = Score('score.mscz')

    def print_elements(element: _Element, level: int) -> None:
        for sub_element in element:
            print(f"{'    ' * level}<{sub_element.tag}>")
            print_elements(sub_element, level + 1)

    print_elements(score.xml_root, 0)

The output of the code example is very long, so here is a shortened version:

::

    <programVersion>
    <programRevision>
    <LastEID>
    <Score>
        <Division>
        <showInvisible>
        <showUnprintable>
        <showFrames>
        <showMargins>
        <open>
        <metaTag>
        ...

... edit the meta data of a score file?
---------------------------------------

metatag
^^^^^^^

XML structure of a meta tag:

.. code-block:: xml

    <metaTag name="tag"></metaTag>

All meta tags:

- ``arranger``
- ``audioComUrl`` (new in v4)
- ``composer``
- ``copyright``
- ``creationDate``
- ``lyricist``
- ``movementNumber``
- ``movementTitle``
- ``mscVersion``
- ``platform``
- ``poet`` (not in v4)
- ``source``
- ``sourceRevisionId``
- ``subtitle``
- ``translator``
- ``workNumber``
- ``workTitle``

vbox
^^^^

XML structure of a vbox tag:

.. code-block:: xml

    <VBox>
        <Text>
        <style>title</style>
        <text>Some title text</text>
        </Text>

All vbox tags:

- ``title`` (v2,3: ``Title``)
- ``subtitle`` (v2,3: ``Subtitle``)
- ``composer`` (v2,3: ``Composer``)
- ``lyricist`` (v2,3: ``Lyricist``)

This command line tool bundles some meta data informations:

Combined meta data fields:
^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``title`` (1. ``vbox_title`` 2. ``metatag_work_title``)
- ``subtitle`` (1. ``vbox_subtitle`` 2. ``metatag_subtitle`` 3. ``metatag_movement_title``)
- ``composer`` (1. ``vbox_composer`` 2. ``metatag_composer``)
- ``lyricist`` (1. ``vbox_lyricist`` 2. ``metatag_lyricist``)

Set the meta tag ``composer``:

.. code-block:: xml

    <museScore version="4.20">
        <Score>
            <metaTag name="composer">Composer</metaTag>

.. code-block:: Python

    score = Score('score.mscz')
    assert score.meta.meta_tag.composer == "Composer"

    score.meta.meta_tag.composer  = "Mozart"
    score.save()

    new_score: Score = score.reload()
    assert new_score.meta.meta_tag.composer == "Mozart"

.. code-block:: xml

    <museScore version="4.20">
        <Score>
            <metaTag name="composer">Mozart</metaTag>

CLI Usage
=========

:: 

    usage: musescore-manager [-h] [--print-completion {bash,zsh,tcsh}]
                             [-C <file-path>] [-b] [-d] [--catch-errors] [-m]
                             [-e FILE_PATH] [-E <extension>] [--compress]
                             [--remove-origin] [-V] [-v] [-k | --color | --no-color]
                             [--diff] [--print-xml] [-c <fields>] [-D]
                             [-i <source-fields> <format-string>] [-j]
                             [-l <log-file> <format-string>] [-y]
                             [-S <field> <format-string>]
                             [--metatag <field> <value>] [--vbox <field> <value>]
                             [--title <string>] [--subtitle <string>]
                             [--composer <string>] [--lyricist <string>]
                             [-x <number-or-all>] [-r <remap-pairs>] [-F]
                             [--rename <path-template>]
                             [-t <directory> | --only-filename] [-A] [-a] [-n]
                             [-K <fields>] [--list-fields] [--list-functions] [-L]
                             [-g <glob-pattern> | --mscz | --mscx]
                             [-s <style-name> <value>] [--clean] [-Y <file>] [--s3]
                             [--s4] [--reset-small-staffs] [--list-fonts]
                             [--text-font <font-face>] [--title-font <font-face>]
                             [--musical-symbol-font {Leland,Bravura,Emmentaler,Gonville,MuseJazz,Petaluma,Finale Maestro,Finale Broadway}]
                             [--musical-text-font {Leland Text,Bravura Text,Emmentaler Text,Gonville Text,MuseJazz Text,Petaluma Text,Finale Maestro Text,Finale Broadway Text}]
                             [--staff-space <dimension>]
                             [--page-size <width> <height>] [--a4] [--letter]
                             [--margin <dimension>]
                             [--show-header | --no-show-header]
                             [--header-first-page | --no-header-first-page]
                             [--different-odd-even-header | --no-different-odd-even-header]
                             [--header <left> <center> <right>]
                             [--header-odd-even <odd-left> <even-left> <odd-center> <even-center> <odd-right> <even-right>]
                             [--clear-header] [--show-footer | --no-show-footer]
                             [--footer-first-page | --no-footer-first-page]
                             [--different-odd-even-footer | --no-different-odd-even-footer]
                             [--footer <left> <center> <right>]
                             [--footer-odd-even <odd-left> <even-left> <odd-center> <even-center> <odd-right> <even-right>]
                             [--clear-footer]
                             [--lyrics-font-size STYLE_LYRICS_FONT_SIZE]
                             [--lyrics-min-distance STYLE_LYRICS_MIN_DISTANCE]
                             [<path> ...]

    The next generation command line tool to manipulate the XML based "*.mscX" and "*.mscZ" files of the notation software MuseScore.

    positional arguments:
      <path>                Path to a "*.msc[zx]" file or a folder containing
                            "*.msc[zx]" files. can be specified several times.

    options:
      -h, --help            show this help message and exit
      --print-completion {bash,zsh,tcsh}
                            print shell completion script
      -C <file-path>, --config-file <file-path>
                            Specify a configuration file in the INI format.
      -b, --backup          Create a backup file.
      -d, --dry-run         Simulate the actions.
      --catch-errors        Print error messages instead stop execution in a batch run.
      -m, --mscore, --save-in-mscore
                            Open and save the XML file in MuseScore after manipulating
                            the XML with lxml to avoid differences in the XML structure.
      -e FILE_PATH, --executable FILE_PATH
                            Path of the musescore executable.

    export:
      Export the scores in different formats.

      -E <extension>, --export <extension>
                            Export the scores in a format defined by the extension. The
                            exported file has the same path, only the file extension is
                            different. Further information can be found at the MuseScore
                            website: https://musescore.org/en/handbook/2/file-formats,
                            https://musescore.org/en/handbook/3/file-export,
                            https://musescore.org/en/handbook/4/file-export. MuseScore
                            must be installed and the script must know the location of
                            the binary file.
      --compress            Save an uncompressed MuseScore file (*.mscx) as a compressed
                            file (*.mscz).
      --remove-origin       Delete the uncompressed original MuseScore file (*.mscx) if
                            it has been successfully converted to a compressed file
                            (*.mscz).

    info:
      Print informations about the score and the CLI interface itself.

      -V, --version         show program's version number and exit
      -v, --verbose         Make commands more verbose. You can specifiy multiple
                            arguments (. g.: -vvv) to make the command more verbose.
      -k, --color, --no-color
                            Colorize the command line print statements.
      --diff                Show a diff of the XML file before and after the
                            manipulation.
      --print-xml           Print the XML markup of the score.

    meta:
      Deal with meta data informations stored in the MuseScore file.

      -c <fields>, --clean-meta <fields>
                            Clean the meta data fields. Possible values: „all“ or a
                            comma separated list of fields, for example:
                            „field_one,field_two“.
      -D, --delete-duplicates
                            Deletes lyricist if this field is equal to composer. Deletes
                            subtitle if this field is equal totitle. Move subtitle to
                            combimed_title if title is empty.
      -i <source-fields> <format-string>, --distribute-fields <source-fields> <format-string>
                            Distribute source fields to target fields by applying a
                            format string on the source fields. It is possible to apply
                            multiple --distribute-fields options. <source-fields> can be
                            a single field or a comma separated list of fields:
                            field_one,field_two. The program tries first to match the
                            <format-string> on the first source field. If thisfails, it
                            tries the second source field ... and so on.
      -j, --json            Write the meta data to a json file. The resulting file has
                            the same path as the input file, only the extension is
                            changed to “json”.
      -l <log-file> <format-string>, --log <log-file> <format-string>
                            Write one line per file to a text file. e. g. --log
                            /tmp/musescore-manager.log '$title $composer'
      -y, --synchronize     Synchronize the values of the first vertical frame (vbox)
                            (title, subtitle, composer, lyricist) with the corresponding
                            metadata fields
      -S <field> <format-string>, --set-field <field> <format-string>
                            Set value to meta data fields.
      --metatag <field> <value>, --metatag-meta <field> <value>
                            Define the metadata in MetaTag elements. Available fields:
                            arranger, audio_com_url, composer, copyright, creation_date,
                            lyricist, movement_number, movement_title, msc_version,
                            platform, poet, source, source_revision_id, subtitle,
                            translator, work_number, work_title.
      --vbox <field> <value>, --vbox-meta <field> <value>
                            Define the metadata in VBox elements. Available fields:
                            composer, lyricist, subtitle, title.
      --title <string>      Create a vertical frame (vbox) containing a title text field
                            and set the corresponding document properties work title
                            field (metatag).
      --subtitle <string>   Create a vertical frame (vbox) containing a subtitle text
                            field and set the corresponding document properties subtitle
                            and movement title filed (metatag).
      --composer <string>   Create a vertical frame (vbox) containing a composer text
                            field and set the corresponding document properties composer
                            field (metatag).
      --lyricist <string>   Create a vertical frame (vbox) containing a lyricist text
                            field and set the corresponding document properties lyricist
                            field (metatag).

    lyrics:
      -x <number-or-all>, --extract <number-or-all>, --extract-lyrics <number-or-all>
                            Extract each lyrics verse into a separate MuseScore file.
                            Specify ”all” to extract all lyrics verses. The old verse
                            number is appended to the file name, e. g.: score_1.mscx.
      -r <remap-pairs>, --remap <remap-pairs>, --remap-lyrics <remap-pairs>
                            Remap lyrics. Example: "--remap 3:2,5:3". This example
                            remaps lyrics verse 3 to verse 2 and verse 5 to 3. Use
                            commas to specify multiple remap pairs. One remap pair is
                            separated by a colon in this form: "old:new": "old" stands
                            for the old verse number. "new" stands for the new verse
                            number.
      -F, --fix, --fix-lyrics
                            Fix lyrics: Convert trailing hyphens ("la- la- la") to a
                            correct hyphenation ("la - la - la")

    rename:
      Rename the “*.msc[zx]” files. 

      --rename <path-template>
                            A path template string to set the destination location.
      -t <directory>, --target <directory>
                            Target directory
      --only-filename       Rename only the filename and don’t move the score to a
                            different directory.
      -A, --alphanum        Use only alphanumeric characters.
      -a, --ascii           Use only ASCII characters.
      -n, --no-whitespace   Replace all whitespaces with dashes or sometimes underlines.
      -K <fields>, --skip-if-empty <fields>
                            Skip the rename action if the fields specified in <fields>
                            are empty. Multiple fields can be separated by commas, e.
                            g.: composer,title
      --list-fields         List all available fields that can be used in the path
                            templates.
      --list-functions      List all available functions that can be used in the path
                            templates.

    selection:
      The following options affect how the manager selects the MuseScore files.

      -L, --list-files      Only list files and do nothing else.
      -g <glob-pattern>, --glob <glob-pattern>
                            Handle only files which matches against Unix style glob
                            patterns (e. g. "*.mscx", "* - *"). If you omit this option,
                            the standard glob pattern "*.msc[xz]" is used.
      --mscz                Take only "*.mscz" files into account.
      --mscx                Take only "*.mscx" files into account.

    style:
      Change the styles.

      -s <style-name> <value>, --style <style-name> <value>
                            Set a single style value. For example: --style pageWidth 8.5
      --clean               Clean and reset the formating of the "*.mscx" file
      -Y <file>, --style-file <file>
                            Load a "*.mss" style file and include the contents of this
                            file.
      --s3, --styles-v3     List all possible version 3 styles.
      --s4, --styles-v4     List all possible version 4 styles.
      --reset-small-staffs  Reset all small staffs to normal size.

    font (style):
      Change the font faces of a score.

      --list-fonts          List all font related styles.
      --text-font <font-face>
                            Set nearly all fonts except “romanNumeralFontFace”,
                            “figuredBassFontFace”, “dynamicsFontFace“,
                            “musicalSymbolFont” and “musicalTextFont”.
      --title-font <font-face>
                            Set “titleFontFace” and “subTitleFontFace”.
      --musical-symbol-font {Leland,Bravura,Emmentaler,Gonville,MuseJazz,Petaluma,Finale Maestro,Finale Broadway}
                            Set “musicalSymbolFont”, “dynamicsFont” and
                            “dynamicsFontFace”.
      --musical-text-font {Leland Text,Bravura Text,Emmentaler Text,Gonville Text,MuseJazz Text,Petaluma Text,Finale Maestro Text,Finale Broadway Text}
                            Set “musicalTextFont”.

    page (style):
      Page settings.

      --staff-space <dimension>
                            Set the staff space or spatium. This is the vertical
                            distance between two lines of a music staff.
      --page-size <width> <height>
                            Set the page size.
      --a4, --din-a4        Set the paper size to DIN A4 (210 by 297 mm).
      --letter              Set the paper size to Letter (8.5 by 11 in).
      --margin <dimension>  Set the top, right, bottom and left margins to the same
                            value.

    header (style):
      Change the header.

      --show-header, --no-show-header
                            Show or hide the header.
      --header-first-page, --no-header-first-page
                            Show the header on the first page.
      --different-odd-even-header, --no-different-odd-even-header
                            Use different header for odd and even pages.
      --header <left> <center> <right>
                            Set the header for all pages.
      --header-odd-even <odd-left> <even-left> <odd-center> <even-center> <odd-right> <even-right>
                            Set different headers for odd and even pages.
      --clear-header        Clear all header fields by setting all fields to empty
                            strings. The header is hidden.

    footer (style):
      Change the footer.

      --show-footer, --no-show-footer
                            Show or hide the footer.
      --footer-first-page, --no-footer-first-page
                            Show the footer on the first page.
      --different-odd-even-footer, --no-different-odd-even-footer
                            Use different footers for odd and even pages.
      --footer <left> <center> <right>
                            Set the footer for all pages.
      --footer-odd-even <odd-left> <even-left> <odd-center> <even-center> <odd-right> <even-right>
                            Set different footers for odd and even pages.
      --clear-footer        Clear all footer fields by setting all fields to empty
                            strings. The footer is hidden.

    lyrics (style):
      Change the lyrics styles.

      --lyrics-font-size STYLE_LYRICS_FONT_SIZE
                            Set the font size of both even and odd lyrics.
      --lyrics-min-distance STYLE_LYRICS_MIN_DISTANCE
                            Set the minimum gap or minimum distance between syllables or
                            words.

Configuration file
==================

``/etc/mscxyz.ini``

.. code-block:: ini

    [general]
    executable = /usr/bin/mscore3
    colorize = True

    [rename]
    format = '$title ($composer)'

Other MuseScore related projects
================================

* https://github.com/johentsch/ms3

Development
===========

Test
----

::

    make test

Publish a new version
---------------------

::

    git tag 1.1.1
    git push --tags
    make publish

Package documentation
---------------------

The package documentation is hosted on
`readthedocs <http://mscxyz.readthedocs.io>`_.

Generate the package documentation:

::

    make docs
