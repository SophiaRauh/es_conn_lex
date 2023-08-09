# -*- coding: utf-8 -*-

# Sophia Rauh
# Matrikelnummer 790850
# Python 3.9.13
# Windows 10

"""Parse eflomal alignments"""

import argparse
import pandas as pd
import time
from collections import defaultdict
from copy import deepcopy

# from process_data import remove_contractions
from processing_filtering import remove_punct_phrases, save_alignments


def parse_word_alignments(result, source_sentences, target_sentences):
    """Creates alignments for single words, phrases and discontinous
    phrases based on the eflomal alignment (TODO: explain format)

    Parameters
    ----------
    result : str
        The file name for the eflomal alignment
    german_sentences : str
        The file name for the German corpus
    french_sentences : str
        The file name for the French corpus

    Returns
    -------
    de_fr_alignments: defaultdict
        A dictionary with German keys and the French alignments as
        values
    fr_de_alignments: defaultdict
        A dictionary with French keys and the German alignments as
        values
    """

    start = time.time()  # currently 6 minutes
    lang1_lang2_alignments = defaultdict(list)
    lang2_lang1_alignments = defaultdict(list)

    # pos_ = 0
    with open(result, "r", encoding="utf-8") as result,\
            open(source_sentences, "r", encoding="utf-8") as source,\
            open(target_sentences, "r", encoding="utf-8") as target:
        for index, lang1, lang2 in zip(result, source, target):
            source = lang1.split()
            target = lang2.split()
            alignment = index.split()
            pair = [a.split("-") for a in alignment]
            # pos_ += 1
            # if pos_ == 10:
            #     break

            # Adds an empty string as alignment if there is no
            # alignment for a word
            lang1_missing = list(range(0, len(source)))
            lang2_missing = list(range(0, len(target)))
            for word1, word2 in pair:
                try:
                    lang1_missing.remove(int(word1))
                except ValueError:
                    pass
                try:
                    lang2_missing.remove(int(word2))
                except ValueError:
                    pass

            if lang1_missing:
                for missing in lang1_missing:
                    lang1_lang2_alignments[source[missing]].append("")
            if lang2_missing:
                for missing in lang2_missing:
                    lang2_lang1_alignments[target[missing]].append("")

            # Adds the alignments to dictionaries so that phrases
            # are allowed as well
            phrase_align_lang1_r = defaultdict(list)
            phrase_align_lang2_r = defaultdict(list)
            for p in pair:
                phrase_align_lang1_r[p[0]].append(p[1])
                phrase_align_lang2_r[p[1]].append(p[0])

            # Reverses the pair, so that phrases are allowed as keys
            phrase_align_lang1 = defaultdict(list)
            phrase_align_lang2 = defaultdict(list)
            for k, v in phrase_align_lang2_r.items():
                phrase_align_lang1[tuple(v)].append(k)
            for k, v in phrase_align_lang1_r.items():
                phrase_align_lang2[tuple(v)].append(k)

            # eliminate unsymmetrical alignments
            source_target = set([(key, tuple(value)) for key, value
                                 in phrase_align_lang1.items()])
            target_source_r = set([(tuple(value), key) for key, value
                                   in phrase_align_lang2.items()])
            # TODO: print some examples here for unsymmetricality
            # demonstration
            source_error = list(source_target - target_source_r)
            target_error = list(target_source_r - source_target)
            if source_error and target_error:
                for key, value in source_error:
                    del phrase_align_lang1[key]
                for value, key in target_error:
                    del phrase_align_lang2[key]

            # Identifies discontinous phrases
            # However, seems more like alignment errors
            # For source - target
            for lang1, lang2 in phrase_align_lang1.items():
                if len(lang2) > 1:
                    lang2_original = deepcopy(lang2)
                    for pos in range(len(lang2)-1):
                        if lang2[pos].isnumeric() and lang2[pos+1].isnumeric():
                            if abs(int(lang2[pos]) - int(lang2[pos+1])) == 2:
                                if target[int(lang2[pos])+1] == ",":
                                    phrase_align_lang1[lang1].insert(
                                        pos+1, ",")
                                else:
                                    phrase_align_lang1[lang1].insert(
                                        pos+1, "...")
                            elif abs(int(lang2[pos]) - int(lang2[pos+1])) > 2:
                                phrase_align_lang1[lang1].insert(pos+1, "...")
                    # Change in the other lexicon as well if
                    # something was changed
                    if len(lang2) != len(lang2_original):
                        phrase_align_lang2[tuple(lang2)] = \
                            phrase_align_lang2[tuple(lang2_original)]
                        del phrase_align_lang2[tuple(lang2_original)]

            # For  target - source
            for lang2, lang1 in phrase_align_lang2.items():
                if len(lang1) > 1:
                    lang1_original = deepcopy(lang1)
                    for pos in range(len(lang1)-1):
                        if lang1[pos].isnumeric() and lang1[pos+1].isnumeric():
                            if abs(int(lang1[pos]) - int(lang1[pos+1])) == 2:
                                if source[int(lang1[pos])+1] == ",":
                                    phrase_align_lang2[lang2].insert(
                                        pos+1, ",")
                                else:
                                    phrase_align_lang2[lang2].insert(
                                        pos+1, "...")
                            elif abs(int(lang1[pos]) - int(lang1[pos+1])) > 2:
                                phrase_align_lang2[lang2].insert(pos+1, "...")
                    if len(lang1) != len(lang1_original):
                        phrase_align_lang1[tuple(lang1)] = \
                            phrase_align_lang1[tuple(lang1_original)]
                        del phrase_align_lang1[tuple(lang1_original)]

            # Index is replaced by the corresponding word
            for lang1, lang2 in phrase_align_lang1.items():
                k = ([source[int(i)] if i.isnumeric() else i for i in lang1])
                v = ([target[int(i)] if i.isnumeric() else i for i in lang2])
                k = remove_punct_phrases(k)
                v = remove_punct_phrases(v)
                # contractions = ["d'", "du", "des", "aux", "au"]
                # if v and v[-1] in contractions:
                #     v = remove_contractions(v, "french")
                lang1_lang2_alignments[" ".join(k)].append(" ".join(v))

            # Index is replaced by the corresponding word
            for lang2, lang1 in phrase_align_lang2.items():
                k = ([target[int(i)] if i.isnumeric() else i for i in lang2])
                v = ([source[int(i)] if i.isnumeric() else i for i in lang1])
                k = remove_punct_phrases(k)
                v = remove_punct_phrases(v)
                # contractions = ["d'", "du", "des", "aux", "au"]
                # if v and v[-1] in contractions:
                #     v = remove_contractions(v, "french")
                lang2_lang1_alignments[" ".join(k)].append(" ".join(v))

    end = time.time()
    print("The processing of the alignment took {:5.3f}s.".format(end-start))

    return lang1_lang2_alignments, lang2_lang1_alignments


