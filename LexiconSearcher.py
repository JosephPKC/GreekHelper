from __future__ import print_function
import DatabaseManager as dB
import TextFileParser as tp

# selfs are of the following form:
# self -(Parameters) (Arguments)

class LexiconSearcher:
    __lexicon = None
    __name = None

    __FILE_NAME = "Lexicon.txt"
    __PARAM_INDICATOR = "-"
    
    UNKNOWN_COMMAND = 0
    BAD_INSERT = 1

    INFO = ["info", "i"]
    LIST = ["list", "li", "l"]
    UPDATE = ["update", "up", "u"]
    HELP = ["help", "h", "?"]
    QUIT = ["quit", "q"]
    
    FORM = ["form", "fo", "f"]
    DEFINE = ["define", "def", "d"]
    UNACCENTED = ["unaccent", "u"]

    def __init__(self, database_name):
        self.__name = database_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__lexicon:
            self.__lexicon.__exit__(exc_type, exc_value, traceback)

    # Run the searcher main loop
    def run_searcher(self):
        with dB.Lexicon(self.__name) as self.__lexicon:
            inp = self.__get_user_input()
            self.__parse_user_input(inp)

    def __get_user_input(self):
        return raw_input("> ")

    def __parse_user_input(self, inp):
        inps = inp.split()
        params, args = self.__get_parameters(inps[1:])
        self.__execute_command(inps[0], params, args)

    def __execute_command(self, cmd, params, args):
        if cmd.lower() in self.INFO:
            print("Info self", end="\n")
            query = self.__info(params, args[0])  # We only require one argument
        elif cmd.lower() in self.LIST:
            print("List self", end="\n")
        elif cmd.lower() in self.UPDATE:
            print("Update self", end="\n")
            self.__update()
        elif cmd.lower() in self.HELP:
            print("Help self", end="\n")
        elif cmd.lower() in self.QUIT:
            print("Quit self", end="\n")
        else:
            self.__error(self.UNKNOWN_COMMAND, cmd, args)

    def __get_parameters(self, args):
        params = []
        index = 0
        for i, a in enumerate(args):
            if a[0] == self.__PARAM_INDICATOR:
                params.append(a)
            else:
                index = i
                break  # Parameters must be before arguments.
        return params, args[index:]

    def __error(self, error_code, cmd, args):
        if error_code == self.UNKNOWN_COMMAND:
            print("Unknown self: " + cmd + ".", end="\n")
        elif error_code == self.BAD_INSERT:
            print("Bad Insert.", end="\n")

    def __info(self, params, word):

        return ""

    def __update(self):
        self.__lexicon.reset()
        with tp.Parser(self.__FILE_NAME) as parser:
            form, words, part, check = parser.read()
            while check:
                res = self.__lexicon.insert(form, part, form, is_form=True)
                if not res:
                    self.__error(self.BAD_INSERT, None, None)
                    break
                res = self.__lexicon.insert(words, part, form, False)
                if not res:
                    self.__error(self.BAD_INSERT, None, None)
                    break

                form, words, part, check = parser.read()

