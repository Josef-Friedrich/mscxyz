#compdef musescore-manager

# AUTOMATICALLY GENERATED by `shtab`


_shtab_musescore_manager_commands() {
  local _commands=(
    
  )
  _describe 'musescore-manager commands' _commands
}

_shtab_musescore_manager_options=(
  "(- : *)"{-h,--help}"[show this help message and exit]"
  "(- : *)--print-completion[print shell completion script]:print_completion:(bash zsh tcsh)"
  "(- : *)"{-V,--version}"[show program\'s version number and exit]"
  {-b,--backup}"[Create a backup file.]"
  {-k,--colorize}"[Colorize the command line print statements.]"
  {-C,--config-file}"[Specify a configuration file in the INI format.]:general_config_file:_files"
  {-d,--dry-run}"[Simulate the actions.]"
  {-m,--mscore}"[Open and save the XML file in MuseScore after manipulating the XML with lxml to avoid differences in the XML structure.]"
  "--diff[Show a diff of the XML file before and after the manipulation.]"
  {-e,--executable}"[Path of the musescore executable.]:general_executable:_files"
  "*"{-v,--verbose}"[Make commands more verbose. You can specifiy multiple arguments (. g.\: -vvv) to make the command more verbose.]"
  {-E,--export}"[Export the scores in a format defined by the extension. The exported file has the same path, only the file extension is different. Further information can be found at the MuseScore website\: https\:\/\/musescore.org\/en\/handbook\/2\/file-formats, https\:\/\/musescore.org\/en\/handbook\/3\/file-export, https\:\/\/musescore.org\/en\/handbook\/4\/file-export. MuseScore must be installed and the script must know the location of the binary file.]:export_extension:(mscz mscx spos mpos pdf svg png wav mp3 ogg flac mid midi kar musicxml xml mxl brf mei)"
  {-c,--clean}"[Clean the meta data fields. Possible values\: \„all\“ or \„field_one,field_two\“.]:meta_clean:"
  {-D,--delete-duplicates}"[Deletes combined_lyricist if this field is equal to combined_composer. Deletes combined_subtitle if this field is equal tocombined_title. Move combined_subtitle to combimed_title if combined_title is empty.]"
  "*"{-i,--distribute-fields}"[Distribute source fields to target fields applying a format string on the source fields. It is possible to apply multiple --distribute-fields options. SOURCE_FIELDS can be a single field or a comma separated list of fields\: field_one,field_two. The program tries first to match the FORMAT_STRING on the first source field. If thisfails, it tries the second source field ... an so on.]:meta_dist:"
  {-j,--json}"[Additionally write the meta data to a json file.]"
  {-l,--log}"[Write one line per file to a text file. e. g. --log \/tmp\/musescore-manager.log \'\$title \$composer\']:meta_log:"
  {-y,--synchronize}"[Synchronize the values of the first vertical frame (vbox) (title, subtitle, composer, lyricist) with the corresponding metadata fields]"
  "*"{-S,--set-field}"[Set value to meta data fields.]:meta_set:"
  {-x,--extract,--extract-lyrics}"[Extract each lyrics verse into a separate MuseScore file. Specify \”all\” to extract all lyrics verses. The old verse number is appended to the file name, e. g.\: score_1.mscx.]:lyrics_extract:"
  {-r,--remap,--remap-lyrics}"[Remap lyrics. Example\: \"--remap 3\:2,5\:3\". This example remaps lyrics verse 3 to verse 2 and verse 5 to 3. Use commas to specify multiple remap pairs. One remap pair is separated by a colon in this form\: \"old\:new\"\: \"old\" stands for the old verse number. \"new\" stands for the new verse number.]:lyrics_remap:"
  {-F,--fix,--fix-lyrics}"[Fix lyrics\: Convert trailing hyphens (\"la- la- la\") to a correct hyphenation (\"la - la - la\")]"
  {-f,--format}"[Format string.]:rename_format:"
  {-A,--alphanum}"[Use only alphanumeric characters.]"
  {-a,--ascii}"[Use only ASCII characters.]"
  {-n,--no-whitespace}"[Replace all whitespaces with dashes or sometimes underlines.]"
  {-K,--skip-if-empty}"[Skip rename action if FIELDS are empty. Separate FIELDS using commas\: combined_composer,combined_title]:rename_skip:"
  {-t,--target}"[Target directory]:rename_target:"
  {-L,--list-files}"[Only list files and do nothing else.]"
  {-g,--glob}"[Handle only files which matches against Unix style glob patterns (e. g. \"\*.mscx\", \"\* - \*\"). If you omit this option, the standard glob pattern \"\*.msc\[xz\]\" is used.]:selection_glob:"
  "--mscz[Take only \"\*.mscz\" files into account.]"
  "--mscx[Take only \"\*.mscx\" files into account.]"
  "*"{-s,--style}"[Set a single style value. For example\: --style pageWidth 8.5]:style_value:"
  {-Y,--style-file}"[Load a \"\*.mss\" style file and include the contents of this file.]:style_file:_files"
  {--s3,--styles-v3}"[List all possible version 3 styles.]"
  {--s4,--styles-v4}"[List all possible version 4 styles.]"
  "--list-fonts[List all font related styles.]"
  "--text-font[Set nearly all fonts except \“romanNumeralFontFace\”, \“figuredBassFontFace\”, \“dynamicsFontFace\“, \“musicalSymbolFont\” and \“musicalTextFont\”.]:style_text_font:"
  "--title-font[Set \“titleFontFace\” and \“subTitleFontFace\”.]:style_title_font:"
  "--musical-symbol-font[Set \“musicalSymbolFont\”, \“dynamicsFont\” and  \“dynamicsFontFace\”.]:style_musical_symbol_font:"
  "--musical-text-font[Set \“musicalTextFont\”.]:style_musical_text_font:"
  "--staff-space[Set the staff space or spatium. This is the vertical distance between two lines of a music staff.]:style_staff_space:"
  "--page-size[Set the page size.]:style_page_size:"
  "--margin[Set the top, right, bottom and left margin to the same value.]:style_margin:"
  "(*)::Path to a \"\*.msc\[zx\]\" file or a folder containing \"\*.msc\[zx\]\" files. can be specified several times.:_files"
)


_shtab_musescore_manager() {
  local context state line curcontext="$curcontext" one_or_more='(-)*' remainder='(*)'

  if ((${_shtab_musescore_manager_options[(I)${(q)one_or_more}*]} + ${_shtab_musescore_manager_options[(I)${(q)remainder}*]} == 0)); then  # noqa: E501
    _shtab_musescore_manager_options+=(': :_shtab_musescore_manager_commands' '*::: :->musescore-manager')
  fi
  _arguments -C -s $_shtab_musescore_manager_options

  case $state in
    musescore-manager)
      words=($line[1] "${words[@]}")
      (( CURRENT += 1 ))
      curcontext="${curcontext%:*:*}:_shtab_musescore_manager-$line[1]:"
      case $line[1] in
        
      esac
  esac
}



typeset -A opt_args
_shtab_musescore_manager "$@"
