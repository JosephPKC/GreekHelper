# -*- coding: utf-8 -*-
import io
import Utils

class Parser:
    __fi = None

    def __init__(self, file_name):
        # Try to open the file
        try:
            self.__fi = io.open(file_name, 'r', encoding='utf8')
        except IOError:
            print "Could not open file!"
            self.__fi = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__fi:
            self.__fi.close()

    def read_one_word(self):
        # Ignore lines that begin with # -- comments
        # Ignore empty lines
        # Form of the word --denotes what part of speech it is

        mode, n, w, c = self.__read_mode()
        if self.__fi is None:
            return None
        elif mode == Utils.PartOfSpeech.VERB:
            return self.__read_verb(n, w, c), mode
        elif mode == Utils.PartOfSpeech.NOUN:
            return self.__read_noun(n, w, c), mode
        elif mode == Utils.PartOfSpeech.ADJECTIVE:
            return self.__read_adj(n, w, c), mode
        elif mode == Utils.PartOfSpeech.PRONOUN:
            return self.__read_pro(n, w, c), mode
        elif mode == Utils.PartOfSpeech.PARTICIPLE:
            return self.__read_part(w), mode
        else:
            return self.__read_misc(n, w, c, mode), mode

    def __read_mode(self):
        # Read in the first line --
        # Part of Speech, N, W, C
        line = self.__get_line(',')
        return line[0], line[1], line[2], line[3]

    def __read_verb(self, n, w, c):
        # Format:
        # Verb Form should come first
        # Principal Parts, delimited by , (There should be 6 parts)
        # Types, delimited by , (Ending, Aorist, Perfect, Irr)
        # N lines of definitions (takes the entire string, except the terminating carriage return)
        # Each Verb that follows the preceding form comes next (W of them)
        # Word String -- The actual word
        # Form Info delimited by , --Person (1, 2, 3, -) Number (S, D, P, -)
        # Tense (Present, Future, Imperfect, Aorist, Perfect, Pluperfect, Future Perfect)
        # Voice (Active, Middle, Passive),
        # Mood (Infinitive, Indicative, Imperative, Subjunctive, Optative, Participle)
        form = [c]
        words = {}
        # Read in Form
        # Read in Six Principal Parts
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Types
        self.__load_types(form)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(w, words)

        return form, words

    def __read_noun(self, n, w, c):
        # Format:
        # Noun Form should come first
        # Nominative, Genitive, Article -- Form
        # Major, Minor, Gender, 0/1 for Irregularity
        # N lines of definitions
        # (W Noun Words)
        # Word String
        # Case, Number, Gender
        form = [c]
        words = {}
        # Read in Form
        # Read in N, G, A
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for f in line:
            form.append(f)

        # Read in Types
        self.__load_types(form)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(w, words)

        return form, words

    def __read_adj(self, n, w, c):
        # N -- number of definitions, W
        # ADJ
        # Masculine, Feminine or -, Neuter
        # Major, Minor, 0/1 Irregularity
        # N definitions
        # W words
        # Word String
        # Case, Number, Gender
        form = [c]
        words = {}
        # Read in Form
        # Read in M, F, N
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Types
        self.__load_types(form)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(w, words)

        return form, words

    def __read_pro(self, n, w, c):
        # Masculine, Feminine, Neuter
        # Person, Type
        # N definitions
        # W words
        # Word String
        # Case, Number, Gender, Person
        form = [c]
        words = {}
        # Read in Form
        # Read in M, F, N
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Types
        self.__load_types(form)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(w, words)

        return form, words

    def __read_part(self, w):
        # Six Principal Parts
        # W
        # Word String
        # Case, Number, Gender, Tense, Voice
        form = []
        words = {}
        # Read in Form
        # Read in M, F, N
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Words
        self.__load_words(w, words)

        return form, words

    def __read_misc(self, n, w, c, p):
        # W are alternate forms
        # N Definitions
        # W Word String
        form = [c]
        words = {}
        # Read in Form
        # Read in Primary Word String
        line = self.__get_line()
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(w, words)

        return form, words

    def __get_line(self, d=None):
        line = "#"
        # Ignore lines that begin with # (indicates a comment)
        # Ignore empty lines
        while True:
            line = self.__fi.readline()
            if len(line) == 0:  # End of file?
                break
            if line[0] != '#':  # Not a comment
                break
        if d is None:
            return line.rstrip('\n')
        else:
            return line.rstrip('\n').split(d)

    def __load_defs(self, n, f):
        for i in range(n):
            line = self.__get_line()
            if len(line) == 0:
                return False
            f.append(line)

    def __load_words(self, w, f):
        for i in range(w):
            wo = self.__get_line()
            if len(wo) == 0:
                return False
            line = self.__get_line(",")
            if len(line) == 0:
                return False
            f[wo] = line

    def __load_types(self, f):
        line = self.__get_line(",")
        if len(line) == 0:
            return False
        for t in line:
            f.append(t)

'''
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
'''
