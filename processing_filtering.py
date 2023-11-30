# -*- coding: utf-8 -*-

# Sophia Rauh
# Matrikelnummer 790850
# Python 3.9.13
# Windows 10

"""Preprocessing of the data"""

import json
import pandas as pd
import string
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from copy import deepcopy

from nltk.tokenize import RegexpTokenizer


def filter_most_common_conns(dictionary, word_threshold, phrase_threshold):
    """Removes alignments with a probability less than the threshold

    Parameters
    ----------
    dictionary : dict
        The alignment with probabilities
    threshold : float
        The minimum probability an alignment has to have

    Returns
    -------
    filtered : dict
        The alignment without the values less than the threshold
    """

    filtered = deepcopy(dictionary)
    for source, target in dictionary.items():
        for conn, count in target.items():
            if len(conn.split()) == 1:
                if count < word_threshold:
                    del filtered[source][conn]
            if len(conn.split()) > 1:
                if count < phrase_threshold:
                    del filtered[source][conn]

    return filtered


def remove_low_counts(prob_dict, count_dict, word_count, phrase_count):
    """Removes the alignments with a number that is too low

    Parameters
    ----------
    prob_dict : dict
        The probabilities of alignments
    count_dict : dict
        The counts of alignments
    word_count : int
        The minimum number for an alignment (for single words)
    phrase_count : int
        The minimum number for an alignment (for phrases)

    Returns
    -------
    filtered_prob_dict : dict
        The probability alignment without the low numbers
    """

    filtered_prob_dict = deepcopy(prob_dict)

    for source, alignment in prob_dict.items():
        for target in alignment.keys():
            if len(target.split()) == 1:
                if count_dict[source][target] < word_count:
                    filtered_prob_dict[source].pop(target)
            else:
                if count_dict[source][target] < phrase_count:
                    filtered_prob_dict[source].pop(target)

    return filtered_prob_dict


def conn_count(alignments, lex):
    """Counts the connective alignments and sorts them

    Parameters
    ----------
    alignments : dict
        A dictionary that contains all alignments unsorted and uncounted
    lex : list
        A list with the connectives of a language

    Returns
    -------
    count : dict
        A dictionary with sorted and counted alignments
    """

    count = dict()
    for key in lex:
        try:
            count[key] = Counter(alignments[key])
        except KeyError:
            pass

    return count


def remove_punct_phrases(tokens):
    """Removes punctuation in phrases

    ', weil' -> 'weil'
    Does not remove commas followed by 'dass' or 'daß'

    Parameters
    ----------
    tokens : list
        A list that contains a tokenized sentence

    Returns
    -------
    no_punct_phrases : list
        A list with the tokenized phrase without the punctuation
    tokens : list
        Unchanged list, if the list only contains one word
    """

    punctuation = string.punctuation + "¿"

    no_punct_phrases = tokens
    if len(tokens) > 1:
        if tokens[0] in punctuation:
            no_punct_phrases = tokens[1:]
        if tokens[-1] in punctuation:
            no_punct_phrases = no_punct_phrases[:-1]
        if no_punct_phrases and no_punct_phrases[0] == "...":
            no_punct_phrases = no_punct_phrases[1:]
            # '...' was used to indicate discontinuous phrases
            # If it just separated a comma from a word and is now at
            # the beginning or and of the phrase, it is deleted
        if no_punct_phrases and no_punct_phrases[-1] == "...":
            no_punct_phrases = no_punct_phrases[:-1]
        if not no_punct_phrases:
            return [""]
        return no_punct_phrases
    else:
        return tokens


def save_alignments(file_name, content):
    """Saves a dictionary as a JSON file"""

    with open(file_name, "w",
              encoding="utf-8") as file:
        json.dump(content, file, indent=4,
                  sort_keys=True, ensure_ascii=False)


def remove_punct_values(dictionary):
    """Replaces alignments to a punctuation with an empty string

    Removes ',', '.', etc. in values, but not ', weil'

    Parameters
    ----------
    dictionary : dict
        The unsorted and uncounted alignments

    Returns
    -------
    no_punct : dict
        The alignment without punctuation
    """

    no_punct = defaultdict(list)
    for source, target in dictionary.items():
        for word in target:
            if word and word in string.punctuation:
                no_punct[source].append("")
            else:
                no_punct[source].append(word)
    return no_punct


def alignment_probabilities(alignments):
    """Calculates the probalities of the alignments

    Parameters
    ----------
    alignments : dict
        A dictionary with uncounted and unsorted alignments

    Returns
    -------
    conn_alignments : dict
        A dictionary with the probability of each alignment
    """

    conn_alignments = dict()
    for key in alignments:
        try:
            conn_alignments[key] = Counter(alignments[key])
        except KeyError:
            continue

    for k, v in conn_alignments.items():
        exp = dict()
        for word, count in v.items():
            exp[word] = count / sum(v.values())
        conn_alignments[k] = exp

    return conn_alignments


def read_xml_lex(doc):
    """Filters the ConnLex connectives

    Parameters
    ----------
    doc : str
        Path to the XML file of a connective lexicon

    Returns
    -------
    conn : list
        A list with the connectives
    """

    regex = r"[\w\.]+|\b\w+'|\w+(?:['-]\w+)*|[^\w\s]"
    tokenizer = RegexpTokenizer(regex)

    root = ET.parse(doc).getroot()
    conn = []
    for entry in root.findall("./entry"):
        # Saves all variants of a connective
        # Single words and phrases (continuous)
        singles_phrases = [variant.text.lower() for variant
                           in entry.findall("./orths/orth[@type='cont']/part")]

        # Tokenization: "d'abord" -> "d' abord"
        singles_phrases = [" ".join(tokenizer.tokenize(phrase))
                           for phrase in singles_phrases]
        conn += singles_phrases

        # Same procedure for discontinuous phrases
        for discont in entry.findall("./orths/orth[@type='discont']"):
            discontinuous = [part.text.lower() for part
                             in discont.findall("./part")]
            discontinuous = [" ".join(tokenizer.tokenize(phrase))
                             for phrase in discontinuous]
            discontinuous = " ... ".join(discontinuous)
            conn.append(discontinuous)

    # Removes doubles which exist because everything is lower-case now
    conn = pd.unique(conn).tolist()

    return conn


def read_es_conns(conn_file):
    """Gets Spanish discourse particles from a text file

    Parameters
    ----------
    conn_file : str
        Path to the file with connectives, one connective per line

    Returns
    -------
    conns : list
        A list with the connectives

    Note: Can be used for other languages as well
    """

    conns = []
    with open(conn_file, "r", encoding="utf-8") as file:
        for line in file:
            conns.append(line.strip())
    conns = pd.unique(conns).tolist()

    return conns


def json_to_dict(file):
    """Saves the alignment of the JSON file as a dictionary"""

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data
