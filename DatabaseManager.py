# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import sqlite3 as sql
import Utils


# Class that handles queries to the lexicon
class Lexicon:
    __conn = None
    __current_id = 0

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
    PART_FORM_TABLE = "ParticipleForms"

    def __init__(self, db_path):
        try:
            self.__conn = sql.connect(db_path)
            self.__conn.text_factory = lambda x: str(x, "utf-8")
            self.__conn.text_factory = str
            cur = self.__conn.cursor()
            cur.execute("PRAGMA foreign_keys = 1;")
            self.__conn.commit()
            cur.execute("")
        except sql.Error, e:
            print "Error %s: " % e.args[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__conn:
            self.__conn.close()

    def reset(self):
        # Erase everything in the database
        cur = self.__conn.cursor()
        cur.execute("DELETE FROM WordForms;")
        cur.execute("DELETE FROM Words;")
        self.__conn.commit()

    def insert(self, word, pos, form=None, is_form=False):
        # is_form will tell us whether it is a specific word, or a word form.
        if is_form and form is None:
            print "Form is required when inserting an individual word."
            return False
        if pos == Utils.PartOfSpeech.NOUN.value:  # Nouns
            print "Inserting noun"
            return self.__insert_noun_form(word) if is_form else self.__insert_noun(word, form)
        elif pos == Utils.PartOfSpeech.VERB.value:  # Verbs
            print "Inserting verb"
            return self.__insert_verb_form(word) if is_form else self.__insert_verb(word, form)
        elif pos == Utils.PartOfSpeech.ADJECTIVE.value:  # Adjectives
            print "Inserting adjective"
            return self.__insert_adj_form(word) if is_form else self.__insert_adj(word, form)
        elif pos == Utils.PartOfSpeech.PRONOUN.value:  # Pronouns
            print "Inserting pronoun"
            return self.__insert_pronoun_form(word) if is_form else self.__insert_pronoun(word, form)
        elif pos == Utils.PartOfSpeech.PARTICIPLE.value:
            print "Inserting participle"
            return False if is_form else self.__insert_participle(word, form)
        else:  # Others
            print "Inserting other words"

    def __insert_noun(self, noun, form):
        # Noun is a container that holds everything...
        # It is a list, where each index is an info parameter
        # So it has:
            # 0: Word String
            # 1: Case
            # 2: Number
            # 3: Gender

        # Check if the Word Form exists --This must exist, or else fail
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.NOUN)
        if form_id is None:
            return False

        # Get the next local ID (the max value of local IDs for the Form ID
        word_id = self.__get_local_id(form_id)

        # Insert into Words --Name, Local Id, Form Id, Part of Speech
        self.__sql_insert_words(noun[0], word_id, form_id, Utils.PartOfSpeech.NOUN)

        # Insert into Nouns -- Local ID, Form ID, 1, 2, 3 of Noun[]
        self.__sql_insert_nouns(word_id, form_id, noun[1], noun[2], noun[3])
        self.__conn.commit()
        return True

    def __insert_noun_form(self, noun):
        # Noun has:
            # 0: Nominative Word
            # 1: Genitive Word
            # 2: Article
            # 3: Gender
            # 4: Major Declension
            # 5: Minor Declension
            # 6: Irregularity
            # 7: Definitions

        # Check if the Word Form exists --it shouldn't exist or else we are re-adding
        form_id = self.__get_form_id(noun[:3], Utils.PartOfSpeech.NOUN)
        if form_id is not None:
            return False

        # Get the next Form ID
        form_id = self.__get_next_form_id()

        # Insert into WordForms --FormID, pos
        self.__sql_insert_word_forms(form_id, Utils.PartOfSpeech.NOUN)

        # Insert into NounForms --Nominative, Genitive, Article, Gender, Dec, Dec2, Irr
        self.__sql_insert_noun_forms(form_id, noun[0], noun[1], noun[2], noun[3], noun[4], noun[5], noun[6])

        # Insert into Definitions
        definitions = noun[7]
        for d in definitions:
            self.__sql_insert_definition(form_id, d)
        self.__conn.commit()
        return True

    def __insert_verb(self, verb, form):
        # Verb has:
            # 0: Word String
            # 1: Person
            # 2: Number
            # 3: Tense
            # 4: Voice
            # 5: Mood

        # Check if word form exists
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.VERB)
        if form_id is None:
            return False

        for v, i in verb.iteritems():
            # Get next local ID

            word_id = self.__get_local_id(form_id)
            self.__sql_insert_words(v, word_id, form_id, Utils.PartOfSpeech.VERB)
            self.__sql_insert_verbs(word_id, form_id, i[0], i[1], i[2], i[3], i[4])
        self.__conn.commit()
        return True

    def __insert_verb_form(self, verb):
        # Verb Form has:
            # 0: First
            # 1: Second
            # 2: Third
            # 3: Fourth
            # 4: Fifth
            # 5: Sixth
            # 6: Ending Type
            # 7: Contraction Type
            # 8: Aorist Type
            # 9: Perfect Type
            # 10: Irregularity
            # 11: Definitions

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
        definitions = verb[11]
        for d in definitions:
            self.__sql_insert_definition(form_id, d)
        self.__conn.commit()
        return True

    def __insert_adj(self, adj, form):
        # Adj has:
            # 0: Word String
            # 1: Case
            # 2: Number
            # 3: Gender

        # Check for Word Form
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.ADJECTIVE)
        if form_id is None:
            return False

        # Get next local ID
        word_id = self.__get_local_id(form_id)

        # Insert into Words
        self.__sql_insert_words(adj[0], word_id, form_id, Utils.PartOfSpeech.ADJECTIVE)

        # Insert into Adjectives
        self.__sql_insert_adj(word_id, form_id, adj[1], adj[2], adj[3])
        self.__conn.commit()
        return True

    def __insert_adj_form(self, adj):
        # Adj Form has:
            # 0: Masculine
            # 1: Feminine
            # 2: Neuter
            # 3: Major
            # 4: Minor
            # 5: Irregularity
            # 6: Definitions

        # Check for Word Form
        form_id = self.__get_form_id(adj[:3], Utils.PartOfSpeech.ADJECTIVE)
        if form_id is not None:
            return False

        # Get next Form ID
        form_id = self.__get_next_form_id()

        # Insert into Word Forms
        self.__sql_insert_word_forms(form_id, Utils.PartOfSpeech.ADJECTIVE)

        # Insert into Adj Forms
        self.__sql_insert_adj_forms(form_id, adj[1], adj[2], adj[3], adj[4], adj[5], adj[6])

        # Insert into Definitions
        definitions = adj[7]
        for d in definitions:
            self.__sql_insert_definition(form_id, d)
        self.__conn.commit()
        return True

    def __insert_pronoun(self, pro, form):
        # Pronoun
            # 0: Word String
            # 1: Case
            # 2: Number
            # 3: Gender
            # 4: Person

        # Check for Word Form
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.PRONOUN)
        if form_id is None:
            return False

        # Get next local ID
        word_id = self.__get_local_id(form_id)

        # Insert into Words
        self.__sql_insert_words(pro[0], word_id, form_id, Utils.PartOfSpeech.PRONOUN)

        # Insert into Adjectives
        self.__sql_insert_pro(word_id, form_id, pro[1], pro[2], pro[3], pro[4])
        self.__conn.commit()
        return True

    def __insert_pronoun_form(self, pro):
        # Pronoun Form
            # 0: Masculine
            # 1: Feminine
            # 2: Neuter
            # 3: Person
            # 4: Type
            # 5: Definitions

        # Check for Word Form
        form_id = self.__get_form_id(pro[:3], Utils.PartOfSpeech.PRONOUN)
        if form_id is not None:
            return False

        # Get next Form ID
        form_id = self.__get_next_form_id()

        # Insert into Word Forms
        self.__sql_insert_word_forms(form_id, Utils.PartOfSpeech.PRONOUN)

        # Insert into Adj Forms
        self.__sql_insert_pro_forms(form_id, pro[1], pro[2], pro[3], pro[4])

        # Insert into Definitions
        definitions = pro[5]
        for d in definitions:
            self.__sql_insert_definition(form_id, d)
        self.__conn.commit()
        return True

    def __insert_participle(self, part, form):
        # Participle
            # 0: Word String
            # 1: Case
            # 2: Number
            # 3: Gender
            # 4: Tense
            # 5: Voice

        # Check for Word Form
        form_id = self.__get_form_id(form, Utils.PartOfSpeech.PARTICIPLE)
        if form_id is None:
            return False

        # Get next local ID
        word_id = self.__get_local_id(form_id)

        # Insert into Words
        self.__sql_insert_words(part[0], word_id, form_id, Utils.PartOfSpeech.PARTICIPLE)

        # Insert into Adjectives
        self.__sql_insert_part(word_id, form_id, part[1], part[2], part[3], part[4], part[5])
        self.__conn.commit()
        return True

    # Select Query Helpers
    # Form ID Select Methods
    def __get_form_id(self, form, pos):
        if pos == Utils.PartOfSpeech.NOUN:  # Nouns
            print "Get Form ID of a noun"
            return self.__get_form_id_noun(form)
        elif pos == Utils.PartOfSpeech.VERB:  # Verbs
            print "Get Form ID of a verb"
            return self.__get_form_id_verb(form)
        elif pos == Utils.PartOfSpeech.ADJECTIVE:  # Adjectives
            print "Get Form ID of an adjective"
            return self.__get_form_id_adj(form)
        elif pos == Utils.PartOfSpeech.PRONOUN:  # Pronouns
            print "Get Form ID of a pronoun"
            return self.__get_form_id_pro(form)
        else:  # Others
            print "Get Form ID of another word"

    def __get_form_id_noun(self, form):
        cur = self.__conn.cursor()
        cur.execute("SELECT * FROM " + self.NOUN_FORM_TABLE + " WHERE " +
                    self.NOUN_FORM_TABLE + ".Nominative == " + form[0] + " AND " +
                    self.NOUN_FORM_TABLE + ".Genitive == " + form[1] + " AND " +
                    self.NOUN_FORM_TABLE + ".Article == " + form[2] + ";")
        data = cur.fetchone()  # There should be only one form or None
        return data[0] if data is not None else None

    def __get_form_id_verb(self, form):
        cur = self.__conn.cursor()
        cur.execute("SELECT * FROM " + self.VERB_FORM_TABLE + " WHERE " +
                    self.VERB_FORM_TABLE + ".FirstPrincipalPart == '" + form[0] + "' AND " +
                    self.VERB_FORM_TABLE + ".SecondPrincipalPart == '" + form[1] + "' AND " +
                    self.VERB_FORM_TABLE + ".ThirdPrincipalPart == '" + form[2] + "' AND " +
                    self.VERB_FORM_TABLE + ".FourthPrincipalPart == '" + form[3] + "' AND " +
                    self.VERB_FORM_TABLE + ".FifthPrincipalPart == '" + form[4] + "' AND " +
                    self.VERB_FORM_TABLE + ".SixthPrincipalPart == '" + form[5] + "';")
        data = cur.fetchone()  # There should be only one form or None
        return data[0] if data is not None else None

    def __get_form_id_adj(self, form):
        cur = self.__conn.cursor()
        cur.execute("SELECT * FROM " + self.ADJ_FORM_TABLE + " WHERE " +
                    self.ADJ_FORM_TABLE + ".Masculine == " + form[0] + " AND " +
                    self.ADJ_FORM_TABLE + ".Feminine == " + form[1] + " AND " +
                    self.ADJ_FORM_TABLE + ".Neuter == " + form[2] + ";")
        data = cur.fetchone()  # There should be only one form or None
        return data[0] if data is not None else None

    def __get_form_id_pro(self, form):
        cur = self.__conn.cursor()
        cur.execute("SELECT * FROM " + self.PRO_FORM_TABLE + " WHERE " +
                    self.PRO_FORM_TABLE + ".Masculine == " + form[0] + " AND " +
                    self.PRO_FORM_TABLE + ".Feminine == " + form[1] + " AND " +
                    self.PRO_FORM_TABLE + ".Neuter == " + form[2] + ";")
        data = cur.fetchone()  # There should be only one form or None
        return data[0] if data is not None else None

    # Word ID Select Method
    def __get_local_id(self, form_id):
        cur = self.__conn.cursor()
        cur.execute("SELECT MAX(WordID) FROM " + self.WORD_TABLE + " WHERE " +
                    self.WORD_TABLE + ".FormID == " + str(form_id) + ";")
        data = cur.fetchone()  # There should be only one
        return data[0] + 1 if data[0] is not None else 0

    # Next Form ID Select Method
    def __get_next_form_id(self):
        cur = self.__conn.cursor()
        cur.execute("SELECT MAX(FormID) FROM " + self.WORD_FORM_TABLE + ";")
        data = cur.fetchone()
        return (data[0] + 1) if data[0] is not None else 0

    # SQL Insert Methods
    def __sql_insert_definition(self, form_id, definition):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.DEF_TABLE + " VALUES( " +
                    str(form_id) + ", '" +
                    definition + "');")

    def __sql_insert_words(self, name, word_id, form_id, pos):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.WORD_TABLE + " VALUES( " +
                    str(word_id) + ", " +
                    str(form_id) + ", '" +
                    pos.value + "', '" +
                    name + "', '" +
                    self.__deaccentuate(name) + "');")

    def __sql_insert_nouns(self, word_id, form_id, case, number, gender):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.NOUN_TABLE + " VALUES( " +
                    word_id + ", " +
                    form_id + ", " +
                    case + ", " +
                    number + ", " +
                    gender + ");")

    def __sql_insert_verbs(self, word_id, form_id, person, number, tense, voice, mood):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.VERB_TABLE + " VALUES( " +
                    str(word_id) + ", " +
                    str(form_id) + ", '" +
                    person + "', '" +
                    number + "', '" +
                    tense + "', '" +
                    voice + "', '" +
                    mood + "');")

    def __sql_insert_adj(self, word_id, form_id, case, number, gender):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.ADJ_TABLE + " VALUES( " +
                    word_id + ", " +
                    form_id + ", " +
                    case + ", " +
                    number + ", " +
                    gender + ");")

    def __sql_insert_pro(self, word_id, form_id, case, number, gender, person, kind):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.VERB_TABLE + " VALUES( " +
                    word_id + ", " +
                    form_id + ", " +
                    case + ", " +
                    number + ", " +
                    gender + ", " +
                    person + ", " +
                    kind + ", " + ");")

    def __sql_insert_part(self, word_id, form_id, case, number, gender, tense, voice):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.VERB_TABLE + " VALUES( " +
                    word_id + ", " +
                    form_id + ", " +
                    case + ", " +
                    number + ", " +
                    gender + ", " +
                    tense + ", " +
                    voice + ", " + ");")

    def __sql_insert_word_forms(self, form_id, pos, c):
        cur = self.__conn.cursor()

        cur.execute("INSERT INTO " + self.WORD_FORM_TABLE + " VALUES( " +
                    str(form_id) + ", '" +
                    pos.value + "', " +
                    str(c) + ");")

    def __sql_insert_noun_forms(self, form_id, nominative, genitive, article, gender, major, minor, irr):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.NOUN_FORM_TABLE + " VALUES( " +
                    form_id + ", " +
                    nominative + ", " +
                    genitive + ", " +
                    article + ", " +
                    gender + ", " +
                    major + ", " +
                    minor + ", " +
                    irr + ");")

    def __sql_insert_verb_forms(self, form_id, first, second, third, fourth, fifth, sixth, ending, contract, aorist, perfect, deponent, irr):
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

    def __sql_insert_adj_forms(self, form_id, masculine, feminine, neuter, major, minor, irr):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.NOUN_FORM_TABLE + " VALUES( " +
                    form_id + ", " +
                    masculine + ", " +
                    feminine + ", " +
                    neuter + ", " +
                    major + ", " +
                    minor + ", " +
                    irr + ");")

    def __sql_insert_pro_forms(self, form_id, masculine, feminine, neuter, person, irr):
        cur = self.__conn.cursor()
        cur.execute("INSERT INTO " + self.NOUN_FORM_TABLE + " VALUES( " +
                    form_id + ", " +
                    masculine + ", " +
                    feminine + ", " +
                    neuter + ", " +
                    person + ", " +
                    irr + ");")

    def __deaccentuate(self, word):
        return word # Change each accented (including breathing marks) letters into unaccented versions. If there is a standalone accent, leave as is

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