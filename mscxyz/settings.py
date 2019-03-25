class DefaultArguments(object):

    clean_style = None
    export_extension = None
    general_backup = False
    general_colorize = False
    general_dry_run = False
    general_glob = '*.mscx'
    general_mscore = False
    general_verbose = 0
    help_markdown = False
    help_rst = False
    lyrics_extract = 'all'
    lyrics_fix = False
    lyrics_remap = None
    meta_clean = None
    meta_json = False
    meta_set = None
    meta_sync = False
    path = '.'
    rename_alphanum = False
    rename_ascii = False
    rename_format = '$combined_title ($combined_composer)'
    rename_no_whitespace = False
    rename_skip = None
    rename_target = None
    subcommand = None


args = DefaultArguments()
