# -*- coding: utf-8 -*-

"""Connectives Alignment"""

from collections import defaultdict
from copy import deepcopy

from processing_filtering import (filter_most_common_conns,
                                  # remove_pronouns,
                                  alignment_probabilities,
                                  conn_count,
                                  remove_low_counts,
                                  # complete_phrases,
                                  # filter_unlikely_alignments,
                                  # remove_incomplete_phrases,
                                  filter_single_words,
                                  remove_punct_values)
from parse_alignments import parse_phrase_alignments, parse_discontinuous


class FindAlignments:
    """A class used to find new alignments to connectives

    Parameters
    ----------
    source_alignment_file : defaultdict or str
        Dictionary or file with source - target alignments
    target_alignment_file : defaultdict or str
        Dictionary or file with target - source alignments
    alignment : str
        Path to the alignment (format: 1-1 1-2 ...)
    source_corpus : str
        Path to the source corpus
    target_corpus : str
        Path to the target corpus
    target_lex : list
        Target connectives filtered for a discourse relation type
    source_lex : list
        Source connectives filtered for a discourse relation type
    all_target_conns : list
        Target connectives unfiltered
    all_source_conns : list
        Source connectives unfiltered

    Attributes
    ----------
    source_target : dict
        Source - target alignment (unsorted, uncounted)
    target_source : dict
        Target - source alignment (unsorted, uncounted)
    alignment : str
        Path to the alignment (format: 1-1 1-2 ...)
    source_corpus : str
        Path to the source corpus
    target_corpus : str
        Path to the target corpus
    target_lex : list
        Target connectives filtered for a discourse relation type
    source_lex : list
        Source connectives filtered for a discourse relation type
    all_target_conns : list
        Target connectives unfiltered
    all_source_conns : list
        Source connectives unfiltered
    counter : int
        counts the rounds to find new alignments
    source_conn_alignments: dict
        Source alignments (filtered, as probabilities)
    target_conn_alignments: dict
        Target alignments (filtered, as probabilities)
    source_count : dict
        Source alignments (unfiltered, as counts)
    target_count : dict
        Target alignments (unfiltered, as counts)
    """

    def __init__(self, source_alignment_file, target_alignment_file, alignment,
                 source_corpus, target_corpus, source_lex, target_lex,
                 source_code, target_code):
        self.source_target = source_alignment_file
        self.target_source = target_alignment_file
        self.alignment = alignment
        self.source_corpus = source_corpus
        self.target_corpus = target_corpus
        self.target_lex = target_lex
        self.source_lex = source_lex
        self.all_source_conns = deepcopy(source_lex)
        self.all_target_conns = deepcopy(target_lex)
        self.counter = 0
        self.source_conn_alignments = dict()
        self.target_conn_alignments = dict()
        self.source_count = dict()
        self.target_count = dict()
        self.source_code = source_code
        self.target_code = target_code

    def find_conns(self, lex=[], lang="source", word_threshold=0.02,
                   phrase_threshold=0.02, word_min_count=20,
                   phrase_min_count=10, limit=1):
        """Finds new connective alignments

        Parameters
        ----------
        lex : list
            The lexicon used to find new alignments (source or target)
        lang : str
            The language is "source" or "target" language
        word_threshold : float
            The minimum probability for an alignment for a single word
        phrase_threshold : float
            The minimum probability for an alignment for a phrase
        word_min_count : int
            The minimum number for an alignment for a single word
        phrase_min_count : int
            The minimum number for an alignment for a phrase
        limit : int
            The number of rounds

        Returns
        -------
        None
        """

        self.counter += 1

        if lang == "target":
            other_lang_code = self.source_code
            alignments = self.target_source
            count_dict = self.target_count
            lang_pos = 2
            other_lang = "source"
            if not lex:
                lex = self.target_lex
            # Delete connectives with inaccurate alignment
            # fr_del = ["dire que", "dire qu'", "et dire que", "et dire qu'",
            #           "encore que", "cependant que", "cependant qu'",
            #           "encore qu'", "si", "s'",
            #           "en même temps que", "en même temps qu'"]
            # lex = [conn for conn in lex if conn not in fr_del]

            other_lex = self.source_lex
            complete_lex = self.all_source_conns
        elif lang == "source":
            other_lang_code = self.target_code
            alignments = self.source_target
            count_dict = self.source_count
            lang_pos = 1
            other_lang = "target"
            if not lex:
                lex = self.source_lex
            # Delete connectives with inaccurate alignment
            # de_del = ["bloß", "dabei", "mangels", "mithin", "obschon",
            #           "wenn ... auch", "wiederum", "wobei", "wohingegen",
            #           "als ob"]
            # lex = [conn for conn in lex if conn not in de_del]
            other_lex = self.target_lex
            complete_lex = self.all_target_conns
        else:
            pass

        new_conns = []
        new_alignments = defaultdict(list)
        # Find all alignments for the current connective lexicon
        single_words = [word for word in lex if len(word.split()) == 1]
        phrases = [phrase for phrase in lex if len(phrase.split()) > 1
                   and "..." not in phrase]
        discontinuous = [phrase for phrase in lex if "..." in phrase]

        for key in single_words:
            try:
                new_alignments[key] = alignments[key]
            except KeyError:
                pass

        new_phrase_alignments = parse_phrase_alignments(
            self.alignment, self.source_corpus, self.target_corpus,
            phrases, lang=lang_pos)

        new_discontinuous = parse_discontinuous(
            self.alignment, self.source_corpus, self.target_corpus,
            discontinuous, lang=lang_pos)

        single_count = conn_count(new_alignments, lex)
        phrase_count = conn_count(new_phrase_alignments, phrases)
        discont_count = conn_count(new_discontinuous, discontinuous)
        if lang == "target":
            self.target_count.update(single_count)
            self.target_count.update(phrase_count)
            self.target_count.update(discont_count)
        elif lang == "source":
            self.source_count.update(single_count)
            self.source_count.update(phrase_count)
            self.source_count.update(discont_count)

        # Combine the single word and phrase alignments
        new_alignments = {**new_alignments, **new_phrase_alignments,
                          **new_discontinuous}
        new_alignments = remove_punct_values(new_alignments)
        new_alignments = alignment_probabilities(new_alignments)
        new_alignments = filter_most_common_conns(new_alignments,
                                                  word_threshold,
                                                  phrase_threshold)
        new_alignments = remove_low_counts(new_alignments, count_dict,
                                           word_min_count, phrase_min_count)
        new_alignments = filter_single_words(new_alignments, other_lang_code)
        # new_alignments = filter_unlikely_alignments(new_alignments, lang)
        # new_alignments = remove_incomplete_phrases(new_alignments)
        # new_alignments = remove_pronouns(new_alignments, other_lang)
        # new_alignments = complete_phrases(new_alignments, complete_lex)

        # Find new connectives
        for conns in new_alignments.values():
            for word, count in conns.items():
                if word and word not in other_lex:
                    new_conns.append(word)
        new_conns = list(set(new_conns))

        if lang == "target":
            self.target_conn_alignments.update(new_alignments)
            self.source_lex += new_conns
            lex = self.source_lex
            lang = "source"
        else:
            self.source_conn_alignments.update(new_alignments)
            self.target_lex += new_conns
            lex = self.target_lex
            lang = "target"

        if self.counter == limit:
            print(len(self.source_lex))
            print(len(self.all_source_conns))
            return

        if self.counter == 1:
            # Ensures that the first entries of the lexicon (DimLex or
            # LexConn) are not ignored
            self.find_conns(lex, lang, word_threshold, phrase_threshold,
                            word_min_count, phrase_min_count, limit)
        else:
            self.find_conns(new_conns, lang, word_threshold, phrase_threshold,
                            word_min_count, phrase_min_count, limit)
