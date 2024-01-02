"""This submodule provides default parameters for args. Here is the
``args`` object stored from ``argparse``. It can be accessed by the other
submodules using the function `get_args()`."""


class DefaultArguments:
    clean_style = None
    export_extension = None
    general_backup = False
    general_colorize = False
    general_config_file = None
    general_dry_run = False
    general_executable = None
    general_glob = "*.mscx"
    general_mscore = False
    general_verbose = 0
    help_markdown = False
    help_rst = False
    lyrics_extract = "all"
    lyrics_fix = False
    lyrics_remap = None
    meta_clean = None
    meta_json = False
    meta_set = None
    meta_sync = False
    path = "."
    rename_alphanum = False
    rename_ascii = False
    rename_format = "$combined_title ($combined_composer)"
    rename_no_whitespace = False
    rename_skip = None
    rename_target = None
    subcommand = None


args = DefaultArguments()


def reset_args() -> DefaultArguments:
    """Reset the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules to import.
    """
    global args
    args = DefaultArguments()
    return args
