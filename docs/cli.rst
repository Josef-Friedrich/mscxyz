**********************
Comande line interface
**********************

:: 

    usage: musescore-manager [-h] [--print-completion {bash,zsh,tcsh}]
                             [-C <file-path>] [-b] [-d] [--catch-errors] [-m]
                             [-e FILE_PATH] [-E <extension>] [--compress] [-V] [-v]
                             [-k | --color | --no-color] [--diff] [--print-xml]
                             [-c <fields>] [-D] [-i <source-fields> <format-string>]
                             [-j] [-l <log-file> <format-string>] [-y]
                             [-S <field> <format-string>]
                             [--metatag <field> <value>] [--vbox <field> <value>]
                             [--title <string>] [--subtitle <string>]
                             [--composer <string>] [--lyricist <string>]
                             [-x <number-or-all>] [-r <remap-pairs>] [-F]
                             [--rename <path-template>]
                             [-t <directory> | --only-filename] [-A] [-a] [-n]
                             [-K <fields>] [-L]
                             [-g <glob-pattern> | --mscz | --mscx]
                             [-s <style-name> <value>] [--clean] [-Y <file>] [--s3]
                             [--s4] [--reset-small-staffs] [--list-fonts]
                             [--text-font <font-face>] [--title-font <font-face>]
                             [--musical-symbol-font <font-face>]
                             [--musical-text-font <font-face>]
                             [--staff-space <dimension>]
                             [--page-size <width> <height>] [--a4] [--letter]
                             [--margin <dimension>]
                             [--show-header | --no-show-header]
                             [--header-first-page | --no-header-first-page]
                             [--different-odd-even-header | --no-different-odd-even-header]
                             [--header <left> <center> <right>]
                             [--header-odd-even <odd-left> <even-left> <odd-center> <even-center> <odd-right> <even-right>]
                             [--show-footer | --no-show-footer]
                             [--footer-first-page | --no-footer-first-page]
                             [--different-odd-even-footer | --no-different-odd-even-footer]
                             [--footer <left> <center> <right>]
                             [--footer-odd-even <odd-left> <even-left> <odd-center> <even-center> <odd-right> <even-right>]
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

    info:
      Print informations about the score and the CLI interface itself.

      -V, --version         show program's version number and exit
      -v, --verbose         Make commands more verbose. You can specifiy multiple
                            arguments (. g.: -vvv) to make the command more verbose.
      -k, --color, --no-color
                            Colorize the command line print statements. (default: True)
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
      --musical-symbol-font <font-face>
                            Set “musicalSymbolFont”, “dynamicsFont” and
                            “dynamicsFontFace”.
      --musical-text-font <font-face>
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

