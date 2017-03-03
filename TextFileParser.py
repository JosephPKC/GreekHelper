# -*- coding: utf-8 -*-
import io       # For file operations
import Utils    # For the Part of Speech
from collections import defaultdict


class Parser:
    """
    Parser class will parse in a text file and create usable words for inserting into the database
    """
    __fi = None     # File: File IO

    # Constructor
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

    # Core Method
    # Read in an entire word
    def read(self):
        """
        Try to read an entire word from the text file
        :return: The entire word tuple: Form, Individual Words, Part of Speech, Success
        """
        w, mode = self.__read_one_word()  # Helper method to read in a word
        if w is None or mode is None:
            return None, None, None, False
        form = w[0]  # The form is the first of w pair
        if len(w) == 2:
            words = w[1]  # If there is another, the words is the second
        else:
            words = None  # Else, there are no Words
        return form, words, mode, True  # Return the successfully read in word

    # Helper Methods
    # Helper method for readin in a word
    def __read_one_word(self):
        """
        Reads in an entire word
        :return: The word (form, words), and the Part
        """
        if self.__fi is None:  # If there is no file, then fail
            return None, None

        # Read in the first line, which contains Part, Num of Defs, Chapter
        mode, n, c = self.__read_mode()
        # If any of them failed to load in, then fail
        if mode is None or n is None or c is None:
            return None, None
        n = int(n)  # Change n to integer (because it is read as a string)

        # Switch depending on the Part
        # If Verb
        if mode == Utils.PartOfSpeech.VERB.value:
            return self.__read_verb(n, c), mode
        # If Noun
        elif mode == Utils.PartOfSpeech.NOUN.value:
            return self.__read_noun(n, c), mode
        # If Adjective
        elif mode == Utils.PartOfSpeech.ADJECTIVE.value:
            return self.__read_adj(n, c), mode
        # If Pronoun
        elif mode == Utils.PartOfSpeech.PRONOUN.value:
            return self.__read_pro(n, c), mode
        # If Participle
        elif mode == Utils.PartOfSpeech.PARTICIPLE.value:
            return self.__read_part(), mode
        # If Adverb, Conjunction, Interjection, Correlative, Particle, or Preposition
        else:
            return self.__read_misc(n, c), mode

    # Read in the first line, or the mode
    def __read_mode(self):
        """
        Reads in the Part, Number of Defs, and Chapter
        :return: Part, Number of Defs, Chapter
        """
        # Format:
        # Part of Speech, N: Number of Definitions, C: Chapter
        line = self.__get_line(',')
        if len(line) == 3:  # If there is are 3 things:
            return str(line[0]), str(line[1]), str(line[2])
        else:  # There are things missing, or there are additional things
            return None, None, None

    # Read in Methods - These methods follow the same structure. Only difference is file format
    # Specifically reading in a verb
    def __read_verb(self, n, c):
        """
        Reads in a Verb.
        Format:
        Verb Form--
        -6 Principal Parts, delimited by comma
        -Ending, Contract, Aorist, Perfect, Deponent, Irr Type, delimited by comma
        -N lines of definitions
        Individual Verbs--
        -Word Name String
        -Person, Number, Tense, Voice, Mood, delimited by comma
        --Person: 1, 2, 3, None
        --Number: Singular, Dual, Plural, None
        --Tense: Present, Future, Imperfect, Aorist, Perfect, Pluperfect, Future Perfect
        --Voice: Active, Middle, Passive
        --Mood: Infinitive, Indicative, Imperative, Subjunctive, Optative
        :param n: Number of Definitions
        :param c: Chapter
        :return: Form, Words
        """
        # Create the list and dictionary
        form = []
        words = defaultdict(list)
        # Read in Form
        # Read in Six Principal Parts
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Types
        self.__load_types(form)

        form.append(c)  # Append chapter

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(words)

        return form, words

    # Read in Noun
    def __read_noun(self, n, c):
        """
        Read in a Noun
        Format:
        Noun Form--
        -Nominative, Genitive, Article
        -Major, Minor, Gender, Irr Type, delimited by comma
        -N lines of Definitions
        Individual Nouns--
        -Word String
        -Case, Number, Gender
        --Case: Nominative, Genitive, Dative, Accusative, Vocative
        --Number: Singular, Plural
        --Gender: Masculine, Feminine, Neuter
        :param n: Number of Defs
        :param c: Chapter
        :return: Form, Words
        """
        form = []
        words = defaultdict(list)
        # Read in Form
        # Read in N, G, A
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for f in line:
            form.append(f)

        # Read in Types
        self.__load_types(form)

        form.append(c)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(words)

        return form, words

    # Read in Adjective
    def __read_adj(self, n, c):
        """
        Format:
        Adjective Form--
        -Masculine, Feminine/-, Neuter (Feminine can be blank, meaning it is a two ending adjective)
        -Major, Minor, Irr Type, delimited by comma
        -N lines of Defs
        Adjectives--
        -Word String
        -Case, Number, Gender (Same as Noun)
        :param n: Number of Defs
        :param c: Chapter
        :return: Form, Words
        """
        form = []
        words = defaultdict(list)
        # Read in Form
        # Read in M, F, N
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Types
        self.__load_types(form)

        form.append(c)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(words)

        return form, words

    # Read in Pronoun
    def __read_pro(self, n, c):
        """
        Format:
        Form--
        -Masculine, Feminine, Neuter
        -Person, Type
        --Type: Demonstrative, Personal, Reflexive, Relative
        -N lines of Defs
        Pronoun--
        -Word String
        -Case, Number, Gender, Person
        :param n: Number of Defs
        :param c: Chapter
        :return: Form, Words
        """
        form = []
        words = defaultdict(list)
        # Read in Form
        # Read in M, F, N
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Types
        self.__load_types(form)

        form.append(c)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(words)

        return form, words

    # Read Participle
    def __read_part(self):
        """
        Format:
        Form--
        -Six Principal Parts for Verbs
        Participle--
        -Word String
        -Case, Number, Gender, Tense, Voice
        :return: Form, Words
        """
        form = []
        words = defaultdict(list)
        # Read in Form
        # Read in M, F, N
        line = self.__get_line(",")
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        # Read in Words
        self.__load_words(words)

        return form, words

    # Read All Others
    def __read_misc(self, n, c):
        """
        Format:
        Form--
        -Primary Form
        -N lines of Def
        Misc--
        -Alternative Forms
        :param n: Number of Defs
        :param c: Chapter
        :param p:
        :return:
        """
        form = []
        words = defaultdict(list)
        # Read in Form
        # Read in Primary Word String
        line = self.__get_line()
        if len(line) == 0:
            return [], {}
        for p in line:
            form.append(p)

        form.append(c)

        # Read in Definitions
        self.__load_defs(n, form)

        # Read in Words
        self.__load_words(words)

        return form, words

    # Get a single line
    def __get_line(self, d=None):
        """
        Grabs a single line, with delimiter d from the file
        :param d: delimiter. Default is none
        :return: Line, delimited if requested
        """
        line = "#"
        # Ignore lines that begin with # (indicates a comment)
        # Ignore empty lines
        while True:
            line = self.__fi.readline()  # Get a line
            if len(line) == 0:  # If found the End of File
                break
            if line[0] != '#':  # If found a non-comment line
                break
        if d is None:  # If no delimiter
            return line.rstrip('\n')
        else:  # If specified a delimiter
            return line.rstrip('\n').split(d)

    # Load definitions
    def __load_defs(self, n, f):
        """
        Adds definitions from the file to f
        :param n: Number of Defs
        :param f: Where to load definitions
        :return: Success
        """
        for i in range(n):  # For each supposed definition
            line = self.__get_line()  # Get the definition line
            if len(line) == 0:
                return False  # If there is nothing, then fail
            f.append(line)
        return True

    # Load Words
    def __load_words(self, f):
        """
        Loads words into f
        :param f: Where to load
        :return: Success
        """
        while True:  # As long as you can...
            wo = self.__get_line()  # Get the Word Name
            if wo[0] == "!" or len(wo) == 0:  # Separation Between Forms/End of Form
                break  # Stop, as there are no more words
            line = self.__get_line(",")  # Get Info on Word
            if len(line) == 0:  # If no info (There must be info directly following a word string)
                return False  # Bad format
            f[wo].append(line)  # Dictionary mapping a word string to its info
        return True

    # Load Types
    def __load_types(self, f):
        """
        Load types into f
        :param f: Where to load
        :return: Success
        """
        line = self.__get_line(",")  # Get a line, delimited by comma
        if len(line) == 0:  # If the line is nothing, fail
            return False
        for t in line:  # For each type in the line, load it
            f.append(t)
        return True

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
