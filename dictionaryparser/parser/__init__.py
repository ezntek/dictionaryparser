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
import sys

from collections import deque
from dataclasses import dataclass
from typing import Literal, NoReturn

POS_TABLE = {
    "n.": "noun",
    "v.": "verb",
    "aff.": "affix",
    "irr.v.": "irregular verb",
    "num.": "number",
    "stv.": "stative_verb",
    "adv.": "adverb",
    "pron.": "pronoun",
    "part.": "particle",
    "conj.": "conjunction",
    "hon.": "honorific",
    "intj.": "interjection",
    "inte.": "interrogative",
    "prep.": "preposition",
    "pos.": "postposition",
    "phr.": "phrase",
    "aux.": "auxiliary",
}

PartOfSpeech = Literal[
    "noun",
    "verb",
    "affix",
    "irregular_verb",
    "stative_verb",
    "adverb",
    "pronoun",
    "particle",
    "conjunction",
    "honorific",
    "interjection",
    "interrogative",
    "preposition",
    "postposition",
    "phrase",
    "auxiliary",
    "number",
]


def _die(*args, **kwargs) -> NoReturn:
    print(file=sys.stderr, *args, **kwargs)
    exit(1)


@dataclass
class Definition:
    word: str

    # pos -> part of speech
    pos: PartOfSpeech
    word_class: Literal["i", "ii", "iii", "na"]  # na → not applicable
    definition: str
    notes: list[str]
    is_derived_term: bool
    parent: str
    irregular_inflections: list[str]

    @staticmethod 
    def from_dict(d: dict) -> "Definition":
        return Definition(d["word"], d["pos"], d["word_class"], d["definition"], d["notes"], d["is_derived_term"], d["parent"], d["irregular_inflections"])

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "pos": self.pos,
            "word_class": self.word_class,
            "definition": self.definition,
            "notes": self.notes,
            "is_derived_term": self.is_derived_term,
            "parent": self.parent,
            "irregular_inflections": self.irregular_inflections
        }

    def pretty_print(self, indents=4):
        INDENT = " " * indents
        print()
        print(f"\033[1m\033[34m{self.word}\033[0m, {self.pos.replace('_', ' ')}{f' \033[1m({self.word_class})\033[0m:' if self.word_class != "" else ''}") 
        print(f"{INDENT}{self.definition}")

        if len(self.notes) != 0:
            print(f"{INDENT}\033[2m{f"\n{INDENT}".join(self.notes)}\033[0m")

        if self.is_derived_term:
            print(f"{INDENT}\033[1mDerived From \033[32m{self.parent}\033[0m")
        if len(self.irregular_inflections) != 0:
            inflections = ", ".join(self.irregular_inflections)
            print(f"{INDENT}\033[1mIrregular Inflections: \033[0m {inflections}")
        

Note = str
Inflection = str
class Parser:
    lines: deque[str]
    len: int

    def __init__(self, file: str) -> None:
        self.lines = deque(file.split("\n"))
        self.len = len(file)

    def next_line(self, line: str) -> Definition | Note | list[Inflection]:
        """Gets the next line in the dictionary, i.e. 1 word-definition pair."""

        is_alt_form = line[0] in [" ", "\t"]

        # Assuming [term] [pos] <class> // definition
        try:
            # left hand side, right hand side
            lhs, rhs = line.split(" // ", maxsplit=1)
        except ValueError:
            line = line.strip()
            
            if "inflections: " in line:
                inflections_s = line[len("inflections: "):]
                inflections = inflections_s.split(", ")
                return inflections
            else:
                return Note(line)

        try:
            lhs = lhs.strip().split(" ")
            term, *rem = lhs
        except ValueError:
            _die(f"could not split LHS: {lhs}")

        definition = rhs
        pos = ""
        wclass = ""
        for elem in rem:  # loop over all remaining elements that are unparsed
            if elem in POS_TABLE:
                pos = elem
            elif elem in ["i.", "ii.", "iii."]:
                wclass = elem

        try:
            pos = POS_TABLE[pos]
        except KeyError:
            _die(f"cannot find POS in table: {line}")

        return Definition(word=term, pos=pos, word_class=wclass, definition=definition, is_derived_term=is_alt_form, notes=[], parent=str(), irregular_inflections=[])  # type: ignore

    def parse(self) -> list[Definition]:
        """Parses the whole dictionary into a `list[Definition]`."""

        res: list[Definition] = []
        while len(self.lines) != 0:
            line = self.lines.popleft()
            if line == "":
                continue

            # Ignore Aa Bb etc

            is_heading = (
                line[0].strip().lower() in "abcdefghijklmnopqrstuvwxyz'ïöäæ"
                and len(line.strip()) <= 4
            )

            if is_heading:
                continue

            next_line = self.next_line(line)

            if isinstance(next_line, Note): 
                prev = res[len(res) - 1]
                prev.notes.append(next_line)
                res[len(res) - 1] = prev
            elif (
                isinstance(next_line, Definition)
                and next_line.is_derived_term == True
            ):
                prev = res[len(res) - 1]
                next_line.parent = prev.word
                res.append(next_line)
            elif (
                isinstance(next_line, list)
            ):
                prev = res[len(res) - 1]
                prev.irregular_inflections = next_line
                res[len(res) - 1] = prev
            else:
                res.append(next_line)
        return res

    def parse_to_dict(self) -> dict:
        """Parses the whole dictionary into a `dict`."""

        res = self.parse()
        d = {
            "items": [itm.to_dict() for itm in res] 
        }
        return d

    def parse_to_json(self, compact=True) -> str:
        """
        Parses the whole dictionary into a `json`. set `compact=False` to
        generate prettier output.
        """

        dic = self.parse_to_dict()
        if compact:
            return json.dumps(dic)
        else:
            return json.dumps(dic, indent=4, sort_keys=False)
