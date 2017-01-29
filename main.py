# -*- coding: UTF-8 -*-
from __future__ import print_function
import DatabaseManager as dB
import TextFileParser as tp
import types
from enum import Enum


def __test__insert_verb(handle):
    handle.insert_verb(0, "Omega", "None",
                        ["παιδεύω", "παιδεύσω", "ἐπαίδευσα",
                         "πεπαίδευκα", "πεπαίδευμαι", "ἐπαιδεύθην"],
                        ["παιδεύειν", "παιδεύεσθαι", "παιδεύσειν", "παιδεύσεσθαι",
                         "παιδεῦσαι", "παιδεύσασθαι", "πεπαιδευκέναι"],
                        {("Present", "Active", "Indicative"):
                            ["παιδεύω", "παιδεύομεν", "παιδεύεις",
                             "παιδεύετε", "παιδεύει", "παιδεύουσι|παιδεύουσιν"],
                         ("Present", "Middle", "Indicative"):
                            ["παιδεύομαι", "παιδευόμεθα", "παιδεύῃ|παιδεύει",
                             "παιδεύεσθε", "παιδεύεται", "παιδεύονται"],
                         ("Present", "Passive", "Indicative"):
                            ["παιδεύομαι", "παιδευόμεθα", "παιδεύῃ|παιδεύει",
                             "παιδεύεσθε", "παιδεύεται", "παιδεύονται"],
                         ("Imperfect", "Active", "Indicative"):
                            ["ἐπαίδευον", "ἐπαιδεύομεν", "ἐπαίδευες",
                             "ἐπαιδεύετε", "ἐπαίδευε|ἐπαίδευεν", "ἐπαίδευον"],
                         ("Imperfect", "Middle", "Indicative"):
                            ["ἐπαιδευόμην", "ἐπαιδευόμεθα", "ἐπαιδεύου",
                             "ἐπαιδεύεσθε", "ἐπαιδεύετο", "ἐπαιδεύοντο"],
                         ("Imperfect", "Passive", "Indicative"):
                            ["ἐπαιδευόμην", "ἐπαιδευόμεθα", "ἐπαιδεύου",
                             "ἐπαιδεύεσθε", "ἐπαιδεύετο", "ἐπαιδεύοντο"],
                         ("Future", "Active", "Indicative"):
                            ["παιδεύσω", "παιδεύσομεν", "παιδεύσεις",
                             "παιδεύσετε", "παιδεύσει", "παιδεύσουσι|παιδεύσουσιν"],
                         ("Future", "Middle", "Indicative"):
                            ["παιδεύσομαι", "παιδευσόμεθα", "παιδεύσῃ|παιδεύσει",
                             "παιδεύσεσθε", "παιδεύσεται", "παιδεύσονται"],
                         ("Aorist", "Active", "Indicative"):
                            ["ἐπαίδευσα", "ἐπαιδεύσαμεν", "ἐπαίδευσας",
                             "ἐπαιδεύσατε", "ἐπαίδευσε|ἐπαίδευσεν", "ἐπαίδευσαν"],
                         ("Aorist", "Middle", "Indicative"):
                            ["ἐπαιδεσάμην", "ἐπαιδευσάμεθα", "ἐπαιδεύσω",
                             "ἐπαιδεύσασθε", "ἐπαιδεύσατο", "ἐπαιδεύσαντο"],
                         ("Perfect", "Active", "Indicative"):
                            ["πεπαίδευκα", "πεπαιδεύκαμεν", "πεπαίδευκας",
                             "πεπαιδεύκατε", "πεπαίδευκε|πεπαίδευκεν", "πεπαιδεύκασι|πεπαιδεύκασιν"],
                         ("Pluperfect", "Active", "Indicative"):
                            ["ἐπεπαιδεύκη", "ἐπεπαιδεύκεμεν", "ἐπεπαιδεύκης",
                             "ἐπεπαιδεύκετε", "ἐπεπαιδεύκει|ἐπεπαιδεύκειν", "ἐπεπαιδεύκεσαν"],
                         ("Present", "Active", "Imperative"):
                            ["", "", "παίδευε",
                             "παιδεύετε", "παιδευέτω", "παιδευόντων"],
                         ("Present", "Middle", "Imperative"):
                            ["", "", "παιδεύου",
                             "παιδεύεσθε", "παιδευέσθω", "παιδευέσθων"],
                         ("Present", "Passive", "Imperative"):
                            ["", "", "παιδεύου",
                             "παιδεύεσθε", "παιδευέσθω", "παιδευέσθων"],
                         ("Aorist", "Active", "Imperative"):
                            ["", "", "παίδευσον",
                             "παιδεύσατε", "παιδευσάτω", "παιδευσάντων"],
                         ("Aorist", "Middle", "Imperative"):
                            ["", "", "παίδευσαι",
                             "παιδεύσασθε", "παιδευσάσθω", "παιδευσάσθων"]},
                        ["teach, educate", "(MIDDLE) have (someone) taught"])


