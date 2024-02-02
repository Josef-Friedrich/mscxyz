**********************
Comande line interface
**********************

:: 

    usage: musescore-manager [-h] [--print-completion {bash,zsh,tcsh}] [-V] [-b]
                             [--bail] [--catch-errors] [-k] [-C GENERAL_CONFIG_FILE]
                             [-d] [-m] [--diff] [-e FILE_PATH] [-v] [-E <extension>]
                             [--compress] [-c META_CLEAN] [-D]
                             [-i <source-fields> <format-string>] [-j]
                             [-l <log-file> <format-string>] [-y]
                             [-S DESTINATION_FIELD FORMAT_STRING]
                             [--metatag <field> <value>] [--vbox <field> <value>]
                             [-x LYRICS_EXTRACT] [-r LYRICS_REMAP] [-F]
                             [--rename <path-template>]
                             [-t <directory> | --only-filename] [-A] [-a] [-n]
                             [-K <fields>] [-L]
                             [-g <glob-pattern> | --mscz | --mscx]
                             [-s <style-name> <value>] [--clean] [-Y <file>] [--s3]
                             [--s4] [--list-fonts] [--text-font <font-face>]
                             [--title-font <font-face>]
                             [--musical-symbol-font <font-face>]
                             [--musical-text-font <font-face>]
                             [--staff-space <dimension>]
                             [--page-size <width> <height>] [--a4] [--letter]
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
      --bail                Stop execution when an exception occurs.
      --catch-errors        Print error messages instead stop execution in a batch run.
      -k, --colorize        Colorize the command line print statements.
      -C GENERAL_CONFIG_FILE, --config-file GENERAL_CONFIG_FILE
                            Specify a configuration file in the INI format.
      -d, --dry-run         Simulate the actions.
      -m, --mscore, --save-in-mscore
                            Open and save the XML file in MuseScore after manipulating
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
      --compress            Save an uncompressed MuseScore file (*.mscx) as a compressed
                            file (*.mscz).

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
      -j, --json            Write the meta data to a json file. The resulting file has
                            the same path as the input file, only the extension is
                            changed to “json”.
      -l <log-file> <format-string>, --log <log-file> <format-string>
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
      --page-size <width> <height>
                            Set the page size.
      --a4, --din-a4        Set the paper size to DIN A4 (210 by 297 mm).
      --letter              Set the paper size to Letter (8.5 by 11 in).
      --margin <dimension>  Set the top, right, bottom and left margins to the same
                            value.
      --header, --no-header
                            Show or hide the header
      --footer, --no-footer
                            Show or hide the footer.

