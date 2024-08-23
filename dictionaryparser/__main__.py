#
# Dictionary Parser: Parse the Hayalese Dictionary of Modern Rikatisyï.
#
# Copyright (c) Eason Qin, 2024.
#
# This source code form is licensed under the MIT/Expat license. For
# more information, you may visit the OSI website and get the full text
# of the license.
#

import sys
import dictionaryparser as dp

def usage() -> str:
    return f"""\033[1mParser for the Hayalese Dictionary of Modern Rikatisyï.\033[0m

Copyright (c) Eason Qin, 2024. This program is licensed under the MIT/Expat
license without any implied or explicitly stated warranties as this program
is provided AS IS. Go to the OSI website for the full text of the license.

\033[1mUsage:\033[0m {sys.argv[0]} \033[1m[filename]\033[0m
    filename: the path of the plain text file to parse.
"""


def main():
    if len(sys.argv) == 1:
        print(usage())
        return

    fname = sys.argv[1]
    with open(fname, "r+") as file:
        content = file.read()

    d = dp.Parser(content).parse_to_json()
    print(d)


if __name__ == "__main__":
    main()
