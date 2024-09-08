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
- `-d` - delete (for commands that manipulate messages, but do not delete old versions of them by default)

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