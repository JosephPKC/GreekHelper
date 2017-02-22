# -*- coding: UTF-8 -*-
from __future__ import print_function
import DatabaseManager as dB
import TextFileParser as tp
import types
from enum import Enum



# string|string|... denotes alternative forms
# Conjugations with alternate forms: PresAInd 3P, ImpAInd 3S, PresMPInd 2S, FutMInd 2S, FutAInd 3P
# "" indicates nothing
# Enclitic accentuation may change, so keep each possible one as an alternate form

def __run_tests():
    with dB.Handler("GreekLexicon.db") as handler:


    with tp.Parser("Verbs.txt", "v") as parser:
        verb = parser.read_verb()
        # __test_print(verb)

DEFINE = "define"

__handler = None


class Error(Enum):
    unknown_command = 0


def get_user_input():
    print(">", end="")
    return raw_input()


def parse_user_input(input):
    ins = input.split()
    # The first argument should be the command ALWAYS
    # The other arguments are arguments to the command
    # If there are more arguments than required, the other arguments are ignored
    execute_command(ins[0], ins[1:])


def execute_command(command, arguments):
    if command.lower() == DEFINE:
        result = define(arguments[0].lower())
        display_definition(arguments[0].lower(), result)
    else:
        error(Error.unknown_command, command, arguments)


def define(word):
    return __handler.query_definition(word)


def display_definition(word, definition):
    if definition is None:
        print("No definition was found for: ", word)
    else:
        print(word)
        for i, d in enumerate(definition):
            print(i + 1, ":", d[0])


def error(code, command, arguments):
    if code == Error.unknown_command:
        print("Unknown command: " + command + ". Type Help for a list of available commands.")
    else:
        print("Unknown error: " + code)

if __name__ == "__main__":
    c = True
    with dB.Handler("GreekLexicon.db") as handler:
        __handler = handler
        while c:
            inp = get_user_input()
            parse_user_input(inp)


