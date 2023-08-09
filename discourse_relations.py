# -*- coding: utf-8 -*-

"""Assigning Discourse Relations and Creating Visual Output"""

import xml.etree.ElementTree as ET
from collections import defaultdict
from copy import deepcopy

import pandas as pd
import plotly.graph_objects as go
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
    alignment : dict
        A dictionary with keys of the form 'word (relation)' for both
        source and target words

    Note: only useful as a visual representation
    """

    # TODO: check whether this works
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


def filter_for_discourse_relation(conn_lex, conn_rel, relation, rel_mapping):
    """Filter a connective lexicon for a specific discourse relation

    Parameters
    ----------
    conn_lex : list
        List with all connectives of a language
    conn_rel : dict
        Dictionary with connectives as keys and their relations as
        values
    relation : str
        The chosen discourse relation (e.g.: "concession")
    rel_mapping : dict
        Dictionary with groups of relations as keys and their subgroups
        as values
        (e.g.: "concession": "COMPARISON:Concession:Arg1-as-denier")

    Returns
    -------
    filtered_conns : list
        List with all connectives that belong to the chosen relation
    """

    filtered_conns = []
    relations = rel_mapping[relation]
    for conn in conn_lex:
        try:
            if (set(conn_rel[conn]) & set(relations)):
                filtered_conns.append(conn)
        except KeyError:
            pass

    return filtered_conns


def discourse_relation_mapping(alignment, source_mapping, target_mapping):
    """Shows the discourse relations alignment

    Parameters
    ----------
    alignment : dict
        A dictionary with source keys and a dictionary as value
        which contains the target words with their probabilities
    source_mapping : dict
        A dictionary with the source words as keys and the relations
        in a list as values
    target_mapping : dict
        A dictionary with the target words as keys and the relations
        in a list as values

    Returns
    -------
    rel_mapping : dict
        A dictionary showing which relations align with which relations
    """

    rel_mapping = dict()
    # Adds the relation to the target words
    for source, targets in alignment.items():
        if source in source_mapping:
            source_rel = []
            for rel in source_mapping[source]:
                if ":" in rel:
                    first_index = rel.find(":")
                    rel = rel[first_index+1:]
                # Remove the information about arg1/arg2
                if ":" in rel:
                    second_index = rel.find(":")
                    rel = rel[:second_index]
                source_rel.append(rel.capitalize())
            source_rel = set(source_rel)
            source_rel = str(sorted(source_rel))
            if source_rel not in rel_mapping:
                rel_mapping[source_rel] = [1, dict()]
            else:
                # Count how many connectives have this relation
                rel_mapping[source_rel][0] += 1

            for target in targets.keys():
                if target in target_mapping:
                    target_rel = []
                    for rel in target_mapping[target]:
                        if ":" in rel:
                            first_index = rel.find(":")
                            rel = rel[first_index+1:]
                        # Remove the information about arg1/arg2
                        if ":" in rel:
                            second_index = rel.find(":")
                            rel = rel[:second_index]
                        target_rel.append(rel.capitalize())
                    target_rel = set(target_rel)
                    target_rel = str(sorted(target_rel))
                    target_dict = rel_mapping[source_rel][1]
                    if target_rel not in target_dict:
                        target_dict[target_rel] = alignment[source][target]
                    else:
                        target_dict[target_rel] += alignment[source][target]

    # Calculate the proportion of the relations aligned
    for source, targets in rel_mapping.items():
        total = sum(targets[1].values())
        for target in targets[1].keys():
            rel_dict = rel_mapping[source][1]
            rel_dict[target] = rel_dict[target] / total

    return rel_mapping


def create_sankey_diagram(alignments, lang1, lang2, rel, file_name):
    """Creates a sankey diagram that shows the discourse relation
    mapping from lang1 to lang2

    Parameters
    ----------
    alignments : dict
        A dictionary with the mapping of the discourse relations
    lang1 : str
        A string that represents a language, included in the labels
    lang2 : str
        A string that represents a language, included in the labels
    rel : str
        A string with the discourse relation type, included in title
    file_name : str
        A string for the name of the png file to be created

    Creates the sankey diagram as a png file
    """

    rel_labels = []
    source_indices = []
    target_indices = []
    values = []

    # Add labels for the sankey diagram
    for source, targets in alignments.items():
        rel_labels.append(f"{lang1}: {source}")
        for target in targets[1].keys():
            rel_labels.append(f"{lang2}: {target}")
    rel_labels = pd.unique(rel_labels).tolist()

    # Adds the index of source and target
    for source, targets in alignments.items():
        source_index = rel_labels.index(f"{lang1}: {source}")
        for target in targets[1].keys():
            target_index = rel_labels.index(f"{lang2}: {target}")
            source_indices.append(source_index)
            target_indices.append(target_index)
            values.append(alignments[source][1][target]
                          * alignments[source][0])

    for index in range(len(rel_labels)):
        rel_labels[index] = rel_labels[index].replace("'", "")
        rel_labels[index] = rel_labels[index].replace("[", "")
        rel_labels[index] = rel_labels[index].replace("]", "")

    colours = ["rgba(77, 130, 219, 0.5)",
               "rgba(155, 222, 130, 0.5)",
               "rgba(91, 192, 219, 0.5)",
               "rgba(193, 131, 189, 0.5)",
               "rgba(54, 145, 145, 0.4)",
               "rgba(177, 101, 145, 0.5)",
               "rgba(54, 145, 47, 0.6)",
               "rgba(54, 51, 101, 0.6)",
               "rgba(187, 211, 101, 0.6)",
               "rgba(187, 101, 145, 0.6)",
               "rgba(230, 121, 121, 0.5)",
               "rgba(255, 174, 105, 0.5)",
               "rgba(255, 255, 105, 0.5)",
               "rgba(145, 222, 130, 0.5)",
               "rgba(125, 214, 181, 0.5)",
               "rgba(196, 145, 145, 0.6)",
               "rgba(44, 145, 145, 0.6)",
               "rgba(177, 211, 101, 0.6)",
               "rgba(44, 145, 47, 0.6)",
               "rgba(142, 116, 206, 0.5)",
               "rgba(44, 51, 101, 0.6)",
               "rgba(101, 192, 219, 0.6)",
               "rgba(87, 130, 219, 0.6)",
               "rgba(152, 116, 206, 0.5)",
               "rgba(203, 131, 189, 0.5)",
               "rgba(240, 121, 121, 0.5)",
               "rgba(265, 174, 105, 0.5)",
               "rgba(265, 255, 105, 0.5)",
               "rgba(135, 214, 181, 0.5)",
               "rgba(206, 145, 145, 0.6)"]

    colour_mapping = dict()
    for index, rel_id in enumerate(pd.unique(source_indices).tolist()):
        colour_mapping[rel_id] = colours[index]

    colour = []
    for source_id in source_indices:
        colour.append(colour_mapping[source_id])

    fig = go.Figure(data=[go.Sankey(
        node=dict(
          pad=15,
          thickness=20,
          line=dict(color="black", width=0.5),
          label=rel_labels,
          color="midnightblue"
        ),
        link=dict(
          source=source_indices,
          target=target_indices,
          value=values,
          color=colour
         ))])

    fig.update_layout(
        title_text=f"{lang1}-{lang2} {rel.capitalize()} Sankey Diagram",
        font_size=30, width=3000, height=2000,)

    fig.write_image(file_name)


def assign_relations(doc, mapping):
    """Assigns PDTB relations to the connectives

    Parameters
    ----------
    doc : str
        Path to the XML file for connectives
    mapping : str
        Path to a JSON file with the mapping

    Returns
    -------
    pdtb : defaultdict
        A dictionary with connectives as keys and relations as
        values
    """

    # TODO: Mapping not needed for Italian, but for German

    regex = r"[\w\.]+|\b\w+'|\w+(?:['-]\w+)*|[^\w\s]"
    tokenizer = RegexpTokenizer(regex)

    # Dictionary that contains the mapping
    # pdtb: contracted form -> detailed form
    mapping = json_to_dict(mapping)
    pdtb = defaultdict(list)
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

        # Adding connectives with pdtb relation to dictionary
        relations = entry.findall("./syn/sem/pdtb3_relation")
        for connective in singles_phrases:
            for relation in relations:
                rel = relation.attrib["sense"]
                try:
                    pdtb[connective].append(rel)
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
                    pdtb[discontinuous].append(rel)
                except KeyError:
                    pass

    # Removes relations that occur twice (due to the mapping to
    # multiple relations from sdrt to pdtb)
    for connective, pdtb_relations in pdtb.items():
        if len(pdtb_relations) > 1:
            pdtb[connective] = pd.unique(pdtb_relations).tolist()

    return pdtb


if __name__ == "__main__":
    from pathlib import Path
    from processing_filtering import json_to_dict, save_alignments
    it_rel = json_to_dict(
        Path("connectives_and_relations/it_relations.json"))
    it_es_conns = json_to_dict(Path("it_es_connectives_alignment.json"))
    es_it_conns = json_to_dict(Path("es_it_connectives_alignment.json"))
    es_it = add_discourse_relation(es_it_conns, target_mapping=it_rel)
    it_es = add_discourse_relation(it_es_conns, source_mapping=it_rel)
    save_alignments("es_it_rel_ex.json", es_it)
    save_alignments("it_es_rel_ex.json", it_es)

    # rel = json_to_dict(Path("connectives_and_relations/relations.json"))
    # mapping = assign_relations(
    #     Path("connectives_and_relations/lico_d.xml"),
    #     Path("connectives_and_relations/relations.json"))
    # save_alignments("it_relations.json", mapping)
