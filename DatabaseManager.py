# -*- coding: utf-8 -*-
import sqlite3 as sql  # For database operations
import Utils           # For Part of Speech


# Class that handles queries to the lexicon
class Lexicon:
    """
    Lexicon handles database operations
    """
    __conn = None       # Connection to the database

    # Constants for Table Names in the database
    DEF_TABLE = "Definitions"
    WORD_TABLE = "Words"
    NOUN_TABLE = "Nouns"
    VERB_TABLE = "Verbs"
    ADJ_TABLE = "Adjectives"
    PRO_TABLE = "Pronouns"
    WORD_FORM_TABLE = "WordForms"
    NOUN_FORM_TABLE = "NounForms"
    VERB_FORM_TABLE = "VerbForms"
    ADJ_FORM_TABLE = "AdjectiveForms"
    PRO_FORM_TABLE = "PronounForms"
    PART_TABLE = "ParticipleForms"

    # Mapping of Accented to Unaccented
    ACCENT_MAP = {
        u"ἀἁάᾶὰἄἅἆἇἂἃ": u"α",
        u"ἐἑέὲἔἕἒἓ": u"ε",
        u"ἰἱίῖὶἴἵἶἷἲἳ": u"ι",
        u"ὀὁόὸὄὅὂὃ": u"ο",
        u"ὐὑύῦὺὔὕὖὗὒὓ": u"υ",
        u"ἠἡήῆὴἤἥἦἧἢἣ": u"η",
        u"ὠὡώῶὼὤὥὦὧὢὣ": u"ω",
        u"ῤῥ": u"ρ"
    }

    # Constructor
    def __init__(self, db_path):
        try:  # Try to connect to the database at db_path
            self.__conn = sql.connect(db_path)  # Connect
            self.__conn.text_factory = lambda x: str(x, "utf-8")  # Set to UTF-8 for Greek characters
            self.__conn.text_factory = str
            cur = self.__conn.cursor()
            cur.execute("PRAGMA foreign_keys = 1;")  # Set Foreign Key Constraints on (SQLite thing)
            self.__conn.commit()
        except sql.Error, e:  # If there is an exception
            print "Error %s: " % e.args[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__conn:
            self.__conn.close()

    # Core methods
    # Reset the database
    def reset(self):
        """
        Erases EVERYTHING in the database (but NOT the tables)
        :return: None
        """
        # Erase everything in the database
        cur = self.__conn.cursor()
        # WordForms and Words contains everything, Foreign Keys will cascade the other tables
        cur.execute("DELETE FROM WordForms;")
        cur.execute("DELETE FROM Words;")
        self.__conn.commit()

    # Insert into database
    def insert(self, pos, word=None, form=None):
        """
        Insert the word into the database
        :param pos: Word to insert (or the form if just the form)
        :param word: Part of Speech (which tables to insert to)
        :param form: Form (Used only with Words)
        :return: Success
        """
        if word is None and form is None:
            print "Both word and form cannot be None."
            return False  # Fail if both word and form are None (Nothing to insert)
        if word is not None and form is None:
            print "Form cannot be None if Word isn't."
            return False  # Fail if word is not None, but form is

        if pos == Utils.PartOfSpeech.NOUN.value:  # Nouns
            return self.__insert_noun_form(form) if word is None else self.__insert_noun(word, form)
        elif pos == Utils.PartOfSpeech.VERB.value:  # Verbs
            return self.__insert_verb_form(form) if word is None else self.__insert_verb(word, form)
        elif pos == Utils.PartOfSpeech.ADJECTIVE.value:  # Adjectives
            return self.__insert_adj_form(form) if word is None else self.__insert_adj(word, form)
        elif pos == Utils.PartOfSpeech.PRONOUN.value:  # Pronouns
            return self.__insert_pronoun_form(form) if word is None else self.__insert_pronoun(word, form)
        elif pos == Utils.PartOfSpeech.PARTICIPLE.value:
            return False if word is None else self.__insert_participle(word, form)
        else:  # Others
            print "Inserting other words"
        return True

    # Select the info of a word
    def select(self, word, is_verbose=False, is_define=False, is_unaccented=False):
        """
        Search the database for the word's info
        :param word: Word to query
        :param is_verbose: Whether to only give form info, or full info
        :param is_define: Whether to include definitions
        :param is_unaccented: Whether the word is unaccented or not (This is useful for enclitics, or words in sentences with enclitics
        :return: Info, Form, Definitions - each of which are lists
        """
        cur = self.__conn.cursor()

        # Get the Word ID, Form ID Part of word
        cur.execute("SELECT WordID, FormID, PartOfSpeech FROM " + self.WORD_TABLE + " WHERE " +
                    self.WORD_TABLE + (".UnaccentedWordName" if is_unaccented else ".WordName") +
                    " == '" + word + "';")
        ids = cur.fetchone()  # If there is more than one, then there is something wrong (THIS PAIR SHOULD BE UNIQUE)
        if ids is None:  # If there was no match, word cannot be found
            return None, None, None

        word_id = ids[0]; form_id = ids[1]; part = ids[2]

        info = None; form = None; defs = None

        table = ""; form_table = ""
        # Switch to see which Table to look at:
        if part == Utils.PartOfSpeech.VERB.value:
            table = self.VERB_TABLE
            form_table = self.VERB_FORM_TABLE
        elif part == Utils.PartOfSpeech.NOUN.value:
            table = self.NOUN_TABLE
            form_table = self.NOUN_FORM_TABLE
        elif part == Utils.PartOfSpeech.ADJECTIVE.value:
            table = self.ADJ_TABLE
            form_table = self.ADJ_FORM_TABLE
        elif part == Utils.PartOfSpeech.PRONOUN.value:
            table = self.PRO_TABLE
            form_table = self.PRO_FORM_TABLE
        elif part == Utils.PartOfSpeech.PARTICIPLE.value:
            table = self.PART_TABLE
            form_table = self.VERB_FORM_TABLE
        else:
            print "MISC TABLE"
        # Get the INFO for that word from the table
        cur.execute("SELECT * FROM " + table + " WHERE " +
                    table + ".WordID == " + str(word_id) + " AND " +
                    table + ".FormID == " + str(form_id) + ";")
        info = cur.fetchone()[2:]  # Again, there should ONLY be ONE.
        #  Ignore the first two (word id and form id)

        # Get Form if verbose
        if is_verbose:
            cur.execute("SELECT * FROM " + form_table + " WHERE " +
                        form_table + ".FormID == " + str(form_id) + ";")
            form = cur.fetchone()[1:] # Ignore the first column (first id)

        if is_define:
            cur.execute("SELECT Definition FROM " + self.DEF_TABLE + " WHERE " +
                        self.DEF_TABLE + ".FormID == " + str(form_id) + ";")
            defs = cur.fetchall()  # There can be more than one

        return info, form, defs

        # Look up the word in Words (If unaccented, look at unaccented column instead)
        # Get WordID, FormID, and PartOfSpeech
        # Based on PartOfSpeech, look at relevant table
        # Get All from relevant word table (not form table) by matching wordID and formID
        # If verbose, then look at relevant form table, and select everything by matching formID + Chapter from WordForms
        # If define, then look at definitions table, and select everything by matching formID
        # return the triple: Info from Word Table, Form from Verbose, Defs from Define

    # Insert Helper Methods
    # Insert a Noun
    def __insert_noun(self, noun, form):
        """
        Insert a Noun
        :param noun: Noun - list that contains word info
        :param form: Noun Form list
        :return: Success
        """
        # Check if the Word Form exists --This must exist, or else fail
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.NOUN)
        if form_id is None:
            return False

        # Insert every Noun:
        for n, l in noun.iteritems():
            for i in l:
                # Get the next local ID
                word_id = self.__get_local_id(form_id)

                # Insert
                self.__sql_insert_words(n, word_id, form_id, Utils.PartOfSpeech.NOUN)
                self.__sql_insert_nouns(word_id, form_id, i[0], i[1], i[2])

        self.__conn.commit()
        return True

    # Insert a Noun Form
    def __insert_noun_form(self, noun):
        """
        Insert a Noun Form
        :param noun: Noun Form
        :return: Success
        """

        # Check if the Word Form exists --it shouldn't exist or else we are re-adding
        form_id = self.__get_form_id(noun[:3], Utils.PartOfSpeech.NOUN)
        if form_id is not None:
            return False

        # Get the next Form ID
        form_id = self.__get_next_form_id()

        # Insert into WordForms --FormID, pos
        self.__sql_insert_word_forms(form_id, Utils.PartOfSpeech.NOUN, noun[7])

        # Insert into NounForms --Nominative, Genitive, Article, Gender, Dec, Dec2, Irr
        self.__sql_insert_noun_forms(form_id, noun[0], noun[1], noun[2], noun[3], noun[4], noun[5], noun[6])

        # Insert into Definitions
        definitions = noun[8:]
        for d in definitions:
            self.__sql_insert_definition(form_id, d)

        self.__conn.commit()
        return True

    # Insert a Verb
    def __insert_verb(self, verb, form):
        """
        Insert a Verb
        :param verb: Verb Words
        :param form: Verb Form
        :return: Success
        """
        # Check if word form exists
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.VERB)
        if form_id is None:
            return False

        for v, l in verb.iteritems():
            for i in l:
                # Get next local ID
                word_id = self.__get_local_id(form_id)

                # Insert
                self.__sql_insert_words(v, word_id, form_id, Utils.PartOfSpeech.VERB)
                self.__sql_insert_verbs(word_id, form_id, i[0], i[1], i[2], i[3], i[4])

        self.__conn.commit()
        return True

    # Insert Verb Form
    def __insert_verb_form(self, verb):
        """
        Insert a Verb Form
        :param verb: Verb Form
        :return: Success
        """
        # Check if word form exists
        form_id = self.__get_form_id(verb[:6], Utils.PartOfSpeech.VERB)
        if form_id is not None:
            return False

        # Get next form ID
        form_id = self.__get_next_form_id()

        # Insert into Word Forms
        self.__sql_insert_word_forms(form_id, Utils.PartOfSpeech.VERB, verb[12])
        # Insert into Verb Forms
        self.__sql_insert_verb_forms(form_id, verb[0], verb[1], verb[2], verb[3],
                                     verb[4], verb[5], verb[6], verb[7], verb[8],
                                     verb[9], verb[10], verb[11])

        # Insert into Definitions
        definitions = verb[13:]
        for d in definitions:
            self.__sql_insert_definition(form_id, d)

        self.__conn.commit()
        return True

    # Insert Adjective
    def __insert_adj(self, adj, form):
        """
        Insert an Ajdective
        :param adj: Adjectives
        :param form: Adj Form
        :return: Success
        """

        # Check for Word Form
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.ADJECTIVE)
        if form_id is None:
            return False

        for a, l in adj.iteritems():
            for i in l:
                # Get next local ID
                word_id = self.__get_local_id(form_id)

                # Insert
                self.__sql_insert_words(a, word_id, form_id, Utils.PartOfSpeech.ADJECTIVE)
                self.__sql_insert_adj(word_id, form_id, i[0], i[1], i[2])

        self.__conn.commit()
        return True

    # Insert Adjective Form
    def __insert_adj_form(self, adj):
        """
        Insert an Adjective Form
        :param adj: Adj Form
        :return: Success
        """

        # Check for Word Form
        form_id = self.__get_form_id(adj[:3], Utils.PartOfSpeech.ADJECTIVE)
        if form_id is not None:
            return False

        # Get next Form ID
        form_id = self.__get_next_form_id()

        # Insert into Word Forms
        self.__sql_insert_word_forms(form_id, Utils.PartOfSpeech.ADJECTIVE, adj[6])

        # Insert into Adj Forms
        self.__sql_insert_adj_forms(form_id, adj[0], adj[1], adj[2], adj[3], adj[4], adj[5])

        # Insert into Definitions
        definitions = adj[7:]
        for d in definitions:
            self.__sql_insert_definition(form_id, d)

        self.__conn.commit()
        return True

    # Insert Pronoun
    def __insert_pronoun(self, pro, form):
        """
        Insert Pronoun
        :param pro: Pronouns
        :param form: P Form
        :return: Success
        """

        # Check for Word Form
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.PRONOUN)
        if form_id is None:
            return False

        for p, l in pro.iteritems():
            for i in l:
                # Get next local ID
                word_id = self.__get_local_id(form_id)

                # Insert
                self.__sql_insert_words(p, word_id, form_id, Utils.PartOfSpeech.PRONOUN)
                self.__sql_insert_pro(word_id, form_id, i[0], i[1], i[2], i[3])

        self.__conn.commit()
        return True

    # Insert Pronoun Form
    def __insert_pronoun_form(self, pro):
        """
        Insert P Form
        :param pro: P Form
        :return: Success
        """

        # Check for Word Form
        form_id = self.__get_form_id(pro[:3], Utils.PartOfSpeech.PRONOUN)
        if form_id is not None:
            return False

        # Get next Form ID
        form_id = self.__get_next_form_id()

        # Insert into Word Forms
        self.__sql_insert_word_forms(form_id, Utils.PartOfSpeech.PRONOUN, pro[5])

        # Insert into Pro Forms
        self.__sql_insert_pro_forms(form_id, pro[0], pro[1], pro[2], pro[3], pro[4])

        # Insert into Definitions
        definitions = pro[6:]
        for d in definitions:
            self.__sql_insert_definition(form_id, d)

        self.__conn.commit()
        return True

    # Insert Participle
    def __insert_participle(self, part, form):
        """
        Insert Participle
        :param part: Participle
        :param form: Verb Form (Remember Participles are formed from Verbs)
        :return: Success
        """

        # Check for Word Form
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.PARTICIPLE)
        if form_id is None:
            return False

        for p, l in part.iteritems():
            for i in l:
                # Get next local ID
                word_id = self.__get_local_id(form_id)

                # Insert into Words
                self.__sql_insert_words(p, word_id, form_id, Utils.PartOfSpeech.PARTICIPLE)

                # Insert into Participles
                self.__sql_insert_part(word_id, form_id, i[0], i[1], i[2], i[3], i[4])

        self.__conn.commit()
        return True

    # Select Query Helpers
    # Form ID Select Method
    def __get_form_id(self, form, pos):
        """
        Gets the Form ID of the form
        :param form: Form
        :param pos: Part of Speech
        :return: Form ID
        """
        if pos == Utils.PartOfSpeech.NOUN:  # Nouns
            return self.__get_form_id_noun(form)
        elif pos == Utils.PartOfSpeech.VERB:  # Verbs
            return self.__get_form_id_verb(form)
        elif pos == Utils.PartOfSpeech.ADJECTIVE:  # Adjectives
            return self.__get_form_id_adj(form)
        elif pos == Utils.PartOfSpeech.PRONOUN:  # Pronouns
            return self.__get_form_id_pro(form)
        else:  # Others
            print "Get Form ID of another word"

    # Form ID of Noun
    def __get_form_id_noun(self, form):
        """
        Get Form ID of Noun
        :param form: N Form
        :return: ID or None
        """
        cur = self.__conn.cursor()
        cur.execute("SELECT FormID FROM " + self.NOUN_FORM_TABLE + " WHERE " +
                    self.NOUN_FORM_TABLE + ".Nominative == '" + form[0] + "' AND " +
                    self.NOUN_FORM_TABLE + ".Genitive == '" + form[1] + "' AND " +
                    self.NOUN_FORM_TABLE + ".Article == '" + form[2] + "';")
        data = cur.fetchone()  # There should be only one form or None
        return data[0] if data is not None else None

    # Form ID of Verb
    def __get_form_id_verb(self, form):
        """
        Get Form ID of Verb
        :param form: V Form
        :return: ID or None
        """
        cur = self.__conn.cursor()
        cur.execute("SELECT FormID FROM " + self.VERB_FORM_TABLE + " WHERE " +
                    self.VERB_FORM_TABLE + ".FirstPrincipalPart == '" + form[0] + "' AND " +
                    self.VERB_FORM_TABLE + ".SecondPrincipalPart == '" + form[1] + "' AND " +
                    self.VERB_FORM_TABLE + ".ThirdPrincipalPart == '" + form[2] + "' AND " +
                    self.VERB_FORM_TABLE + ".FourthPrincipalPart == '" + form[3] + "' AND " +
                    self.VERB_FORM_TABLE + ".FifthPrincipalPart == '" + form[4] + "' AND " +
                    self.VERB_FORM_TABLE + ".SixthPrincipalPart == '" + form[5] + "';")
        data = cur.fetchone()  # There should be only one form or None
        return data[0] if data is not None else None

    # Form ID of Adj
    def __get_form_id_adj(self, form):
        """
        Get Form ID of Adj
        :param form: A Form
        :return: ID or None
        """
        cur = self.__conn.cursor()
        cur.execute("SELECT * FROM " + self.ADJ_FORM_TABLE + " WHERE " +
                    self.ADJ_FORM_TABLE + ".Masculine == '" + form[0] + "' AND " +
                    self.ADJ_FORM_TABLE + ".Feminine == '" + form[1] + "' AND " +
                    self.ADJ_FORM_TABLE + ".Neuter == '" + form[2] + "';")
        data = cur.fetchone()  # There should be only one form or None
        return data[0] if data is not None else None

    # Form ID of Pronoun
    def __get_form_id_pro(self, form):
        """
        Get Form ID of Pro
        :param form: P Form
        :return: ID or None
        """
        cur = self.__conn.cursor()
        cur.execute("SELECT * FROM " + self.PRO_FORM_TABLE + " WHERE " +
                    self.PRO_FORM_TABLE + ".Masculine == '" + form[0] + "' AND " +
                    self.PRO_FORM_TABLE + ".Feminine == '" + form[1] + "' AND " +
                    self.PRO_FORM_TABLE + ".Neuter == '" + form[2] + "';")
        data = cur.fetchone()  # There should be only one form or None
        return data[0] if data is not None else None

    # Word ID Select Method
    def __get_local_id(self, form_id):
        """
        Get the next Word ID of a form
        :param form_id: Form ID
        :return: Word ID or 0 (if there are no words for that form yet)
        """
        cur = self.__conn.cursor()
        cur.execute("SELECT MAX(WordID) FROM " + self.WORD_TABLE + " WHERE " +
                    self.WORD_TABLE + ".FormID == " + str(form_id) + ";")
        data = cur.fetchone()  # There should be only one
        return data[0] + 1 if data[0] is not None else 0

    # Next Form ID Select Method
    def __get_next_form_id(self):
        """
        Get the next Form ID
        :return: Form ID or 0 (if there are no forms yet)
        """
        cur = self.__conn.cursor()
        cur.execute("SELECT MAX(FormID) FROM " + self.WORD_FORM_TABLE + ";")
        data = cur.fetchone()
        return (data[0] + 1) if data[0] is not None else 0

    # SQL Insert Methods
    # Insert Definition SQLite
    def __sql_insert_definition(self, form_id, definition):
        """
        Executes an SQLite insert query for definitions
        :param form_id: Form
        :param definition: Defs
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.DEF_TABLE + " VALUES( " +
                    str(form_id) + ", '" +
                    definition + "');")

    # Insert Word SQLite
    def __sql_insert_words(self, name, word_id, form_id, pos):
        """
        Executes an SQLite insert query for words
        :param name: Word String Name
        :param word_id: Word ID
        :param form_id: Form ID
        :param pos: Part of Speech
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.WORD_TABLE + " VALUES( " +
                    str(word_id) + ", " +
                    str(form_id) + ", '" +
                    pos.value + "', '" +
                    name + "', '" +
                    self.__deaccentuate(name) + "');")

    # Insert Noun SQLite
    def __sql_insert_nouns(self, word_id, form_id, case, number, gender):
        """
        Executes an SQLite insert query for nouns
        :param word_id: Word ID
        :param form_id: Form ID
        :param case: Case
        :param number: Number
        :param gender: Gender
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.NOUN_TABLE + " VALUES( " +
                    str(word_id) + ", " +
                    str(form_id) + ", '" +
                    case + "', '" +
                    number + "', '" +
                    gender + "');")

    # Insert Verbs SQLite
    def __sql_insert_verbs(self, word_id, form_id, person, number, tense, voice, mood):
        """
        Executes an SQLite insert query for verbs
        :param word_id: Word ID
        :param form_id: Form ID
        :param person: Person
        :param number: Number
        :param tense: Tense
        :param voice: Voice
        :param mood: Mood
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.VERB_TABLE + " VALUES( " +
                    str(word_id) + ", " +
                    str(form_id) + ", '" +
                    person + "', '" +
                    number + "', '" +
                    tense + "', '" +
                    voice + "', '" +
                    mood + "');")

    # Insert Adj SQLite
    def __sql_insert_adj(self, word_id, form_id, case, number, gender):
        """
        Executes an SQLite insert query for adj
        :param word_id: Word ID
        :param form_id: Form ID
        :param case: Case
        :param number: Number
        :param gender: Gender
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.ADJ_TABLE + " VALUES( " +
                    str(word_id) + ", " +
                    str(form_id) + ", '" +
                    case + "', '" +
                    number + "', '" +
                    gender + "');")

    # Insert Pro SQLite
    def __sql_insert_pro(self, word_id, form_id, case, number, gender, person):
        """
        Executes an SQLite insert query for pros
        :param word_id: Word ID
        :param form_id: Form ID
        :param case: Case
        :param number: Number
        :param gender: Gender
        :param person: Person
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.PRO_TABLE + " VALUES( " +
                    str(word_id) + ", " +
                    str(form_id) + ", '" +
                    case + "', '" +
                    number + "', '" +
                    gender + "', '" +
                    person + "');")

    # Insert Part SQLite
    def __sql_insert_part(self, word_id, form_id, case, number, gender, tense, voice):
        """
        Executes an SQLite insert query for participles
        :param word_id: Word ID
        :param form_id: Form ID
        :param case: Case
        :param number: Number
        :param gender: Gender
        :param tense: Tense
        :param voice: Voice
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.PART_TABLE + " VALUES( " +
                    str(word_id) + ", " +
                    str(form_id) + ", '" +
                    case + "', '" +
                    number + "', '" +
                    gender + "', '" +
                    tense + "', '" +
                    voice + "');")

    # Insert Word Forms
    def __sql_insert_word_forms(self, form_id, pos, c):
        """
        Executes an SQLite insert query for word forms
        :param form_id: Form ID
        :param pos: Part of Speech
        :param c: Chapter
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.WORD_FORM_TABLE + " VALUES( " +
                    str(form_id) + ", '" +
                    pos.value + "', " +
                    str(c) + ");")

    # Insert Noun Forms
    def __sql_insert_noun_forms(self, form_id, nominative, genitive, article, gender, major, minor, irr):
        """
        Executes an SQLite insert query for noun forms
        :param form_id: Form ID
        :param nominative: N
        :param genitive: G
        :param article: A
        :param gender: Gender
        :param major: Major
        :param minor: Minor
        :param irr: Irregular
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.NOUN_FORM_TABLE + " VALUES( " +
                    str(form_id) + ", '" +
                    nominative + "', '" +
                    genitive + "', '" +
                    article + "', '" +
                    gender + "', '" +
                    major + "', '" +
                    minor + "', '" +
                    irr + "');")

    # Insert Verb Forms
    def __sql_insert_verb_forms(self, form_id, first, second,
                                third, fourth, fifth, sixth,
                                ending, contract, aorist, perfect, deponent, irr):
        """
        Executes an SQLite insert query for verb forms
        :param form_id: Form ID
        :param first: Principal Part
        :param second: Principal Part
        :param third: Principal Part
        :param fourth: Principal Part
        :param fifth: Principal Part
        :param sixth: Principal Part
        :param ending: Ω or μι ending
        :param contract: Whether the verb contracts in the Present, Imperfect, Future
        :param aorist: Whether the verb uses First Aorist or Second Aorist endings
        :param perfect: Whether the verb uses κ or not
        :param deponent: Whether the verb is deponent in one or more of its forms
        :param irr: Whether the verb conjugates regularly
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.VERB_FORM_TABLE + " VALUES( '" +
                    str(form_id) + "', '" +
                    first + "', '" +
                    second + "', '" +
                    third + "', '" +
                    fourth + "', '" +
                    fifth + "', '" +
                    sixth + "', '" +
                    ending + "', '" +
                    contract + "', '" +
                    aorist + "', '" +
                    perfect + "', '" +
                    deponent + "', '" +
                    irr + "');")

    # Insert Adj Forms
    def __sql_insert_adj_forms(self, form_id, masculine, feminine, neuter, major, minor, irr):
        """
        Executes an SQLite query to insert adj form
        :param form_id: Form ID
        :param masculine: M
        :param feminine: F
        :param neuter: N
        :param major: Declension
        :param minor: Subgroup
        :param irr: Irregularity
        :return: None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.ADJ_FORM_TABLE + " VALUES( " +
                    str(form_id) + ", '" +
                    masculine + "', '" +
                    feminine + "', '" +
                    neuter + "', '" +
                    major + "', '" +
                    minor + "', '" +
                    irr + "');")

    # Insert Pronoun Forms
    def __sql_insert_pro_forms(self, form_id, masculine, feminine, neuter, person, kind):
        """
        Executes an SQLite query to insert pro forms
        :param form_id: Form ID
        :param masculine: M
        :param feminine: F
        :param neuter: N
        :param person: 1, 2, 3
        :param kind: type of pronoun
        :return:None
        """
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.PRO_FORM_TABLE + " VALUES( " +
                    str(form_id) + ", '" +
                    masculine + "', '" +
                    feminine + "', '" +
                    neuter + "', '" +
                    person + "', '" +
                    kind + "');")

    # Deaccentuate a word (Remove accents and breathing marks)
    def __deaccentuate(self, word):
        """
        This removes accents and breathing marks above letters.
        This does not remove isolated accents.
        :param word: The word to deaccentuate
        :return: Deaccentuated word
        """
        unaccented = ""
        for i in range(len(word)):  # Loop through each character
            unaccented += self.__deaccentuate_char(word[i])
        return unaccented

    # Deaccentuate a character (Get an unaccented version of the character)
    def __deaccentuate_char(self, ch):
        for a, u in self.ACCENT_MAP.iteritems():
            if self.__find_unicode(a, ch) >= 0:
                return u
        return ch

    def __find_unicode(self, s, c):
        for i in range(len(s)):
            if s[i] == c:
                return i
        return -1

# Old Handler Class
# Here for reference
'''
# Class to handle the Greek Lexicon Database.
# This includes querying, inserting, and modifying data.
class Handler:
    __con = None

    WORDS = "Words"
    DEFINITIONS = "Definitions"
    VERBS = "Verbs"
    PRINCIPLE_PARTS = "PrincipalParts"
    INFINITIVES = "Infinitives"
    CONJUGATIONS = "Conjugations"
    NAME_TO_ID = "NameToID"
    NOUNS = "Nouns"
    NOUN_DECLENSIONS = "NounDeclensions"
    ADJECTIVES = "Adjectives"
    ADJ_DECLENSIONS = "AdjectiveDeclensions"

    # Constructor
    def __init__(self, db_path):
        try:
            self.__con = sql.connect(db_path)
            self.__con.text_factory = lambda x: str(x, "utf-8")
            self.__con.text_factory = str
        except sql.Error, e:
            print "Error %s: " % e.args[0]

    # With Methods
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__con:
            self.__con.close()

    # Public Query Methods
    def query_definition(self, word):
        # print "Querying Definition of ", word
        cur = self.__con.cursor()
        # Get ID for the word
        wid = self.__get_id(word)
        if wid is None:
            return None
        cur.execute("SELECT Definition FROM " + self.DEFINITIONS +
                    " WHERE " + self.DEFINITIONS + ".WordID == " + str(wid) + ";")
        return cur.fetchall()

    def query_face(self, word):
        # print "Querying Face of ", word
        cur = self.__con.cursor()
        wid = self.__get_id(word)
        if wid is None:
            return None
        pos = self.__get_pos(word)
        if pos == "Verb":
            cur.execute("SELECT FirstPrincipalPart, SecondPrincipalPart, ThirdPrincipalPart, "
                        "FourthPrincipalPart, FifthPrincipalPart, SixthPrincipalPart "
                        "FROM " + self.PRINCIPLE_PARTS + " WHERE " +
                        self.PRINCIPLE_PARTS + ".VerbID == '" + str(wid) + "';")
            return cur.fetchone()
        elif pos == "Noun":
            cur.execute("SELECT Nominative, Genitive, Article "
                        "FROM " + self.NOUNS + " WHERE " +
                        self.NOUNS + ".WordID == '" + str(wid) + "';")
            data = cur.fetchone()
            return cur.fetchone()
        elif pos == "Adjective":
            cur.execute("SELECT Masculine, Feminine, Neuter "
                        "FROM " + self.ADJECTIVES + " WHERE " +
                        self.ADJECTIVES + ".WordID == '" + str(wid) + "';")
            return cur.fetchone()
        else:
            return None

    def query_info(self, word):
        # print "Querying Form of ", word
        cur = self.__con.cursor()
        wid = self.__get_id(word)
        if wid is None:
            return None
        pos = self.__get_pos(word)
        if pos == "Verb":
            cur.execute("SELECT W.PartOfSpeech, V.VerbGroup, V.ContractGroup "
                        "FROM " + self.Words + " AS W, " + self.VERBS + " AS V "
                        "WHERE W.WordID == " + str(wid) + " AND V.WordID == " + str(wid) + ";")
            return cur.fetchone()
        elif pos == "Noun":
            cur.execute("SELECT W.PartOfSpeech, N.Gender, N.DecGroup, N.DecSubGroup "
                        "FROM " + self.Words + " AS W, " + self.NOUNS + " AS N "
                        "WHERE W.WordID == " + str(wid) + " AND N.WordID == " + str(wid) + ";")
            return cur.fetchone()
        elif pos == "Adjective":
            cur.execute("SELECT W.PartOfSpeech, A.DecGroup, A.DecSubGroup "
                        "FROM " + self.Words + " AS W, " + self.ADJECTIVES + " AS A "
                        "WHERE W.WordID == " + " AND A.WordID == " + str(wid) + ";")
            return cur.fetchone()
        else:
            return None

    def query_conjugation(self, word, tense):
        # print "Querying Conjugation of ", word, " in ", tense
        cur = self.__con.cursor()
        wid = self.__get_id(word)
        if wid is None:
            return None
        if self.__get_pos(word) != "Verb":
            return None
        cur.execute("SELECT Number, FirstPerson, SecondPerson, ThirdPerson "
                    "FROM " + self.CONJUGATIONS + " "
                    "WHERE VerbID == " + str(wid) + " "
                    "AND Tense == '" + tense[0] + "' AND Voice == '" + tense[1] +
                    "' AND Mood == '" + tense[2] + "';")
        return cur.fetchall()

    def query_declension(self, word):
        # print "Querying Declension of ", word, " as ", gender
        cur = self.__con.cursor()
        wid = self.__get_id(word)
        if wid is None:
            return None
        pos = self.__get_pos(word)
        if pos == "Noun":
            cur.execute("SELECT Number, Nominative, Genitive, Dative, Accusative, Vocative "
                        "FROM " + self.NOUN_DECLENSIONS + " "
                        "WHERE NounID == " + str(wid) + ";")
            return cur.fetchall()
        elif pos == "Adjective":
            cur.execute("SELECT Gender, Number, Nominative, Genitive, Dative, Accusative, Vocative "
                        "FROM " + self.ADJ_DECLENSIONS + " "
                        "WHERE AdjID == " + str(wid) + ";")
            return cur.fetchall()
        else:
            return None

    def query_all(self, pos):
        # print "Querying All Words that are ", pos
        cur = self.__con.cursor()
        table = self.__map_pos_to_table(pos)
        if pos == "Verb":
            cur.execute("SELECT * FROM " + table +
                        " JOIN PrincipalParts ON " + table + ".WordID == PrincipalParts.VerbID")
        else:
            cur.execute("SELECT * FROM " + table)
        return cur.fetchall()

    def reset(self, pos):
        # print "Removing data from ", pos, "table"
        cur = self.__con.cursor()
        cur.execute("DELETE FROM " + self.__map_pos_to_table(pos) + ";")
        self.__con.commit()

    def reset_all(self):
        cur = self.__con.cursor()
        cur.execute("DELETE FROM " + self.WORDS + ";")
        self.__con.commit()

    def remove_word(self, word):
        cur = self.__con.cursor()
        wid = self.__get_id(word)
        if wid is None:
            return False
        else:
            cur.execute("DELETE FROM " + self.WORDS +
                        " WHERE " + self.WORDS + ".WordID == " + str(wid) + ";")
            self.__con.commit()
            return True

    # Private Helper Methods
    def __get_pos(self, word):
        # print "Getting the part of speech of ", word
        cur = self.__con.cursor()
        wid = self.__get_id(word)
        if wid is None:
            return None
        cur.execute("SELECT PartOfSpeech FROM " + self.WORDS +
                    " WHERE " + self.WORDS + ".WordID == " + str(wid) + ";")
        data = cur.fetchone()
        return data[0] if data is not None else None

    def __get_id(self, word):
        cur = self.__con.cursor()
        cur.execute("SELECT WordID FROM " + self.NAME_TO_ID +
                    " WHERE " + self.NAME_TO_ID + ".WordName == '" + word + "';")
        data = cur.fetchone()
        return data[0] if data is not None else None

    def __map_pos_to_table(self, pos):
        if pos == "Noun":
            return self.NOUNS
        elif pos == "Verb":
            return self.VERBS
        elif pos == "Adjective":
            return self.ADJECTIVES
        else:
            return None

    def __check_id_uniqueness(self, wid):
        cur = self.__con.cursor()
        cur.execute("SELECT * FROM " + self.WORDS +
                    " WHERE " + self.WORDS + ".WordID == " + str(wid) + ";")
        return cur.fetchone() is None

    def __check_name_uniqueness(self, name):
        cur = self.__con.cursor()
        cur.execute("SELECT * FROM " + self.NAME_TO_ID +
                    " WHERE " + self.NAME_TO_ID + ".WordName == '" + name + "';")
        #print "CHECKING NAME: ", cur.fetchone()
        return cur.fetchone() is None

    def __split_alts(self, word):
        return word.split('|')

    # Public Insert Methods
    def insert_verb(self, wid, verb_group, contract_group, principal_parts, infinitives, conjugations, definitions):
        """ Inserts a Verb into the Lexicon
        :param wid: the id of the verb [integer]
        :param verb_group: what ending group the verb is in
        (Ω or μι) [string or enum]
        :param contract_group: what contract type the verb is in
        (None, άω, έω, όω, Future Contract) [string or enum]
        :param principal_parts: the 6 principal parts of the verb
        [list of strings of size 6]
        :param infinitives: the infinitive forms of the verb
        [list of strings of size 7+]
        :param conjugations: the conjugations for each number + person pair for every possible tense
        [dictionary mapping a size 3 list of strings to a size 6 list of strings]
        :param definitions: the definitions for the verb
        [variable list of strings]
        :return: none
        """
        if not self.__check_id_uniqueness(wid):
            return False
        cur = self.__con.cursor()
        # Insert into Words first
        cur.execute("INSERT INTO " + self.WORDS + " VALUES(" + str(wid) + ",'Verb');")
        # Insert into Definitions
        for definition in definitions:
            cur.execute("INSERT INTO " + self.DEFINITIONS + " VALUES(" + str(wid) + ",'" + definition + "');")
        # Insert into Verbs
        cur.execute("INSERT INTO " + self.VERBS +
                    " VALUES(" + str(wid) + ",'" + verb_group + "','" + contract_group + "');")
        # Insert into PrincipalParts
        cur.execute("INSERT INTO " + self.PRINCIPLE_PARTS +
                    " VALUES(" + str(wid) + ",'" +
                    principal_parts[0] + "','" +
                    principal_parts[1] + "','" +
                    principal_parts[2] + "','" +
                    principal_parts[3] + "','" +
                    principal_parts[4] + "','" +
                    principal_parts[5] + "');")
        # Insert into Infinitives
        cur.execute("INSERT INTO " + self.INFINITIVES +
                    " VALUES(" + str(wid) + ",'" +
                    infinitives[0] + "','" +
                    infinitives[1] + "','" +
                    infinitives[2] + "','" +
                    infinitives[3] + "','" +
                    infinitives[4] + "','" +
                    infinitives[5] + "','" +
                    infinitives[6] + "');")
        # Insert into each Conjugation Table
        for tense, conjugation in conjugations.iteritems():
            cur.execute("INSERT INTO " + self.CONJUGATIONS +
                        " VALUES(" + str(wid) + ",'" +
                        tense[0] + "','" +
                        tense[1] + "','" +
                        tense[2] + "','Singular','" +
                        conjugation[0] + "','" +
                        conjugation[1] + "','" +
                        conjugation[2] + "');")
            cur.execute("INSERT INTO " + self.CONJUGATIONS +
                        " VALUES(" + str(wid) + ",'" +
                        tense[0] + "','" +
                        tense[1] + "','" +
                        tense[2] + "','Plural','" +
                        conjugation[3] + "','" +
                        conjugation[4] + "','" +
                        conjugation[5] + "');")
        # For each conjugated verb and infinitive, add each to NameToID
        for inf in infinitives:
            li = self.__split_alts(inf)
            for w in li:
                cur.execute("INSERT INTO " + self.NAME_TO_ID + " VALUES('" + w + "'," + str(wid) + ");")
        for tense, conjugation in conjugations.iteritems():
            for word in conjugation:
                li = self.__split_alts(word)
                for w in li:
                    if self.__check_name_uniqueness(w) and w is not "":
                        cur.execute("INSERT INTO " + self.NAME_TO_ID + " VALUES('" +
                                    w + "'," + str(wid) + ");")
        self.__con.commit()
        return True

    def insert_noun(self, wid, gender, group, subgroup, face, declensions, definitions):
        """ Inserts a Noun into the Lexicon
        :param wid: Id of the Noun [Integer]
        :param gender: Gender of the Noun
        (Masculine, Feminine, Neuter) [String]
        :param group: Declension Group of the Noun (1st, 2nd, 3rd) [String]
        :param subgroup: Declension Subgroup of the Noun
        ( (ᾱ, ᾱς), (η, ης), (ᾱ, ης), (α, ᾱς), (ᾱς, ου),
        (ης, ου), (ος, ου), (ον, ου), (ς, ος), (-,ος),
        (ης, ους), (ος, ους), (ας, ως), (ως, ους) ) [String]
        :param face: The Lexical entry of the Noun
        (Nominative Singular Form, Genitive Singular Form, Definite Article) [Size 3 List of Strings]
        :param declensions: The declensions of the Noun
        [Dictionary mapping a String (Number) to a Size 5 List of Strings]
        :param definitions: Variable List of Strings
        :return: If it can insert
        """
        if not self.__check_id_uniqueness(wid):
            return False
        cur = self.__con.cursor()
        # Insert into Words
        cur.execute("INSERT INTO " + self.WORDS + " VALUES(" + str(wid) + ",'Noun');")
        # Insert into Definitions
        for definition in definitions:
            cur.execute("INSERT INTO " + self.DEFINITIONS + " VALUES(" + str(wid) + ",'" + definition + "');")
        # Insert into Nouns
        cur.execute("INSERT INTO " + self.NOUNS + " VALUES(" +
                    str(wid) + ",'" + face[0] + "','" +
                    face[1] + "','" +
                    face[2] + "','" +
                    gender + "','" +
                    group + "','" +
                    subgroup + "');")
        # Insert into NounDeclensions
        for number, declension in declensions.iteritems():
            cur.execute("INSERT INTO " + self.NOUN_DECLENSIONS + " VALUES(" +
                        str(wid) + ",'" +
                        number + "','" +
                        declension[0] + "','" +
                        declension[1] + "','" +
                        declension[2] + "','" +
                        declension[3] + "','" +
                        declension[4] + "');")
        # For each declined noun, add to NameToID
        for number, declension in declensions.iteritems():
            for word in declension:
                li = self.__split_alts(word)
                for w in li:
                    if self.__check_name_uniqueness(w):
                        cur.execute("INSERT INTO " + self.NAME_TO_ID + " VALUES('" +
                                    w + "'," + str(wid) + ");")
        self.__con.commit()
        return True

    def insert_adj(self, wid, group, subgroup, face, m_declensions, f_declensions, n_declensions, definitions):
        """ Inserts an Adjective into the Lexicon
        :param wid: id
        :param group: First/Second or Third
        :param subgroup: (ος, ᾱ, ον), (ος, η, ον), Nasal, Sigma
        :param face: Nominative Masculine, Nominative Feminine, Nominative Neuter
        (if Nominative Feminine is empty, that means it is a 2 ending adj)
        :param m_declensions: Dictionary mapping Number to 5 Words
        :param f_declensions: ""
        :param n_declensions: ""
        :param definitions: List of definitions
        :return:
        """
        if not self.__check_id_uniqueness(wid):
            return False
        cur = self.__con.cursor()
        # Insert into Words
        cur.execute("INSERT INTO " + self.WORDS + " VALUES(" + str(wid) + ",'Adjective');")
        # Insert into Definitions
        for definition in definitions:
            cur.execute("INSERT INTO " + self.DEFINITIONS + " VALUES(" + str(wid) + ",'" + definition + "');")
        # Insert into Adjectives
        cur.execute("INSERT INTO " + self.ADJECTIVES + " VALUES(" +
                    str(wid) + ",'" + face[0] + "','" +
                    face[1] + "','" +
                    face[2] + "','" +
                    group + "','" +
                    subgroup + "');")
        # Insert into AdjectiveDeclensions
        for number, declension in m_declensions.iteritems():
            cur.execute("INSERT INTO " + self.ADJ_DECLENSIONS + " VALUES(" +
                        str(wid) + ",'" +
                        "Masculine" + "','" +
                        number + "','" +
                        declension[0] + "','" +
                        declension[1] + "','" +
                        declension[2] + "','" +
                        declension[3] + "','" +
                        declension[4] + "');")
        for number, declension in f_declensions.iteritems():
            cur.execute("INSERT INTO " + self.ADJ_DECLENSIONS + " VALUES(" +
                        str(wid) + ",'" +
                        "Feminine" + "','" +
                        number + "','" +
                        declension[0] + "','" +
                        declension[1] + "','" +
                        declension[2] + "','" +
                        declension[3] + "','" +
                        declension[4] + "');")
        for number, declension in n_declensions.iteritems():
            cur.execute("INSERT INTO " + self.ADJ_DECLENSIONS + " VALUES(" +
                        str(wid) + ",'" +
                        "Neuter" + "','" +
                        number + "','" +
                        declension[0] + "','" +
                        declension[1] + "','" +
                        declension[2] + "','" +
                        declension[3] + "','" +
                        declension[4] + "');")
        # For each declined adj, add to NameToID
        for number, declension in m_declensions.iteritems():
            for word in declension:
                li = self.__split_alts(word)
                for w in li:
                    if self.__check_name_uniqueness(w):
                        cur.execute("INSERT INTO " + self.NAME_TO_ID + " VALUES('" +
                                    w + "'," + str(wid) + ");")
        for number, declension in f_declensions.iteritems():
            for word in declension:
                li = self.__split_alts(word)
                for w in li:
                    if self.__check_name_uniqueness(w):
                        cur.execute("INSERT INTO " + self.NAME_TO_ID + " VALUES('" +
                                    w + "'," + str(wid) + ");")
        for number, declension in n_declensions.iteritems():
            for word in declension:
                li = self.__split_alts(word)
                for w in li:
                    if self.__check_name_uniqueness(w):
                        cur.execute("INSERT INTO " + self.NAME_TO_ID + " VALUES('" +
                                    w + "'," + str(wid) + ");")
        self.__con.commit()
        return True

'''