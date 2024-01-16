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

Some options change mutliple styles at once:

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

.. code-block:: Python

Set all text font faces (using the method ``score.style.set_text_font_faces(font_face)``,
not available in MuseScore 2):

.. code-block:: Python

    score = Score('score.mscz')
    assert score.style.get("defaultFontFace") == "FreeSerif"

    response = score.style.set_text_font_faces("Alegreya")

    assert response == [
        ("lyricsOddFontFace", "FreeSerif", "Alegreya"),
        ("lyricsEvenFontFace", "FreeSerif", "Alegreya"),
        ("hairpinFontFace", "FreeSerif", "Alegreya"),
        ("pedalFontFace", "FreeSerif", "Alegreya"),
        ("chordSymbolAFontFace", "FreeSerif", "Alegreya"),
        ("chordSymbolBFontFace", "FreeSerif", "Alegreya"),
        ("nashvilleNumberFontFace", "FreeSerif", "Alegreya"),
        ("voltaFontFace", "FreeSerif", "Alegreya"),
        ("ottavaFontFace", "FreeSerif", "Alegreya"),
        ("tupletFontFace", "FreeSerif", "Alegreya"),
        ("defaultFontFace", "FreeSerif", "Alegreya"),
        ("titleFontFace", "FreeSerif", "Alegreya"),
        ("subTitleFontFace", "FreeSerif", "Alegreya"),
        ("composerFontFace", "FreeSerif", "Alegreya"),
        ("lyricistFontFace", "FreeSerif", "Alegreya"),
        ("fingeringFontFace", "FreeSerif", "Alegreya"),
        ("lhGuitarFingeringFontFace", "FreeSerif", "Alegreya"),
        ("rhGuitarFingeringFontFace", "FreeSerif", "Alegreya"),
        ("stringNumberFontFace", "FreeSerif", "Alegreya"),
        ("harpPedalDiagramFontFace", "Edwin", "Alegreya"),
        ("harpPedalTextDiagramFontFace", "Edwin", "Alegreya"),
        ("longInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("shortInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("partInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("expressionFontFace", "FreeSerif", "Alegreya"),
        ("tempoFontFace", "FreeSerif", "Alegreya"),
        ("tempoChangeFontFace", "Edwin", "Alegreya"),
        ("metronomeFontFace", "FreeSerif", "Alegreya"),
        ("measureNumberFontFace", "FreeSerif", "Alegreya"),
        ("mmRestRangeFontFace", "Edwin", "Alegreya"),
        ("translatorFontFace", "FreeSerif", "Alegreya"),
        ("systemFontFace", "FreeSerif", "Alegreya"),
        ("staffFontFace", "FreeSerif", "Alegreya"),
        ("rehearsalMarkFontFace", "FreeSerif", "Alegreya"),
        ("repeatLeftFontFace", "FreeSerif", "Alegreya"),
        ("repeatRightFontFace", "FreeSerif", "Alegreya"),
        ("frameFontFace", "FreeSerif", "Alegreya"),
        ("textLineFontFace", "FreeSerif", "Alegreya"),
        ("systemTextLineFontFace", "Edwin", "Alegreya"),
        ("glissandoFontFace", "FreeSerif", "Alegreya"),
        ("bendFontFace", "FreeSerif", "Alegreya"),
        ("headerFontFace", "FreeSerif", "Alegreya"),
        ("footerFontFace", "FreeSerif", "Alegreya"),
        ("instrumentChangeFontFace", "FreeSerif", "Alegreya"),
        ("stickingFontFace", "FreeSerif", "Alegreya"),
        ("user1FontFace", "FreeSerif", "Alegreya"),
        ("user2FontFace", "FreeSerif", "Alegreya"),
        ("user3FontFace", "FreeSerif", "Alegreya"),
        ("user4FontFace", "FreeSerif", "Alegreya"),
        ("user5FontFace", "FreeSerif", "Alegreya"),
        ("user6FontFace", "FreeSerif", "Alegreya"),
        ("user7FontFace", "FreeSerif", "Alegreya"),
        ("user8FontFace", "FreeSerif", "Alegreya"),
        ("user9FontFace", "FreeSerif", "Alegreya"),
        ("user10FontFace", "FreeSerif", "Alegreya"),
        ("user11FontFace", "FreeSerif", "Alegreya"),
        ("user12FontFace", "FreeSerif", "Alegreya"),
        ("letRingFontFace", "FreeSerif", "Alegreya"),
        ("palmMuteFontFace", "FreeSerif", "Alegreya"),
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

... or generate the autocomplete files by yourself:

::

    musescore-manager --print-completion bash > autocomplete.bash
    musescore-manager --print-completion zsh > autocomplete.zsh
    musescore-manager --print-completion tcsh > autocomplete.tcsh

CLI Usage
=========

:: 

    usage: musescore-manager [-h] [--print-completion {bash,zsh,tcsh}] [-V] [-b]
                             [-k] [-C GENERAL_CONFIG_FILE] [-d] [-m] [--diff]
                             [-e FILE_PATH] [-v] [-E <extension>] [-c META_CLEAN]
                             [-D] [-i <source-fields> <format-string>] [-j]
                             [-l DESTINATION FORMAT_STRING] [-y]
                             [-S DESTINATION_FIELD FORMAT_STRING]
                             [--metatag <field> <value>] [--vbox <field> <value>]
                             [--combined <field> <value>] [-x LYRICS_EXTRACT]
                             [-r LYRICS_REMAP] [-F] [--rename] [-f RENAME_FORMAT]
                             [-A] [-a] [-n] [-K FIELDS] [-t RENAME_TARGET] [-L]
                             [-g <glob-pattern> | --mscz | --mscx]
                             [-s <style-name> <value>] [-Y <file>] [--s3] [--s4]
                             [--list-fonts] [--text-font <font-face>]
                             [--title-font <font-face>]
                             [--musical-symbol-font <font-face>]
                             [--musical-text-font <font-face>]
                             [--staff-space <dimension>]
                             [--page-size <width> <height> <width> <height>]
                             [--margin <dimension>] [--header | --no-header]
                             [--footer | --no-footer]
                             [<path> ...]

    The next generation command line tool to manipulate the XML based "*.mscX" and "*.mscZ" files of the notation software MuseScore.

    positional arguments:
      <path>                Path to a "*.msc[zx]" file or a folder containing
                            "*.msc[zx]" files. can be specified several times.

    options:
      -h, --help            show this help message and exit
      --print-completion {bash,zsh,tcsh}
                            print shell completion script
      -V, --version         show program's version number and exit
      -b, --backup          Create a backup file.
      -k, --colorize        Colorize the command line print statements.
      -C GENERAL_CONFIG_FILE, --config-file GENERAL_CONFIG_FILE
                            Specify a configuration file in the INI format.
      -d, --dry-run         Simulate the actions.
      -m, --mscore          Open and save the XML file in MuseScore after manipulating
                            the XML with lxml to avoid differences in the XML structure.
      --diff                Show a diff of the XML file before and after the
                            manipulation.
      -e FILE_PATH, --executable FILE_PATH
                            Path of the musescore executable.
      -v, --verbose         Make commands more verbose. You can specifiy multiple
                            arguments (. g.: -vvv) to make the command more verbose.
      -E <extension>, --export <extension>
                            Export the scores in a format defined by the extension. The
                            exported file has the same path, only the file extension is
                            different. Further information can be found at the MuseScore
                            website: https://musescore.org/en/handbook/2/file-formats,
                            https://musescore.org/en/handbook/3/file-export,
                            https://musescore.org/en/handbook/4/file-export. MuseScore
                            must be installed and the script must know the location of
                            the binary file.

    clean:
      Clean and reset the formating of the "*.mscx" file

      -Y <file>, --style-file <file>
                            Load a "*.mss" style file and include the contents of this
                            file.

    meta:
      Deal with meta data informations stored in the MuseScore file. MuseScore can store meta data informations in different places:

      # metatag

      ## XML structure of a meta tag:

          <metaTag name="tag"></metaTag>

      ## All meta tags:

      - arranger
      - audioComUrl (new in v4
      - composer
      - copyright
      - creationDate
      - lyricist
      - movementNumber
      - movementTitle
      - mscVersion
      - platform
      - poet (not in v4)
      - source
      - sourceRevisionId
      - subtitle
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

          - title (v2,3: Title)
          - subtitle (v2,3: Subtitle)
          - composer (v2,3: Composer)
          - lyricist (v2,3: Lyricist)

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
          - metatag_audio_com_url
          - metatag_composer
          - metatag_copyright
          - metatag_creation_date
          - metatag_lyricist
          - metatag_movement_number
          - metatag_movement_title
          - metatag_msc_version
          - metatag_platform
          - metatag_poet
          - metatag_source
          - metatag_source_revision_id
          - metatag_subtitle
          - metatag_translator
          - metatag_work_number
          - metatag_work_title
          - vbox_composer
          - vbox_lyricist
          - vbox_subtitle
          - vbox_title

      -c META_CLEAN, --clean-meta META_CLEAN
                            Clean the meta data fields. Possible values: „all“ or a
                            comma separated list of fields, for example:
                            „field_one,field_two“.
      -D, --delete-duplicates
                            Deletes combined_lyricist if this field is equal to
                            combined_composer. Deletes combined_subtitle if this field
                            is equal tocombined_title. Move combined_subtitle to
                            combimed_title if combined_title is empty.
      -i <source-fields> <format-string>, --distribute-fields <source-fields> <format-string>
                            Distribute source fields to target fields by applying a
                            format string on the source fields. It is possible to apply
                            multiple --distribute-fields options. <source-fields> can be
                            a single field or a comma separated list of fields:
                            field_one,field_two. The program tries first to match the
                            <format-string> on the first source field. If thisfails, it
                            tries the second source field ... and so on.
      -j, --json            Additionally write the meta data to a json file.
      -l DESTINATION FORMAT_STRING, --log DESTINATION FORMAT_STRING
                            Write one line per file to a text file. e. g. --log
                            /tmp/musescore-manager.log '$title $composer'
      -y, --synchronize     Synchronize the values of the first vertical frame (vbox)
                            (title, subtitle, composer, lyricist) with the corresponding
                            metadata fields
      -S DESTINATION_FIELD FORMAT_STRING, --set-field DESTINATION_FIELD FORMAT_STRING
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
      --combined <field> <value>, --combined-meta <field> <value>
                            Define the metadata combined in one step for MetaTag and
                            VBox elements. Available fields: composer, lyricist,
                            subtitle, title.

    lyrics:
      -x LYRICS_EXTRACT, --extract LYRICS_EXTRACT, --extract-lyrics LYRICS_EXTRACT
                            Extract each lyrics verse into a separate MuseScore file.
                            Specify ”all” to extract all lyrics verses. The old verse
                            number is appended to the file name, e. g.: score_1.mscx.
      -r LYRICS_REMAP, --remap LYRICS_REMAP, --remap-lyrics LYRICS_REMAP
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
      Rename the “*.msc[zx]” files.Fields and functions you can use in the format string (-f, --format):

      Fields
      ======

          - combined_composer
          - combined_lyricist
          - combined_subtitle
          - combined_title
          - metatag_arranger
          - metatag_audio_com_url
          - metatag_composer
          - metatag_copyright
          - metatag_creation_date
          - metatag_lyricist
          - metatag_movement_number
          - metatag_movement_title
          - metatag_msc_version
          - metatag_platform
          - metatag_poet
          - metatag_source
          - metatag_source_revision_id
          - metatag_subtitle
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

      --rename              Format string.
      -f RENAME_FORMAT, --format RENAME_FORMAT
                            Format string.
      -A, --alphanum        Use only alphanumeric characters.
      -a, --ascii           Use only ASCII characters.
      -n, --no-whitespace   Replace all whitespaces with dashes or sometimes underlines.
      -K FIELDS, --skip-if-empty FIELDS
                            Skip rename action if FIELDS are empty. Separate FIELDS
                            using commas: combined_composer,combined_title
      -t RENAME_TARGET, --target RENAME_TARGET
                            Target directory

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
      --s3, --styles-v3     List all possible version 3 styles.
      --s4, --styles-v4     List all possible version 4 styles.
      --list-fonts          List all font related styles.
      --text-font <font-face>
                            Set nearly all fonts except “romanNumeralFontFace”,
                            “figuredBassFontFace”, “dynamicsFontFace“,
                            “musicalSymbolFont” and “musicalTextFont”.
      --title-font <font-face>
                            Set “titleFontFace” and “subTitleFontFace”.
      --musical-symbol-font <font-face>
                            Set “musicalSymbolFont”, “dynamicsFont” and
                            “dynamicsFontFace”.
      --musical-text-font <font-face>
                            Set “musicalTextFont”.
      --staff-space <dimension>
                            Set the staff space or spatium. This is the vertical
                            distance between two lines of a music staff.
      --page-size <width> <height> <width> <height>
                            Set the page size.
      --margin <dimension>  Set the top, right, bottom and left margins to the same
                            value.
      --header, --no-header
                            Show or hide the header
      --footer, --no-footer
                            Show or hide the footer.

Legacy CLI Usage
================

mscxyz
======

.. code-block:: text

  usage: mscx-manager [-h] [-V] [-b] [-c] [-C GENERAL_CONFIG_FILE] [-d]
                      [-g SELECTION_GLOB] [-m] [--diff] [-e FILE_PATH] [-v]
                      {clean,export,help,meta,lyrics,rename,style} ... path

  The legacy command line tool to manipulate the XML based "*.mscX" and "*.mscZ" files of the notation software MuseScore.

  positional arguments:
    path                  Path to a *.msc[zx]" file or a folder which contains
                          "*.msc[zx]" files. In conjunction with the subcommand "help"
                          this positional parameter accepts the names of all other
                          subcommands or the word "all".

  options:
    -h, --help            show this help message and exit
    -V, --version         show program's version number and exit
    -b, --backup          Create a backup file.
    -c, --colorize        Colorize the command line print statements.
    -C GENERAL_CONFIG_FILE, --config-file GENERAL_CONFIG_FILE
                          Specify a configuration file in the INI format.
    -d, --dry-run         Simulate the actions.
    -g SELECTION_GLOB, --glob SELECTION_GLOB
                          Handle only files which matches against Unix style glob
                          patterns (e. g. "*.mscx", "* - *"). If you omit this option,
                          the standard glob pattern "*.msc[xz]" is used.
    -m, --mscore          Open and save the XML file in MuseScore after manipulating
                          the XML with lxml to avoid differences in the XML structure.
    --diff                Show a diff of the XML file before and after the
                          manipulation.
    -e FILE_PATH, --executable FILE_PATH
                          Path of the musescore executable.
    -v, --verbose         Make commands more verbose. You can specifiy multiple
                          arguments (. g.: -vvv) to make the command more verbose.

  Subcommands:
    {clean,export,help,meta,lyrics,rename,style}
                          Run "subcommand --help" for more informations.
      clean               Clean and reset the formating of the "*.mscx" file
      export              Export the scores to PDFs or to a format specified by the
                          extension. The exported file has the same path, only the
                          file extension is different. See
                          https://musescore.org/en/handbook/2/file-formats
                          https://musescore.org/en/handbook/3/file-export
                          https://musescore.org/en/handbook/4/file-export
      help                Show help. Use “mscx-manager help all” to show help messages
                          of all subcommands. Use “mscx-manager help <subcommand>” to
                          show only help messages for the given subcommand.
      meta                Deal with meta data informations stored in the MuseScore
                          file.
      lyrics              Extract lyrics. Without any option this subcommand extracts
                          all lyrics verses into separate mscx files. This generated
                          mscx files contain only one verse. The old verse number is
                          appended to the file name, e. g.: score_1.mscx.
      rename              Rename the "*.mscx" files.
      style               Change the styles.

Subcommands
===========

mscx-manager clean
------------------

.. code-block:: text

  usage: mscx-manager clean [-h] [-s CLEAN_STYLE]

  options:
    -h, --help            show this help message and exit
    -s CLEAN_STYLE, --style CLEAN_STYLE
                          Load a "*.mss" style file and include the contents of this
                          file.

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
      - metatag_audio_com_url
      - metatag_composer
      - metatag_copyright
      - metatag_creation_date
      - metatag_lyricist
      - metatag_movement_number
      - metatag_movement_title
      - metatag_msc_version
      - metatag_platform
      - metatag_poet
      - metatag_source
      - metatag_source_revision_id
      - metatag_subtitle
      - metatag_translator
      - metatag_work_number
      - metatag_work_title
      - vbox_composer
      - vbox_lyricist
      - vbox_subtitle
      - vbox_title

  options:
    -h, --help            show this help message and exit
    -c META_CLEAN, --clean META_CLEAN
                          Clean the meta data fields. Possible values: „all“ or
                          „field_one,field_two“.
    -D, --delete-duplicates
                          Deletes combined_lyricist if this field is equal to
                          combined_composer. Deletes combined_subtitle if this field
                          is equal tocombined_title. Move combined_subtitle to
                          combimed_title if combined_title is empty.
    -d SOURCE_FIELDS FORMAT_STRING, --distribute-fields SOURCE_FIELDS FORMAT_STRING
                          Distribute source fields to target fields applying a format
                          string on the source fields. It is possible to apply
                          multiple --distribute-fields options. SOURCE_FIELDS can be a
                          single field or a comma separated list of fields:
                          field_one,field_two. The program tries first to match the
                          FORMAT_STRING on the first source field. If this fails, it
                          tries the second source field ... an so on.
    -j, --json            Additionally write the meta data to a json file.
    -l DESTINATION FORMAT_STRING, --log DESTINATION FORMAT_STRING
                          Write one line per file to a text file. e. g. --log
                          /tmp/musescore-manager.log '$title $composer'
    -s, --synchronize     Synchronize the values of the first vertical frame (vbox)
                          (title, subtitle, composer, lyricist) with the corresponding
                          metadata fields
    -S DESTINATION_FIELD FORMAT_STRING, --set-field DESTINATION_FIELD FORMAT_STRING
                          Set value to meta data fields.

mscx-manager lyrics
-------------------

.. code-block:: text

  usage: mscx-manager lyrics [-h] [-e LYRICS_EXTRACT_LEGACY] [-r LYRICS_REMAP]
                             [-f]

  options:
    -h, --help            show this help message and exit
    -e LYRICS_EXTRACT_LEGACY, --extract LYRICS_EXTRACT_LEGACY
                          The lyric verse number to extract or "all".
    -r LYRICS_REMAP, --remap LYRICS_REMAP
                          Remap lyrics. Example: "--remap 3:2,5:3". This example
                          remaps lyrics verse 3 to verse 2 and verse 5 to 3. Use
                          commas to specify multiple remap pairs. One remap pair is
                          separated by a colon in this form: "old:new": "old" stands
                          for the old verse number. "new" stands for the new verse
                          number.
    -f, --fix             Fix lyrics: Convert trailing hyphens ("la- la- la") to a
                          correct hyphenation ("la - la - la")

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
      - metatag_audio_com_url
      - metatag_composer
      - metatag_copyright
      - metatag_creation_date
      - metatag_lyricist
      - metatag_movement_number
      - metatag_movement_title
      - metatag_msc_version
      - metatag_platform
      - metatag_poet
      - metatag_source
      - metatag_source_revision_id
      - metatag_subtitle
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

  options:
    -h, --help            show this help message and exit
    -f RENAME_FORMAT, --format RENAME_FORMAT
                          Format string.
    -A, --alphanum        Use only alphanumeric characters.
    -a, --ascii           Use only ASCII characters.
    -n, --no-whitespace   Replace all whitespaces with dashes or sometimes underlines.
    -s FIELDS, --skip-if-empty FIELDS
                          Skip rename action if FIELDS are empty. Separate FIELDS
                          using commas: combined_composer,combined_title
    -t RENAME_TARGET, --target RENAME_TARGET
                          Target directory

mscx-manager export
-------------------

.. code-block:: text

  usage: mscx-manager export [-h] [-e EXPORT_EXTENSION]

  options:
    -h, --help            show this help message and exit
    -e EXPORT_EXTENSION, --extension EXPORT_EXTENSION
                          Extension to export. If this option is omitted, then the
                          default extension is "pdf".

mscx-manager help
-----------------

.. code-block:: text

  usage: mscx-manager help [-h] [-m] [-r]

  options:
    -h, --help      show this help message and exit
    -m, --markdown  Show help in markdown format. This option enables to
                    generate the README file directly form the command line
                    output.
    -r, --rst       Show help in reStructuresText format. This option enables to
                    generate the README file directly form the command line
                    output.

API Usage
=========

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

List score paths in a nested folder structure:

::

    cd /home/xyz/scores
    find . | sort

::

    .
    ./level1
    ./level1/level2
    ./level1/level2/score2.mscz
    ./level1/level2/level3
    ./level1/level2/level3/score3.mscz
    ./level1/score1.mscz
    ./score0.mscz

.. code-block:: Python

    from mscxyz import list_score_paths, Score

    score_paths = list_score_paths(path="/home/xyz/scores", extension="mscz")
    for score_path in score_paths:
        score = Score(score_path)
        assert score.path.exists()
        assert score.extension == "mscz"

    assert len(score_paths) == 4

    assert "level1/level2/level3/score3.mscz" in score_paths[0]
    assert "level1/level2/score2.mscz" in score_paths[1]
    assert "level1/score1.mscz" in score_paths[2]
    assert "score0.mscz" in score_paths[3]

``meta``
--------

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

Configuration file
==================

``/etc/mscxyz.ini``

.. code-block:: ini

    [general]
    executable = /usr/bin/mscore3
    colorize = True

    [rename]
    format = '$combined_title ($combined_composer)'

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