def parse_phrase_alignments(result, language1, language2, phrases, lang=1):
    """Creates alignments for phrases through combining of eflomal
    alignments

    Can be used in case phrases were separated: "abgesehen" and "davon"
    could be aligned as single words to two different french words.
    However, both might be phrases that are expressed with a similar
    structure.

    Parameters
    ----------
    result : str
        The file name for the eflomal alignment
    language1 : str
        The file name for the source language
    language2 : str
        The file name for the target language
    phrases : list
        A list with all phrases of language 1 or 2
    lang : int
        An integer that indicates whether the phrases correspond to
        language 1 or 2

    Returns
    -------
    phrase_alignments : defaultdict
        A dictionary with the alignments for phrases
    """

    phrase_alignments = defaultdict(list)
    with open(result, "r", encoding="utf-8") as result,\
            open(language1, "r", encoding="utf-8") as lang1,\
            open(language2, "r", encoding="utf-8") as lang2:
        for index, l1, l2 in zip(result, lang1, lang2):
            lang_1 = l1.split()
            lang_2 = l2.split()
            alignment = index.split()
            pair = [[int(a.split("-")[0]), int(a.split("-")[1])]
                    for a in alignment]
            if lang == 1:
                sentence = l1
                source_tok = lang_1
                target_tok = lang_2
            elif lang == 2:
                sentence = l2
                source_tok = lang_2
                target_tok = lang_1

            for phrase_ in phrases:
                if phrase_ in sentence:
                    phrase = phrase_.split()
                    # Index of the phrase words in the source language
                    phrase_index = []
                    # Searches the exact position of the phrase in the
                    # string
                    # Might occur more than once, although unlikely
                    for pos in range(0, len(source_tok) - len(phrase) + 1):
                        if source_tok[pos:pos+len(phrase)] == phrase:
                            phrase_index.append(list(range(pos,
                                                           pos + len(phrase))))

                    for pos_range in phrase_index:
                        # Indexes of the target words
                        new_phrase = []
                        for word_pos in pos_range:
                            # Saves all target indexes in a list
                            if lang == 1:
                                alignment_index = [i2 for i1, i2 in pair
                                                   if i1 == word_pos]
                            elif lang == 2:
                                alignment_index = [i1 for i1, i2 in pair
                                                   if i2 == word_pos]
                            new_phrase += alignment_index
                        new_phrase = pd.unique(new_phrase).tolist()
                        if len(new_phrase) > 1:
                            new_phrase.sort()
                            # Inserts "..." for discontinuous
                            # phrases
                            pos = 0
                            while pos < len(new_phrase) - 1:
                                if isinstance(new_phrase[pos], int)\
                                        and isinstance(new_phrase[pos+1], int):
                                    if abs(new_phrase[pos]
                                           - new_phrase[pos+1]) == 2:
                                        if target_tok[new_phrase[pos]+1]\
                                                == ",":
                                            new_phrase.insert(pos+1, ",")
                                        else:
                                            new_phrase.insert(pos+1, "...")
                                    elif abs(new_phrase[pos]
                                             - new_phrase[pos+1]) > 2:
                                        new_phrase.insert(pos+1, "...")
                                pos += 1
                        # Index is replaced by the corresponding word
                        new_phrase = [target_tok[pos] if isinstance(pos, int)
                                      else pos
                                      for pos in new_phrase]
                        new_phrase = remove_punct_phrases(new_phrase)
                        # contractions = ["d'", "du", "des", "aux", "au",
                        #                 "zum", "zur", "vom"]
                        # if new_phrase and new_phrase[-1] in contractions:
                        #     if lang == 1:
                        #         new_phrase = remove_contractions(new_phrase,
                        #                                          "french")
                        #     else:
                        #         new_phrase = remove_contractions(new_phrase,
                        #                                          "german")
                        # else:
                        new_phrase = " ".join(new_phrase)
                        if ", ..." in new_phrase:
                            new_phrase = new_phrase.replace(", ...", "...")
                        phrase_alignments[phrase_].append(new_phrase)

    return phrase_alignments


