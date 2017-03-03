from __future__ import print_function
import DatabaseManager as dB
import TextFileParser as tp
import Utils
from enum import Enum

# selfs are of the following form:
# self -(Parameters) (Arguments)


class Command(Enum):
    """
    Enumeration Class for Commands
    Values are lists of applicable user inputs
    """
    INFO = ["info", "i"]            # Search for the word, and display info.
    LIST = ["list", "li", "l"]      # List all words of a particular type.
    UPDATE = ["update", "up", "u"]  # Update the database from the text file.
    HELP = ["help", "h", "?"]       # List Commands and their Parameters.
    QUIT = ["quit", "q"]            # Quit the program.


class Parameter(Enum):
    """
    Enumeration Class for Parameters
    Values are lists of applicable user inputs
    """
    # Use with INFO Command. Default: Lists the basic form info.
    VERBOSE = ["verbose", "v"]          # Lists the full form info of the word.
    DEFINE = ["define", "def", "d"]     # Lists the definition of the word.
    UNACCENTED = ["unaccent", "u"]      # Ignore the accents on the input word.


class LexiconSearcher:
    """
    Lexicon Searcher is a class that runs the user interface to the database.
    """
    __lexicon = None                # Lexicon: Database Handler
    __name = None                   # Name: Name of the Database
    __FILE_NAME = "Lexicon.txt"     # File Name: Name of the Text File
    __PARAM_INDICATOR = "-"         # Parameter Indicator: A symbol to indicate that something is a parameter

    # Core Methods
    def __init__(self, database_name):
        """
        Constructor for Lexicon Searcher
        :param database_name: Name of the database to connect to
        :return: None
        """
        self.__name = database_name

    # Used with With:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__lexicon:
            self.__lexicon.__exit__(exc_type, exc_value, traceback)

    # Main Loop Method
    def run_searcher(self):
        """
        Runs the Searcher's main loop
        :return: None
        """
        # Connect to the database, and create a handler
        with dB.Lexicon(self.__name) as self.__lexicon:
            q = False
            while not q:
                # Poll for user input, and get it
                inp = self.__get_user_input()
                # Parse user input, and execute any commands in it
                cmd, params, args = self.__parse_user_input(inp)
                # Executes the command with the parameters and arguments
                res = self.__execute_command(cmd, params, args)
                if res.value > 0:
                    self.__error(res, cmd, params, args)
                elif res.value == -1:
                    q = True

    # Private Methods, Helper Methods
    # Get User Input
    def __get_user_input(self):
        """
        Gets user input
        :return: User's input
        """
        return raw_input("> ")

    # Parse User Input
    def __parse_user_input(self, inp):
        """
        Parses user input, and tries to execute the command
        :param inp: User Input
        :return: None
        """
        inps = inp.split()  # Split the user input on whitespace
        # FORMAT: User input should be: Command (Parameters) (Arguments)
        params, args = self.__get_parameters(inps[1:])  # Split as Parameters and Arguments
        return inps[0], params, args


    # Execute the command
    def __execute_command(self, cmd, params, args):
        """
        Executes the given command, with the parameters and arguments
        If the command takes no or less parameters and arguments given,
        then it will only look at the first few, and ignore the extra.
        :param cmd: Given command
        :param params: Given parameters
        :param args: Given arguments
        :return: None
        """
        # Switch to check what the command is
        # If the command is INFO
        if cmd.lower() in Command.INFO.value:
            if len(args) != 1:
                return Utils.Error.BAD_ARGS
            # INFO only requires a single argument, so get the first one
            info, form, defs, check = self.__info(params, args[0])
            if check != Utils.Error.SUCCESS:
                return check
            self.__display(info, form, defs)
        # If the command is LIST
        elif cmd.lower() in Command.LIST.value:
            print("List self", end="\n")
        # If the command is UPDATE
        elif cmd.lower() in Command.UPDATE.value:
            # Update takes no parameters and no arguments, so ignore them all
            res = self.__update()
            if res != Utils.Error.SUCCESS:
                return res
        # If the command is HELP
        elif cmd.lower() in Command.HELP.value:
            print("Help self", end="\n")
        # If the command is QUIT
        elif cmd.lower() in Command.QUIT.value:
            print("Quit self", end="\n")
            return Utils.Error.QUIT
        # If the command is not recognized (Not in the command class)
        else:
            # Unknown Command Error
            return Utils.Error.UNKNOWN_COMMAND
        return Utils.Error.SUCCESS

    # Separate the Parameters from Arguments
    def __get_parameters(self, args):
        """
        Splits the input into parameters and arguments
        :param args: the arguments input
        :return: parameters, arguments
        """
        params = []
        index = 0
        # Enumerate through the arguments list
        for i, a in enumerate(args):
            if a[0] == self.__PARAM_INDICATOR:  # If we find the Parameter Indicator, it is a parameter
                params.append(a)
            else:  # If we find an argument, there should be no more parameters
                index = i
                break  # Parameters must be before arguments. Ignore any parameters after arguments
        return params, args[index:]

    # Error method for displaying error messages
    def __error(self, error_code, cmd, params, args):
        """
        Displays a relevant error message
        :param error_code: Error Code
        :param cmd: Command
        :param params: Parameters
        :param args: Arguments
        :return: None
        """
        # Unknown Command Error
        if error_code == Utils.Error.UNKNOWN_COMMAND:
            print("Unknown Command: " + cmd + ".", end="\n")
        # Bad Insert Error
        elif error_code == Utils.Error.BAD_INSERT:
            print("Bad Insert.", end="\n")

    # Searches the Database for the word, and returns the info
    def __info(self, params, word):
        """
        Gets the info for the word
        :param params: Any parameters to modify how to get info
        :param word: The word to search for
        :return: The info string
        """
        # Look through the params for the INFO parameters
        verbose = False; define = False; unaccent = False;
        for p in params:
            if p[1:] in Parameter.VERBOSE.value:
                verbose = True
            elif p[1:] in Parameter.DEFINE.value:
                define = True
            elif p[1:] in Parameter.UNACCENTED.value:
                unaccent = True
            else:
                return None, None, None, Utils.Error.UNKNOWN_PARAMETER
        i, f, d = self.__lexicon.select(word, verbose, define, unaccent)
        check = True
        if i is None:
            check = False
        elif verbose and f is None:
            check = False
        elif define and d is None:
            check = False
        return i, f, d, Utils.Error.SUCCESS if check else Utils.Error.WORD_NOT_FOUND

    # Updates the database
    def __update(self):
        """
        Updates the database by deleting all info, and then inserting every word from the text file
        :return: None
        """
        self.__lexicon.reset()  # Reset the database
        # Create a Text File Parser
        with tp.Parser(self.__FILE_NAME) as parser:
            # Read in an entire word
            form, words, part, check = parser.read()
            while check:  # Did it successfully read in an entire word?
                # Try to insert that word form into the database
                res = self.__lexicon.insert(part, form=form)
                if not res:  # If fail, error: BAD INSERT
                    return Utils.Error.BAD_INSERT
                # Try to insert the word into the database
                res = self.__lexicon.insert(part, words, form)
                if not res:  # Again, if fail, error: BAD INSERT
                    return Utils.Error.BAD_INSERT

                form, words, part, check = parser.read()  # Read in the next word
        return Utils.Error.SUCCESS

    def __display(self, info, form, defs):
        # For now, just display everything
        for i in info:
            print(i, end=", ")
        print(end="\n")
        if form is not None:
            for f in form:
                print(f, end=", ")
            print(end="\n")
        if defs is not None:
            for d in defs:
                print(d, end=", ")
            print(end="\n")
