# -*- coding: utf-8 -*-

# Sophia Rauh
# Matrikelnummer 790850
# Python 3.9.13
# Windows 10

"""Assigning Discourse Relations and Creating Visual Output"""

import xml.etree.ElementTree as ET
from collections import defaultdict
from copy import deepcopy

import pandas as pd
from nltk.tokenize import RegexpTokenizer


def add_discourse_relation(alignment, source_mapping=dict(),
                           target_mapping=dict()):
    """Adds the discourse relations to both source and target words

    Parameters
    ----------
    alignment : dict
        A dictionary with source keys and a dictionary as value
        which contains the target words with their probabilities
    source_mapping : dict, optional
        A dictionary with the source words as keys and the relations
        in a list as values
    target_mapping : dict, optional
        A dictionary with the target words as keys and the relations
        in a list as values

    Returns
    -------
    rel_alignment : dict
        A dictionary with keys of the form 'word (relation)' for both
        source and target words

    Note: only useful as a visual representation
    """

    rel_alignment = deepcopy(alignment)
    # Adds the relation to the target words
    if target_mapping:
        for source, targets in alignment.items():
            for target in targets.keys():
                if target in target_mapping:
                    relation = f"({', '.join(target_mapping[target])})"
                    with_rel = target + " " + relation
                    probability = rel_alignment[source].pop(target)
                    rel_alignment[source][with_rel] = probability

    # Adds the relation to the source words
    if source_mapping:
        for source, relation in source_mapping.items():
            try:
                relation = f"({', '.join(relation)})"
                rel_alignment[f"{source} {relation}"] = rel_alignment.pop(
                    source)
            except KeyError:
                pass

    return rel_alignment


def assign_relations(doc):
    """Assigns discourse relations to the connectives

    Parameters
    ----------
    doc : str
        Path to the XML file for connectives

    Returns
    -------
    conn_relations : defaultdict
        A dictionary with connectives as keys and relations as
        values
    """

    regex = r"[\w\.]+|\b\w+'|\w+(?:['-]\w+)*|[^\w\s]"
    tokenizer = RegexpTokenizer(regex)

    conn_relations = defaultdict(list)
    root = ET.parse(doc).getroot()
    for entry in root.findall("./entry"):
        # Saves all variants of a connective
        # Single words and phrases (continuous)
        singles_phrases = [variant.text.lower() for variant
                           in entry.findall("./orths/orth[@type='cont']/part")]

        # Removes doubles (because everything is lower-case now)
        singles_phrases = pd.unique(singles_phrases).tolist()
        singles_phrases = [" ".join(tokenizer.tokenize(phrase))
                           for phrase in singles_phrases]

        # Adding connectives with relation to dictionary
        relations = entry.findall("./syn/sem/pdtb3_relation")
        for connective in singles_phrases:
            for relation in relations:
                rel = relation.attrib["sense"]
                try:
                    conn_relations[connective].append(rel)
                except KeyError:
                    pass

        # Same procedure for discontinuous phrases
        discontinuous_phrases = []
        for discont in entry.findall("./orths/orth[@type='discont']"):
            discontinuous = [part.text.lower() for part
                             in discont.findall("./part")]
            discontinuous = [" ".join(tokenizer.tokenize(phrase))
                             for phrase in discontinuous]
            discontinuous = " ... ".join(discontinuous)
            relations = entry.findall("./syn/sem/pdtb3_relation")
            discontinuous_phrases.append(discontinuous)

        discontinuous_phrases = pd.unique(discontinuous_phrases).tolist()
        for discontinuous in discontinuous_phrases:
            for relation in relations:
                rel = relation.attrib["sense"]
                try:
                    conn_relations[discontinuous].append(rel)
                except KeyError:
                    pass

    # Removes relations that occur twice
    for connective, d_relations in conn_relations.items():
        if len(d_relations) > 1:
            conn_relations[connective] = pd.unique(d_relations).tolist()

    return conn_relations
