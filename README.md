# Useful discord features in a bot
## Motivation
Discord lacks some essential functionality like deleting multiple messages at once, or any other multimessage operations.
With this bot I'm trying to add some of these missing features.
## Functionality
The bot uses classic commands, instead of slash ones, although its prefix is a slash.
Command syntax is:
`/command -[flags] [parameters]`

There are currently 3 commands:
- `delete`
- `reloc`
- `ping`
- `reloc_id`

For more info on the commands, use:
`/help [command]` - for description and parameters description
`/command -h` - for usage and notes about the command
## Flags
All flags are written without spaces or any additional symbols except `-`. Flags can be combined. Unknown flags cause the command to be terminated and an error message is sent.

Supported flags:
- `-h` - help (display help message)
- `-v` - verbose (display additional info and error messages)
- `-s` - silent (do not display any info or error messages)

Valid flag syntaxes:
- `-` - no flags, just a placeholder, which is mandatory
- `-h` - one flag
- `-h-s` - two flags
- `-hs` - also two flags, without a delimiter

## Changelog
1.0 - first version, has reloc from a channel to a thread or from thread to a thread, deleting from both a thread and a channel, ping command for checking whether the bot is working.

1.1 - now you can reloc from a channel to a channel and from a thread to a channel. README.md now has a changelog.

1.2 - added help messages for command parameters. Most of log messages are now stored in json files.

1.3 - added `archive_in` parameter to `reloc` command.

1.4 - added `reloc_id` command, now you can relocate individual messages with ease.

1.5 - added `title` parameter to `reloc` command, now you can either add title with author and filename or do not. This is useful when relocating twice to prevent adding 2 titles.

2.0 - entirely new command syntax.
Now the commands have this syntax:
`/command <params>`
<params>  includes all the mandatory and optional parameters in this
form: `<key>=<value>,<key2>...`
There are escape sequences:
To write a comma as a character you need to escape it     
To use `\,` literally, escape the slash: `\\,`

2.1 - when a command has two dates as arguments, you can now shorten the second one by only entering the part that differs from the first one.

2.2 - removed -d flag as it is reloc-unique parameter, which is 
now passed through delete parameter.