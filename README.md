help!
```
usage: mscxyz.py [-h] [-b] [-g GLOB] [-p PICK] [-c CYCLE_LENGTH] [-v]
                 {clean,meta,lyrics,rename,export,help} ... path

A command line tool to manipulate the XML based *.mscX and *.mscZ files of the
notation software MuseScore.

positional arguments:
  path                  Path to a *.mscx file or a folder which contains
                        *.mscx files.

optional arguments:
  -h, --help            show this help message and exit
  -b, --backup          Create a backup file.
  -g GLOB, --glob GLOB  Handle only files which matches against Unix style
                        glob patterns (e. g. "*.mscx", "* - *"). If you omit
                        this option, the standard glob pattern "*.mscx" is
                        used.
  -p PICK, --pick PICK  The --pick option can be used to run multiple
                        mscxyz.py commands in parallel on multiple consoles.
                        If you like so, using this option a "poor man's
                        multithreading" can be accomplished. Multicore CPUs
                        can be used to full capacity. By default every fourth
                        file gets picked up. The option "-p N" begins the
                        picking on the Nth file of a cycle. The corresponding
                        option is named "-c" or "--cycle-length".
  -c CYCLE_LENGTH, --cycle-length CYCLE_LENGTH
                        This option specifies the distance between the picked
                        files. The option "-c N" picks every Nth file. The
                        corresponding options is named "-p" or "--pick".
  -v, --verbose         Make commands more verbose. You can specifiy multiple
                        arguments (. g.: -vvv) to make the command more
                        verbose.

Subcommands:
  {clean,meta,lyrics,rename,export,help}
                        Run "subcommand --help" for more informations.
    clean               Clean and reset the formating of the *.mscx file
    meta                Synchronize the values of the first vertical frame
                        (title, composer, lyricist) with the corresponding
                        metadata fields.
    lyrics              Extract lyrics.
    rename              Rename the *.mscx files.
    export              Export the scores to PDFs or to the specified
                        extension.
    help                Show help
```

# mscxyz.py rename

```
usage: mscxyz.py rename [-h] [-d] [-f FORMAT] [-a]

optional arguments:
  -h, --help            show this help message and exit
  -d, --dry-run         Do not rename the scores
  -f FORMAT, --format FORMAT
                        Format string: possible placeholders are %title%
  -a, --ascii           Use only ASCII characters.
```

# mscxyz.py help

```
usage: mscxyz.py help [-h] [-m]

optional arguments:
  -h, --help      show this help message and exit
  -m, --markdown  Show help in markdown format.
```

# mscxyz.py lyrics

```
usage: mscxyz.py lyrics [-h] [-n NUMBER]

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        Number of lyric verses.
```

# mscxyz.py meta

```
usage: mscxyz.py meta [-h] [-j] [-s]

optional arguments:
  -h, --help  show this help message and exit
  -j, --json  Additionally write the metadata to a json file.
  -s, --show  Show all metadata.
```

# mscxyz.py export

```
usage: mscxyz.py export [-h] [-e EXTENSION]

optional arguments:
  -h, --help            show this help message and exit
  -e EXTENSION, --extension EXTENSION
                        Extension to export
```

# mscxyz.py clean

```
usage: mscxyz.py clean [-h] [-s STYLE]

optional arguments:
  -h, --help            show this help message and exit
  -s STYLE, --style STYLE
                        Load a *.mss style file and include the contents of
                        this file.
```
