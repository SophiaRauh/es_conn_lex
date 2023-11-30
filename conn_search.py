# -*- coding: utf-8 -*-

# Sophia Rauh
# Matrikelnummer 790850
# Python 3.9.13
# Windows 10

"""Connectives Alignment"""

from collections import defaultdict

from processing_filtering import (filter_most_common_conns,
                                  alignment_probabilities,
                                  conn_count,
                                  remove_low_counts,
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
                 source_corpus, target_corpus, source_lex, target_lex):
        self.source_target = source_alignment_file
        self.target_source = target_alignment_file
        self.alignment = alignment
        self.source_corpus = source_corpus
        self.target_corpus = target_corpus
        self.target_lex = target_lex
        self.source_lex = source_lex
        self.counter = 0
        self.source_conn_alignments = dict()
        self.target_conn_alignments = dict()
        self.source_count = dict()
        self.target_count = dict()

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
            alignments = self.target_source
            count_dict = self.target_count
            lang_pos = 2
            if not lex:
                lex = self.target_lex

            other_lex = self.source_lex
        elif lang == "source":
            alignments = self.source_target
            count_dict = self.source_count
            lang_pos = 1
            if not lex:
                lex = self.source_lex
            other_lex = self.target_lex
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
            return

        if self.counter == 1:
            # Ensures that the first entries of the xml lexicon are
            # not ignored
            self.find_conns(lex, lang, word_threshold, phrase_threshold,
                            word_min_count, phrase_min_count, limit)
        else:
            self.find_conns(new_conns, lang, word_threshold, phrase_threshold,
                            word_min_count, phrase_min_count, limit)
