# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import sqlite3 as sql


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
                    " WHERE " + self.DEFINITIONS + ".WordID == " + str(wid[0]) + ";")
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

