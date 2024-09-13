# Useful discord features in a bot
## Motivation
Discord lacks some essential functionality like deleting multiple messages at once, or any other multimessage operations.
With this bot I'm trying to add some of these missing features.
## Functionality
The bot uses classic commands, instead of slash ones, although its prefix is a slash.
Command syntax is:
`/command [parameters]`

There are currently 4 commands:
- `select`
- `delete`
- `reloc`
- `ping`

For more info on the commands, use:
`/help [command]` - for description and parameters description
`/command flags=-h` - for usage and notes about the command
## Flags
All flags are written without spaces or any additional symbols except `-`. Flags can be combined. Unknown flags cause the command to be terminated and an error message is sent.

Supported flags:
- `-h` - help (display help message)
- `-v` - verbose (display additional info and error messages)
- `-s` - silent (do not display any info or error messages)
- `-r` - removes selection for commands that use selected messages 

Valid flag syntaxes:
- `-` - no flags
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

2.3 - as there are more and more commands, commands module now has an `__init__.py` file in which all the commands are imported to be easily exported to main.py. Added new command - `delete_id`"

2.4 - start_date and end_date are now optional parameters for `reloc` command and `delete` command. Now you can select messages from the creation of thread or a channel to the current moment, or just omit just one of them.

2.5 - added `delete_threads` command, which can delete threads with a specific name in a channel. You can also choose, whether to delete the first occurence or all of them. Optimised some of the message operations with lazy evaluation.

3.0 - selection update

    previously, commands selected messages inside them, which required
    different commands for different selector. Now there is a separate
    command /select, which can use 3 different selectors: date, id set
    and regex pattern. If multiple are stated, both filters are applied.

    Deleted commands /reloc_id and /delete_id as they became obsolete
    because the id selector can be used through /select. More than that,
    reloc now does not accept any selectors, now you have to use /select,
    which is more convenient.

    Message selection is done through a file selected-messages.json. In case
    of force termination, it might contain some leftover information about
    selected messages. Make sure to change its contents to {} every time the
    bot is terminated.

3.1 - added `remove` parameter in `/select` command to allow removing certain selector from selection. Now you can first select all the messages from certain time period, for example, then remove specific ids for it - it's one of many possible ways you can use this