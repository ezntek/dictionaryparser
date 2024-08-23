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


def die(*args, **kwargs) -> NoReturn:
    print(file=sys.stderr, *args, **kwargs)
    exit(1)


@dataclass
class Definition:
    # definitions that are alternate forms of a previous definition have this set to true
    is_alternate_form: bool
    word: str

    # pos -> part of speech
    pos: PartOfSpeech
    word_class: Literal["i", "ii", "iii", "na"]  # na → not applicable
    definition: str
    notes: list[str]
    alternate_forms: list["Definition"]

    def to_dict(self) -> dict:
        return {
            "is_alternate_form": self.is_alternate_form,
            "word": self.word,
            "pos": self.pos,
            "word_class": self.word_class,
            "definition": self.definition,
            "notes": self.notes,
            "alternate_forms": [aform.to_dict() for aform in self.alternate_forms]
        }

Note = str
class Parser:
    lines: deque[str]
    len: int

    def __init__(self, file: str) -> None:
        self.lines = deque(file.split("\n"))
        self.len = len(file)

    def next_line(self, line: str) -> Definition | Note:
        """Gets the next line in the dictionary, i.e. 1 word-definition pair."""

        is_alt_form = line[0] in [" ", "\t"]

        # Assuming [term] [pos] <class> // definition
        try:
            # left hand side, right hand side
            lhs, rhs = line.split(" // ", maxsplit=1)
        except ValueError:
            line = line.strip()
            return line

        try:
            lhs = lhs.strip().split(" ")
            term, *rem = lhs
        except ValueError:
            die(f"could not split LHS: {lhs}")

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
            die(f"cannot find POS in table: {line}")

        return Definition(word=term, pos=pos, word_class=wclass, definition=definition, is_alternate_form=is_alt_form, notes=[], alternate_forms=[])  # type: ignore

    def parse(self) -> list[Definition]:
        res: list[Definition] = []
        while len(self.lines) != 0:
            line = self.lines.popleft()
            if line == "":
                continue

            # Ignore Aa Bb etc
            if (
                line[0].strip().lower() in "abcdefghijklmnopqrstuvwxyz'ïö"
                and len(line.strip()) < 4
            ):
                continue

            next_line = self.next_line(line)

            if isinstance(next_line, Note):
                prev = res[len(res) - 1]
                prev.notes.append(next_line)
                res[len(res) - 1] = prev
            elif (
                isinstance(next_line, Definition)
                and next_line.is_alternate_form == True
            ):
                prev = res[len(res) - 1]
                prev.alternate_forms.append(next_line)
                res[len(res) - 1] = prev
            else:
                res.append(next_line)
        return res

    def parse_to_dict(self) -> dict:
        res = self.parse()
        d = {
            "items": [itm.to_dict() for itm in res] 
        }
        return d

    def parse_to_json(self) -> str:
        return json.dumps(self.parse_to_dict())
