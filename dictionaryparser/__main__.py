#
# Dictionary Parser: Parse the Hayalese Dictionary of Modern Rikatisyï.
#
# Copyright (c) Eason Qin, 2024.
#
# This source code form is licensed under the MIT/Expat license. For
# more information, you may visit the OSI website and get the full text
# of the license.
#

import json
from typing import NoReturn
import sys
from dictionaryparser.dictionary import Dictionary
import dictionaryparser.parser as dp
import typer

app = typer.Typer()

def _die(*args, **kwargs) -> NoReturn:
    print(file=sys.stderr, *args, **kwargs)
    exit(1)

@app.command()
def parse(file_path: str, compact: bool = False, output: str = "./dictionary.json"):
    try:
        with open(file_path, "r+") as fp:
            content = fp.read()
    except FileNotFoundError:
        _die(f"{file_path} not found!")
                
    parser = dp.Parser(content)
    res = parser.parse_to_json(compact=compact)
    
    match output:
        case "stdout":
            print(res)
        case "stderr":
            print(res, file=sys.stderr)
        case _:
            try:
                with open(output, "w") as fp:
                    fp.write(res)
            except FileNotFoundError:
                _die(f"{output} not found!")

@app.command()
def search(term: str, dictionary_path: str = "./dictionary.json", mode: str = "word"): # "word" or "definition"
    try:
        with open(dictionary_path, "r") as fp:
            dic = json.load(fp)
    except FileNotFoundError:
        _die(f"{dictionary_path} not found!")

    definitions = [dp.Definition.from_dict(itm) for itm in dic["items"]]
    dictionary = Dictionary(definitions)

    match mode.strip().lower():
        case "word":
            results = dictionary.search_word(term) 
        case "definition":
            results = dictionary.search_definition(term)
        case _:
            _die("invalid mode!")

    for result in results:
        result.pretty_print()

def usage() -> str:
    return f"""\033[1mParser for the Hayalese Dictionary of Modern Rikatisyï.\033[0m

Copyright (c) Eason Qin, 2024. This program is licensed under the MIT/Expat
license without any implied or explicitly stated warranties as this program
is provided AS IS. Go to the OSI website for the full text of the license.

\033[1mUsage:\033[0m {sys.argv[0]} \033[1m[filename]\033[0m
    filename: the path of the plain text file to parse.
"""


def main():
    app()

if __name__ == "__main__":
    main()
