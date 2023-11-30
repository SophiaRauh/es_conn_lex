# -*- coding: utf-8 -*-

# Sophia Rauh
# Matrikelnummer 790850
# Python 3.9.13
# Windows 10

"""Tokenize the Spanish and Italian Corpora"""

import re

from nltk import RegexpTokenizer


ROM_NUM = (r"\bI{1,2}\.|\bI?V\.|\bVI{1,3}\.|\bI?X\.|\bXI{1,3}\.|\bXI?V\.|"
           r"\bXVI{1,3}\.|\bXI?X\.|\bi{1,3}\.|\bi?v\.|\bvi{1,3}\.|\bi?x\.|"
           r"\bxi{1,3}\.|\bxi?v\.|\bxvi{1,3}\.|\bxi?x\.")
INITIALS = r"\b[A-Z]\.[A-Z]\.[A-Z]\.|\b[A-Z]\.[A-Z]\.|\b[A-Z]\."
NUMS = r"\d{1,3}\.\d{3}\.\d{3}|\d{1,3}\.\d{3}"
DATE = r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2,4}|[0-9]{1,2}\.[0-9]{1,2}"
GENERAL = r"\w+(?:['-]\w+)*|[^\w\s]"


def tokenize_italian(file, name):
    """Tokenizes an Italian text and saves it in a new file

    Parameters
    ----------
    file : str
        The path to the text file with an Italian text
    name : str
        The file name for the new tokenized text

    Returns
    -------
    None
    """

    it_abbr = (r"\becc\.|\bu\.s\.|\bcfr\.|\bp\.m\.|\bdef\.|\b[Oo]n\.|\bSt\.|"
               r"\bart\.|\bdoc\.|\bonn\.|\b[Rr]ef\.|\b[dD]r\.|\bpag\.|"
               r"\b[Pp]rof\.|\b[Ss]ig\.|\b[Ss]ig\.ra|\b[dD]ott\.|\ba\.m\.|"
               r"\bn{1,2}\.|\b\w+'")
    regex = "|".join([ROM_NUM, INITIALS, NUMS, DATE, it_abbr, GENERAL])
    tokenizer = RegexpTokenizer(regex)

    with open(file, "r", encoding="utf-8") as file,\
            open(name, "w", encoding="utf-8") as tokenized:
        for pos, line in enumerate(file):
            line = line.replace("’", "'")
            if "?" in line:
                line = re.sub(r"(\w+)\?(\w+)", r"\1'\2", line)
            tokenized.write(" ".join(tokenizer.tokenize(line)).strip() + "\n")


def tokenize_spanish(file, name):
    """Tokenizes a Spanish text and saves it in a new file

    Parameters
    ----------
    file : str
        The path to the text file with a Spanish text
    name : str
        The file name for the new tokenized text

    Returns
    -------
    None
    """

    es_abbr = (r"\b[Ss]r[as]?\.|\betc\.|\bgrs\.|\b[Cc]f\.|\bp\.m\.|\bVd\.|"
               r"\ba\.m\.|\bUE-EE\.UU\.|\bEE\.UU\.?|\bNN\.UU\.?|\bDr\.|"
               r"\bnúm\.|\bSt\.|\bpág\.|\b[Pp]rof\.")
    regex = "|".join([ROM_NUM, INITIALS, NUMS, DATE, es_abbr, GENERAL])
    tokenizer = RegexpTokenizer(regex)

    with open(file, "r", encoding="utf-8") as file,\
            open(name, "w", encoding="utf-8") as tokenized:
        for pos, line in enumerate(file):
            line = line.replace("EE. UU", "EE.UU")
            line = line.replace("EE UU", "EEUU")
            tokenized.write(" ".join(tokenizer.tokenize(line)).strip() + "\n")
