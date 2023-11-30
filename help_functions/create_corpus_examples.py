# -*- coding: utf-8 -*-

# Sophia Rauh
# Matrikelnummer 790850
# Python 3.9.13
# Windows 10

"""Creating a subcorpus for connective pairs"""

import os
from linecache import getline
from pathlib import Path


def create_comparison_files(source_corpus, target_corpus,
                            source_conn, target_conn):
    """Creates a new directory with files with sentences that contain
    a source-target pair

    Parameters
    ----------
    source_corpus : str
        The path to the text file with the source corpus
    target_corpus : str
        The path to the text file with the target corpus
    source_conn : str
        Source connective for the source-target pair
    target_conn : str
        Target connective for the source-target pair

    Returns
    -------
    None
    """

    sentences = []

    # Reads each sentence of the parallel corpus and searches for the
    # pair of connectives
    with open(source_corpus, "r", encoding="utf-8") as source,\
            open(target_corpus, "r", encoding="utf-8") as target:
        for index, (s, t) in enumerate(zip(source, target)):
            source = s.split()
            target = t.split()
            # Exclude phrases with more then 25 words
            if len(source) > 25 or len(source) > 25:
                continue

            # One word connective
            if len(source_conn) == 1:
                cond1 = source_conn in source
                if not cond1:
                    continue
            # Continuous phrases
            elif "..." not in source_conn:
                part1 = all([conn in source for conn in source_conn.split()])
                part2 = source_conn in s
                cond1 = part1 and part2
            # Discontinuous phrases
            else:
                for word in source_conn.split(" ... "):
                    if source_conn.replace(" ... ", " ") in s:
                        break
                    if word not in source:
                        cond1 = False
                        break
                    cond1 = True

            # One word connective
            if len(target_conn) == 1:
                cond2 = target_conn in target
                if not cond2:
                    continue
            # Continuous phrases
            elif "..." not in target_conn:
                part1 = all([conn in target for conn in target_conn.split()])
                part2 = target_conn in t
                cond2 = part1 and part2
            # Discontinuous phrases
            else:
                for word in target_conn.split(" ... "):
                    if target_conn.replace(" ... ", " ") in t:
                        break
                    if word not in target:
                        cond2 = False
                        break
                    cond2 = True

            # If the source connective is in the source sentence
            # and the target connective is in the target sentence
            if cond1 and cond2:
                source_ = "_".join(source_conn.split())
                target_ = "_".join(target_conn.split())
                key = f"{source_}-{target_}"

                # Save preceding and following sentence as context
                s_p = getline(source_corpus, index).strip()
                s_n = getline(source_corpus, index+2).strip()
                t_p = getline(target_corpus, index).strip()
                t_n = getline(target_corpus, index+2).strip()
                s = s.strip()
                t = t.strip()
                with_context = f"{s_p} {s} {s_n} ||| {t_p} {t} {t_n}"
                sentences.append(with_context)

    if sentences:
        # Create directory
        dir_name = "example_sentences"
        try:
            # Create target Directory
            os.mkdir(dir_name)
        except FileExistsError:
            pass

        with open(Path(f"{dir_name}/{key}.txt"), "w",
                  encoding="utf-8") as file:
            for aligned_sentence in sentences:
                file.write(aligned_sentence + "\n\n")
    else:
        print("No output")