def __test_insert_noun(handle):
    handle.insert_noun(1, "Feminine", "First", "ᾱ, ᾱς",
                       ["θεά", "θεᾶς", "ἡ"],
                       {"Singular":
                        ["θεά", "θεᾶς", "θεᾷ", "θεάν", "θεά"],
                        "Plural":
                        ["θεαί", "θεῶν", "θεαῖς", "θεάς", "θεαί"]},
                       ["goddess"])


def __test_insert_adj(handle):
    handle.insert_adj(2, "First", "ᾱ",
                      ["ἄξιος", "ἀξία", "ἄξιον"],
                      {"Singular":
                       ["ἄξιος", "ἀξίου", "ἀξίῳ", "ἄξιον", "ἄξιε"],
                       "Plural":
                       ["ἄξιοι", "ἀξίων", "ἄξίοις", "ἀξίους", "ἄξιοι"]},
                      {"Singular":
                       ["ἀξία", "ἀξίας", "ἀξίᾳ", "ἀξίαν", "ἀξία"],
                       "Plural":
                       ["ἄξιαι", "ἀξίων", "ἀξίαις", "ἀξίας", "ἄξιαι"]},
                      {"Singular":
                       ["ἄξιον", "ἀξίου", "ἀξίῳ", "ἄξιον", "ἄξιον"],
                       "Plural":
                       ["ἄξια", "ἀξίων", "ἀξίοις", "ἄξια", "ἄξια"]},
                      ["[+GENITIVE or INFINITIVE] worthy (of, to), deserving (of, to)"])


def __test_select_definition(handle, word):
    definitions = handle.query_definition(word)
    definition = [r[0] for r in definitions]
    for i, d in enumerate(definition):
        print (i + 1, ": ", d)


def __test_select_face(handle, word):
    face = handle.query_face(word)
    __test_print(face)


def __test_conjugate(handle, verb, tense):
    result = handle.query_conjugation(verb, tense)
    for row in result:
        print(row[0], ": ", end="")
        for r in row[1:]:
            print(r,end=", ")
        print()


def __test_decline(handle, noun):
    result = handle.query_declension(noun)
    for row in result:
        print(row[0], ": ", end="")
        for r in row[1:]:
            print(r,end=", ")
        print()


def __test_all(handle, pos):
    result = handle.query_all(pos)
    for row in result:
        for r in row:
            print(r, end=", ")
        print()


def __test_print(plist):
    for i in plist:
        if isinstance(i, types.ListType) or isinstance(i, types.DictionaryType) or isinstance(i, types.TupleType):
            __test_print(i)
        print(i, end=",")


# string|string|... denotes alternative forms
# Conjugations with alternate forms: PresAInd 3P, ImpAInd 3S, PresMPInd 2S, FutMInd 2S, FutAInd 3P
# "" indicates nothing
# Enclitic accentuation may change, so keep each possible one as an alternate form

def __run_tests():
    with dB.Handler("GreekLexicon.db") as handler:
        __test__insert_verb(handler)
        #__test_select_face(handler, "παιδεύω")
        #__test_select_definition(handler, "ἐπεπαιδεύκη")
        __test_insert_noun(handler)
        #__test_select_definition(handler, "θεαί")
        __test_insert_adj(handler)
        #__test_select_definition(handler, "ἄξια")
        #__test_select_face(handler, "ἄξια")
        #__test_conjugate(handler,"παιδεύω", ["Perfect", "Active", "Indicative"])
        #__test_decline(handler, "θεά")
        #__test_all(handler,"Verb")


    with tp.Parser("Verbs.txt", "v") as parser:
        verb = parser.read_verb()
        # __test_print(verb)

DEFINE = "define"
'''
CONJUGATE - Gives the conjugation of verb
DECLINE - Gives the declension of noun or adjective or pronoun
INFO - Gives the info for the word: face, etc.
DEFINE - Defines the word
LIST - Gives a list of all words of type
HELP - Gives a list of commands
ADMIN - Sets the mode to Admin
RESET - Resets a Word type (removes all) or all. Requires Admin
UPDATE - Re-updates the database, by removing everything, and re-inserting from files. Requires Admin
INSERT - Inserts a row into a table, manually. Requires Admin
'''

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


