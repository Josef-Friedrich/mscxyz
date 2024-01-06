import textwrap

import click


@click.group(
    chain=True,
)
@click.argument(
    "path",
    nargs=1,
    metavar="PATH",
    type=str,
    # help='Path to a *.msc[zx]" file '
    # 'or a folder which contains "*.msc[zx]" files. In conjunction '
    # 'with the subcommand "help" this positional parameter '
    # "accepts the names of all other subcommands or the word "
    # '"all".',
)
def cli() -> None:
    """
    A command line tool to manipulate the XML based "*.mscX" and "*.mscZ"
    files of the notation software MuseScore.
    """
    pass


@cli.command(
    "meta",
    short_help="Deal with meta data informations stored in the MuseScore file.",
    help=textwrap.dedent(
        """\
    MuseScore can store meta data informations in different places:

    # metatag

    ## XML structure of a meta tag:

        <metaTag name="tag"></metaTag>

    ## All meta tags:

        \b
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

        \b
        <VBox>
          <Text>
            <style>Title</style>
            <text>Some title text</text>
            </Text>

    ## All vbox tags:

        \b
        - Title
        - Subtitle
        - Composer
        - Lyricist

    This command line tool bundles some meta data informations:

    # Combined meta data fields:

        \b
        - title (1. vbox_title 2. metatag_work_title)
        - subtitle (1. vbox_subtitle 2. metatag_movement_title)
        - composer (1. vbox_composer 2. metatag_composer)
        - lyricist (1. vbox_lyricist 2. metatag_lyricist)

    You have access to all this metadata fields through following fields:"""
    ),
)
@click.option(
    "-c",
    "--clean",
    is_flag=True,
    help="Clean the meta data fields. Possible values: „all“ or \
     „field_one,field_two“.",
)
@click.option(
    "-D",
    "--delete-duplicates",
    is_flag=True,
    help="Deletes combined_lyricist if this field is equal to "
    "combined_composer. Deletes combined_subtitle if this field is equal to"
    "combined_title. Move combined_subtitle to combimed_title if "
    "combined_title is empty.",
)
@click.option(
    "-d",
    "--distribute-fields",
    nargs=2,
    type=str,
    metavar="SOURCE_FIELDS FORMAT_STRING",
    help="Distribute source fields to target fields applying a format string "
    "on the source fields. It is possible to apply multiple "
    "--distribute-fields options. SOURCE_FIELDS can be a single field or a "
    "comma separated list of fields: field_one,field_two. The program "
    "tries first to match the FORMAT_STRING on the first source field. If this "
    "fails, it tries the second source field ... an so on.",
)
def meta(
    clean: bool, delete_duplicates: bool, distribute_fields: tuple[str, str]
) -> None:
    click.echo("meta called")


@cli.command("style")
def style() -> None:
    click.echo("style called")
