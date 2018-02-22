Comande line interface
======================

.. code-block:: text


mscxyz
======

.. code-block:: text

  usage: mscx-manager [-h] [-V] [-b] [-g GLOB] [-v]
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
    -g GLOB, --glob GLOB  Handle only files which matches against Unix style
                          glob patterns (e. g. "*.mscx", "* - *"). If you omit
                          this option, the standard glob pattern "*.mscx" is
                          used.
    -v, --verbose         Make commands more verbose. You can specifiy multiple
                          arguments (. g.: -vvv) to make the command more
                          verbose.
  
  Subcommands:
    {clean,meta,lyrics,rename,export,help}
                          Run "subcommand --help" for more informations.
      clean               Clean and reset the formating of the "*.mscx" file
      meta                Synchronize the values of the first vertical frame
                          (title, composer, lyricist) with the corresponding
                          metadata fields.
      lyrics              Extract lyrics. Without any option this subcommand
                          extracts all lyrics verses into separate mscx files.
                          This generated mscx files contain only one verse. The
                          old verse number is appended to the file name, e. g.:
                          score_1.mscx.
      rename              Rename the "*.mscx" files.
      export              Export the scores to PDFs or to the specified
                          extension.
      help                Show help. Use "mscxyz.py help all" to show help
                          messages of all subcommands. Use "mscxyz.py help
                          <subcommand>" to show only help messages for the given
                          subcommand.
  

Subcommands
===========


mscx-manager clean
------------------

.. code-block:: text

  usage: mscx-manager clean [-h] [-s STYLE]
  
  optional arguments:
    -h, --help            show this help message and exit
    -s STYLE, --style STYLE
                          Load a "*.mss" style file and include the contents of
                          this file.
  

mscx-manager meta
-----------------

.. code-block:: text

  usage: mscx-manager meta [-h] [-c] [-j] [-s]
  
  # XML structure of a meta tag:
  
      <metaTag name="tag"></metaTag>
  
  # All meta tags:
  
      - arranger
      - composer
      - copyright
      - creationDate
      - lyricist
      - movementNumber
      - movementTitle
      - originalFormat
      - platform
      - poet
      - source
      - translator
      - workNumber
      - workTitle
  
  # XML structure of a vbox tag:
  
      <VBox>
        <Text>
          <style>Title</style>
          <text>Some title text</text>
          </Text>
  
  # All vbox tags:
  
      - Title
      - Subtitle
      - Composer
      - Lyricis
  
  optional arguments:
    -h, --help   show this help message and exit
    -c, --clean  Clean the meta data.
    -j, --json   Additionally write the meta data to a json file.
    -s, --show   Show all metadata.
  

mscx-manager lyrics
-------------------

.. code-block:: text

  usage: mscx-manager lyrics [-h] [-e EXTRACT] [-r REMAP] [-f]
  
  optional arguments:
    -h, --help            show this help message and exit
    -e EXTRACT, --extract EXTRACT
                          The lyric verse number to extract or "all".
    -r REMAP, --remap REMAP
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

  usage: mscx-manager rename [-h] [-d] [-f FORMAT] [-a] [-n]
  
  Tokens and functions you can use in the format string (-f, --format):
  
  Tokens
  ======
  
  - composer
  - lyricist
  - subtitle
  - title
  
  Functions
  =========
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
  
      left
      ----
  
      %left{text,n}
          Return the first “n” characters of “text”.
  
      lower
      -----
  
      %lower{text}
          Convert “text” to lowercase.
  
      num
      ---
  
      %num{number, count}
          Pad decimal number with leading zeros.
          %num{$track, 3}
  
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
  
      %shorten{text} or %shorten{text, max_size}
          Shorten “text” on word boundarys.
          %shorten{$title, 32}
  
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
    -d, --dry-run         Do not rename the scores
    -f FORMAT, --format FORMAT
                          Format string.
    -a, --ascii           Use only ASCII characters.
    -n, --no-whitespace   Replace all whitespaces with dashes or sometimes
                          underlines.
  

mscx-manager export
-------------------

.. code-block:: text

  usage: mscx-manager export [-h] [-e EXTENSION]
  
  optional arguments:
    -h, --help            show this help message and exit
    -e EXTENSION, --extension EXTENSION
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
  
