# -*- coding: utf-8 -*-
import io


class Parser:
    __fi = None
    __mode = "v"

    def __init__(self, file_name, mode):
        # Try to open the file
        try:
            self.__fi = io.open(file_name, 'r', encoding='utf8')
        except IOError:
            print "Could not open file!"
            self.__fi = None
        finally:
            self.__mode = mode

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__fi:
            self.__fi.close()

    def read_one_word(self):
        if self.__fi is None:
            return None
        if self.__mode == "v":
            return self.read_verb()

    def read_verb(self):
        # Verbs need to be in a specific format
        # Format: Each aspect of feature of the verb is on its own line
        # Multiple parts of a feature are delimited by a comma
        # Spaces are not ignored, there should be no spaces around commas and delimiters
        # Things in Parenthesis are descriptions of the feature
        # --
        # Number of Lines for this Verb: 4 + Number of Conjugations + Number of Definitions
        # Primary Type
        # Contract Type
        # (Principal Parts) Present, Future, Aorist, Perfect Active, Perfect MP, Aorist Passive
        # (Infinitives) Each infinitive mood type
        # (The next lines are going to be just conjugations for each tense) Tense, Voice, Mood, 1st Singular,
        # 1st Plural, 2nd Singular, 2nd Plural, 3rd Singular, 3rd Plural
        # (Definitions are the last part of the features. Each on their own line) Definition

        verb = []
        # Read in the number of lines
        num = self.__grab_next_line().split(",")  # Number of Conjugations, Number of Definitions
        verb.append(int(num[0]))  # Temporary integer to hold an ID later on
        # The first three lines are: Primary Type, Contract Type, Principal Parts
        verb.append(self.__grab_next_line())  # Primary Type
        verb.append(self.__grab_next_line())  # Contract Type
        verb.append(self.__grab_next_line().split(","))  # 6 Principal Parts
        verb.append(self.__grab_next_line().split(","))  # Infinitive forms
        conjugations = {}
        for i in range(int(num[0])):
            # List of Tense, Voice, Mood, Conjugations
            conjugation = self.__grab_next_line().split(",")
            # The form is the first three (Tense, Voice, Mood)
            form = (conjugation[0], conjugation[1], conjugation[2])
            # The rest are the conjugations
            conj = [conjugation[3], conjugation[4], conjugation[5], conjugation[6], conjugation[7]]
            conjugations[form] = conj
        verb.append(conjugations)  # All conjugations
        defs = []
        for i in range(int(num[1])):
            defs.append(self.__grab_next_line())  # Definitions
        verb.append(defs)
        return verb

    def read_noun(self):
        # Similar rules used in Verbs
        # Number of Definitions, 5 + Number of Definitions
        # Gender
        # Declension
        # Subgroup
        # (Form) Nominative, Genitive, Article
        # (Singular) N, G, D, A, V
        # (Plural) N, G, D, A, V
        # (Definitions)
        noun = []
        num = int(self.__grab_next_line())
        noun.append(num)
        noun.append(self.__grab_next_line())  # Get Gender
        noun.append(self.__grab_next_line())  # Get Declension Group
        noun.append(self.__grab_next_line())  # Get Subgroup
        noun.append(self.__grab_next_line().split(","))  # Get Face
        sing = self.__grab_next_line().split(",")  # Get Singular Declensions
        plu = self.__grab_next_line().split(",")  # Get Plural Declensions
        noun.append({"Singular": [sing[0], sing[1], sing[2], sing[3], sing[4]],
                     "Plural": [plu[0], plu[1], plu[2], plu[3], plu[4]]})
        defs = []
        for i in range(num):
            defs.append(self.__grab_next_line())  # Get Definition
        noun.append(defs)
        return noun

    def read_adj(self):
        # Almost the same as noun
        # Number of Definitions
        # Declension
        # Type
        # (Face) Masculine, Feminine, Neuter
        # (Singular M)
        # (Plural M)
        # (Singular F)
        # (Plural F)
        # (Singular N)
        # (Plural N)
        # (Definitions)
        adj = []
        num = int(self.__grab_next_line())
        adj.append(num)
        adj.append(self.__grab_next_line())  # Grab Declension
        adj.append(self.__grab_next_line())  # Grab Type
        adj.append(self.__grab_next_line().split(","))  # Grab Face
        for i in range(3): # For Masculine, Feminine, Neuter
            sing = self.__grab_next_line().split(",")  # Get Singular Declensions
            plu = self.__grab_next_line().split(",")  # Get Plural Declensions
            adj.append({"Singular": [sing[0], sing[1], sing[2], sing[3], sing[4]],
                        "Plural": [plu[0], plu[1], plu[2], plu[3], plu[4]]})
        defs = []
        for i in range(num):
            defs.append(self.__grab_next_line())  # Get Definition
        adj.append(defs)
        return adj

    def __grab_next_line(self):
        line = "#"
        # Ignore lines that begin with # (indicates a comment)
        while True:
            line = self.__fi.readline()
            if len(line) == 0: # End of line
                break
            if line[0] != '#': # Not a comment
                break
        return line.rstrip('\n')

