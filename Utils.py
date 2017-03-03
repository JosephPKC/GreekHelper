from enum import Enum


class PartOfSpeech(Enum):
    NOUN = "Noun"
    VERB = "Verb"
    ADJECTIVE = "Adjective"
    PRONOUN = "Pronoun"
    PARTICIPLE = "Participle"
    ADVERB = "Adverb"
    PREPOSITION = "Preposition"
    CONJUNCTION = "Conjunction"
    PARTICLE = "Particle"
    ARTICLE = "Article"


class Error(Enum):
    """
    Enumeration Class for Errors
    Values are integers.
    """
    SUCCESS = 0
    QUIT = -1
    UNKNOWN_COMMAND = 1     # Command is not of the Command Class
    UNKNOWN_PARAMETER = 2   # Parameter is not of the Parameter Class
    BAD_INSERT = 3          # An SQL Insert Error.
    WORD_NOT_FOUND = 4
    BAD_ARGS = 5
