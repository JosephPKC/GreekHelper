import DatabaseManager as dB
import TextFileParser as tp
# from __future__ import print_function
from enum import Enum


class Error(Enum):
    unknown_command = 0


class Command(Enum):
    DEFINE = ["define", "def", "d"]
    FORM = ["form", "fo", "f"]
    LIST = ["list", "li", "l"]
    UPDATE = ["update", "up", "u"]
    HELP = ["help", "h", "?"]
    QUIT = ["quit", "q"]


class LexiconSearcher:
    __lexicon = None
    __name = None

    __FILE_NAME = "Lexicon.txt"

    def __init__(self, database_name):
        self.__name = database_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__lexicon:
            self.__lexicon.__exit__()

    # Run the searcher main loop
    def run_searcher(self):
        with dB.Lexicon(self.__name) as self.__lexicon:
            inp = self.__get_user_input()
            self.parse_user_input(inp)

    def __error(self, e, c, args):
        if e == Error.unknown_command:
            print "Unknown command: ", c, ". Type Help or ? for a list of available commands."
        else:
            print "Unknown error: ", e, "."

    def __get_user_input(self):
        return raw_input(">")

    def __parse_user_input(self, inp):
        ins = inp.split()
        self.__execute_command(ins[0], ins[1:])

    def __execute_command(self, c, args):
        if c.lower() in Command.DEFINE:
            r = self.__define(args[0])
            self.__display_defs(args[0], r)
        else:
            self.__error(Error.unknown_command, c, args)

    def __define(self, w):
        return True

    def __update(self):
        # Create Parser
        with tp.Parser(self.__FILE_NAME) as parser:
            # Reset database
            self.__lexicon.reset()
            c = True
            while c:
                form, words, p = parser.read_one_word()
                if not form and not words:
                    c = False
                else:
                    self.__lexicon.insert(form, p, is_form=True)
                    for w in words:
                        self.__lexicon.insert(w, p, form)

    def __display_defs(self, w, defs):
        if defs is None:
            print "No definitions were found for: ", w, "."
        else:
            print w, ":"
            for i, d in enumerate(defs):
                print i + 1, ": ", d

