import DatabaseManager as dB
import TextFileParser as tp
# from __future__ import print_function
from enum import Enum


class Error(Enum):
    unknown_command = 0


class LexiconSearcher:
    __lexicon = None

    def __init__(self, database_name):
        self.__lexicon = dB.Lexicon(database_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__lexicon:
            self.__lexicon.__exit__()

    # Run the searcher main loop
    def run_searcher(self):


    def get_user_input(self):
        return raw_input(">")
