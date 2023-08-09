#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tokenize the Spanish and Italian Corpora"""

import json
import re
from collections import Counter
from pathlib import Path

from nltk import RegexpTokenizer

ROM_NUM = (r"\bI{1,2}\.|\bI?V\.|\bVI{1,3}\.|\bI?X\.|\bXI{1,3}\.|\bXI?V\.|"
           r"\bXVI{1,3}\.|\bXI?X\.|\bi{1,3}\.|\bi?v\.|\bvi{1,3}\.|\bi?x\.|"
           r"\bxi{1,3}\.|\bxi?v\.|\bxvi{1,3}\.|\bxi?x\.")
INITIALS = r"\b[A-Z]\.[A-Z]\.[A-Z]\.|\b[A-Z]\.[A-Z]\.|\b[A-Z]\."
NUMS = r"\d{1,3}\.\d{3}\.\d{3}|\d{1,3}\.\d{3}"
DATE = r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2,4}|[0-9]{1,2}\.[0-9]{1,2}"
GENERAL = r"\w+(?:['-]\w+)*|[^\w\s]"


def tokenize_italian(file, name):
    it_abbr = (r"\becc\.|\bu\.s\.|\bcfr\.|\bp\.m\.|\bdef\.|\b[Oo]n\.|\bSt\.|"
               r"\bart\.|\bdoc\.|\bonn\.|\b[Rr]ef\.|\b[dD]r\.|\bpag\.|"
               r"\b[Pp]rof\.|\b[Ss]ig\.|\b[Ss]ig\.ra|\b[dD]ott\.|\ba\.m\.|"
               r"\bn{1,2}\.|\b\w+'")
    regex = "|".join([ROM_NUM, INITIALS, NUMS, DATE, it_abbr, GENERAL])
    symbols = []
    tokenizer = RegexpTokenizer(regex)
    with open(file, "r", encoding="utf-8") as file,\
            open(name, "w", encoding="utf-8") as tokenized:
        for pos, line in enumerate(file):
            # if pos == 10000:
            #     break
            line = line.replace("’", "'")
            if "?" in line:
                line = re.sub(r"(\w+)\?(\w+)", r"\1'\2", line)
            tokenized.write(" ".join(tokenizer.tokenize(line)).strip() + "\n")

            symbols += [letter for letter in line]
    with open("it_symbols.json", "w", encoding="utf-8") as file:
        json.dump(Counter(symbols), file, indent=4, ensure_ascii=False)


def tokenize_spanish(file, name):
    es_abbr = (r"\b[Ss]r[as]?\.|\betc\.|\bgrs\.|\b[Cc]f\.|\bp\.m\.|\bVd\.|"
               r"\ba\.m\.|\bUE-EE\.UU\.|\bEE\.UU\.?|\bNN\.UU\.?|\bDr\.|"
               r"\bnúm\.|\bSt\.|\bpág\.|\b[Pp]rof\.")
    symbols = []
    regex = "|".join([ROM_NUM, INITIALS, NUMS, DATE, es_abbr, GENERAL])
    tokenizer = RegexpTokenizer(regex)
    with open(file, "r", encoding="utf-8") as file,\
            open(name, "w", encoding="utf-8") as tokenized:
        for pos, line in enumerate(file):
            # if pos == 10000:
            #     break
            line = line.replace("EE. UU", "EE.UU")
            line = line.replace("EE UU", "EEUU")
            tokenized.write(" ".join(tokenizer.tokenize(line)).strip() + "\n")
            symbols += [letter for letter in line]
    with open("es_symbols.json", "w", encoding="utf-8") as file:
        json.dump(Counter(symbols), file, indent=4, ensure_ascii=False)


def symbols_german(file):
    symbols = []
    with open(file, "r", encoding="utf-8") as file:
        for line in file:
            symbols += [letter for letter in line]
    with open("de_symbols.json", "w", encoding="utf-8") as file:
        json.dump(Counter(symbols), file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    tokenize_italian(Path("corpora/de-it.txt/Europarl.de-it.it.txt"),
                     "europarl_de-it_it_tok.txt")
    tokenize_spanish(Path("corpora/de-es.txt/Europarl_de_es.txt"),
                     "europarl_de-es_es_tok.txt")
    # symbols_german(Path("corpora/de-es.txt/Europarl_de.txt"))