def parse_discontinuous(result, language1, language2, phrases, lang=1):
    """Creates alignments for phrases independently from the eflomal
    alignments

    Can be used in case phrases were separated: "abgesehen" and "davon"
    could be aligned as single words to two different french words.
    However, both might be phrases that are expressed with a similar
    structure.

    Parameters
    ----------
    result : str
        The file name for the eflomal alignment
    language1 : str
        The file name for the source language
    language2 : str
        The file name for the target language
    phrases : list
        A list with all phrases of language 1 or 2
    lang : int
        An integer that indicates whether the phrases correspond to
        language 1 or 2

    Returns
    -------
    phrase_alignments : defaultdict
        A dictionary with the alignments for phrases
    """

    phrase_alignments = defaultdict(list)
    with open(result, "r", encoding="utf-8") as result,\
            open(language1, "r", encoding="utf-8") as lang1,\
            open(language2, "r", encoding="utf-8") as lang2:
        for index, l1, l2 in zip(result, lang1, lang2):
            lang_1 = l1.split()
            lang_2 = l2.split()
            alignment = index.split()
            pair = [[int(a.split("-")[0]), int(a.split("-")[1])]
                    for a in alignment]
            if lang == 1:
                sentence = l1
                source_tok = lang_1
                target_tok = lang_2
            elif lang == 2:
                sentence = l2
                source_tok = lang_2
                target_tok = lang_1

            for phrase_ in phrases:
                phrase = phrase_.split(" ... ")
                if phrase[0] in sentence\
                        and phrase[1] in sentence\
                        and sentence.index(phrase[0])\
                        < sentence.index(phrase[1]):
                    # Index of the phrase words in the source language
                    phrase_index = []
                    # Searches the exact position of the phrase in the
                    # string
                    # Might occur more than once, although unlikely
                    for part in phrase:
                        part = part.split()
                        for pos in range(0, len(source_tok) - len(part) + 1):
                            if source_tok[pos:pos+len(part)] == part:
                                source_pos = list(range(pos, pos
                                                        + len(part)))
                                if source_pos not in phrase_index:
                                    phrase_index.append(source_pos)
                                    break

                    new_phrase = []
                    for pos_range in phrase_index:
                        # Indexes of the target words
                        for word_pos in pos_range:
                            # Saves all target indexes in a list
                            if lang == 1:
                                alignment_index = [i2 for i1, i2 in pair
                                                   if i1 == word_pos]
                            elif lang == 2:
                                alignment_index = [i1 for i1, i2 in pair
                                                   if i2 == word_pos]
                            new_phrase += alignment_index

                    new_phrase = pd.unique(new_phrase).tolist()
                    if len(new_phrase) > 1:
                        new_phrase.sort()
                        # Inserts "..." for discontinuous phrases
                        pos = 0
                        while pos < len(new_phrase) - 1:
                            if isinstance(new_phrase[pos], int)\
                                    and isinstance(new_phrase[pos+1], int):
                                if abs(new_phrase[pos]
                                       - new_phrase[pos+1]) == 2:
                                    if target_tok[new_phrase[pos]+1]\
                                            == ",":
                                        new_phrase.insert(pos+1, ",")
                                    else:
                                        new_phrase.insert(pos+1, "...")
                                elif abs(new_phrase[pos]
                                         - new_phrase[pos+1]) > 1:
                                    new_phrase.insert(pos+1, "...")
                            pos += 1
                    # Index is replaced by the corresponding word
                    new_phrase = [target_tok[pos] if isinstance(pos, int)
                                  else pos
                                  for pos in new_phrase]
                    new_phrase = remove_punct_phrases(new_phrase)
                    # contractions = ["d'", "du", "des", "aux", "au", "zur",
                    #                 "zum", "vom"]
                    # if new_phrase and new_phrase[-1] in contractions:
                    #     if lang == 1:
                    #         new_phrase = remove_contractions(new_phrase,
                    #                                          "french")
                    #     else:
                    #         new_phrase = remove_contractions(new_phrase,
                    #                                          "german")
                    # else:
                    new_phrase = " ".join(new_phrase)
                    if ", ..." in new_phrase:
                        new_phrase = new_phrase.replace(", ...", "...")
                    phrase_alignments[phrase_].append(new_phrase)

    return phrase_alignments


if __name__ == "__main__":
    # de, es = parse_word_alignments("europarl_de-es_alignment.txt",
    #                                "europarl_de-es_de.txt",
    #                                "europarl_de-es_es.txt")
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source_lang", action="store",
                        type=str,
                        help="Source language code")
    parser.add_argument("-t", "--target_lang", action="store",
                        type=str,
                        help="Target language code")
    parser.add_argument("word_alignment",
                        help="Alignment text file in Pharaoh format")
    parser.add_argument("source_corpus", help="Corpus with source sentences")
    parser.add_argument("target_corpus", help="Corpus with target sentences")
    args = parser.parse_args()
    source, target = parse_word_alignments(args.word_alignment,
                                           args.source_corpus,
                                           args.target_corpus)
    save_alignments(
        f"{args.source_lang}_{args.target_lang}_word_alignment.json", source)
    save_alignments(
        f"{args.target_lang}_{args.source_lang}_word_alignment.json", target)
