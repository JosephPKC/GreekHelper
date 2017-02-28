# -*- coding: UTF-8 -*-
from __future__ import print_function
import LexiconSearcher as LS

if __name__ == "__main__":

    db = "Lexicon.db"
    with LS.LexiconSearcher(db) as ls:
        ls.run_searcher()




