# dictionaryparser

A parser for the Hayalese Dictionary of Modern Rikatisyï.

## note

This project is still WORK IN PROGRESS! It will eventually be able to generate JSON as well. refactoring must also be done.

The CLI is very crude and is poorly documented. Use at your own discretion.

## usage

`/path/to/python -m dictionaryparser parse <--compact> <--output [path]> [FILE PATH]`
`/path/to/python -m dictionaryparser search <--dictionary-path [path]> <--mode [word|definition]> "[TERM]"`

A `dictionary.txt` is supplied in the root directory, a snapshot from the 15th of September (at night)

## guide

To begin, run

`/path/to/python -m dictionaryparser parse dictionary.txt`

to generate the database.

Then, enjoy the options available for the `search` command, and view the output.
