# -*- coding: utf-8 -*-

# Sophia Rauh
# Matrikelnummer 790850
# Python 3.9.13
# Windows 10

"""Organising the Output: Connectives Alignments and Visual Output"""

import argparse
import sys
from pathlib import Path

from conn_search import FindAlignments
from help_functions.discourse_relations import (add_discourse_relation,
                                                assign_relations)

from processing_filtering import (json_to_dict, read_xml_lex, read_es_conns,
                                  save_alignments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("word_alignment",
                        help="Alignment text file in Pharaoh format")
    parser.add_argument("source_corpus", help="Corpus with source sentences")
    parser.add_argument("target_corpus", help="Corpus with target sentences")
    parser.add_argument("-s", "--source_lang", action="store",
                        type=str,
                        help="Source language code")
    parser.add_argument("-t", "--target_lang", action="store",
                        type=str,
                        help="Target language code")
    parser.add_argument("-sr", "--show_relation", action="store_true",
                        help="If specified, connectives are saved with"
                        " corresponding discourse relation")
    parser.add_argument("-wt", "--word_threshold", action="store",
                        default=0.021, type=float,
                        help="Relative word threshold in percent")
    parser.add_argument("-pt", "--phrase_threshold", action="store",
                        default=0.014, type=float,
                        help="Relative phrase threshold in percent")
    parser.add_argument("-i", "--iterations", action="store",
                        default=2, type=int, help="Number of iterations")
    parser.add_argument("-wc", "--word_count", action="store",
                        default=20, type=int,
                        help="Absolute word threshold as count")
    parser.add_argument("-pc", "--phrase_count", action="store",
                        default=10, type=int,
                        help="Absolute phrase threshold as count")
    parser.add_argument("-sl", "--source_lex", action="store",
                        default="", type=str,
                        help="Source connective lexikon")
    parser.add_argument("-tl", "--target_lex", action="store",
                        default="", type=str,
                        help="Target connective lexicon")

    args = parser.parse_args()

    source_word_alignment = json_to_dict(
        f"{args.source_lang}_{args.target_lang}_word_alignment.json")
    target_word_alignment = json_to_dict(
        f"{args.target_lang}_{args.source_lang}_word_alignment.json")

    if args.source_lang == "it":
        source_lex = read_xml_lex(
            Path("connectives_and_relations/lico_d.xml"))
    elif args.source_lang == "es":
        source_lex = read_es_conns(
            Path("connectives_and_relations/spanish_conns.txt"))
    elif args.source_lang == "de":
        source_lex = read_xml_lex(
            Path("connectives_and_relations/dimlex.xml"))
    else:
        if args.source_lex:
            if args.source_lex.endswith("xml"):
                source_lex = read_xml_lex(
                    Path(args.source_lex))
            elif args.source_lex.endswith("txt"):
                source_lex = read_es_conns(
                    Path(args.source_lex))
            else:
                sys.exit(
                    "The source connective lexicon has to be a XML or TXT file"
                    )
        else:
            sys.exit(
                "If the source connectives are not in Italian, Spanish or "
                "German, you have to provide the Path to a connective lexicon"
                " with the argument '-sl'")

    if args.target_lang == "it":
        target_lex = read_xml_lex(
            Path("connectives_and_relations/lico_d.xml"))
    elif args.target_lang == "es":
        target_lex = read_es_conns(
            Path("connectives_and_relations/spanish_conns.txt"))
    elif args.target_lang == "de":
        target_lex = read_xml_lex(
            Path("connectives_and_relations/dimlex.xml"))
    else:
        if args.target_lex:
            if args.target_lex.endswith("xml"):
                target_lex = read_xml_lex(
                    Path(args.target_lex))
            elif args.target_lex.endswith("txt"):
                target_lex = read_es_conns(
                    Path(args.target_lex))
            else:
                sys.exit(
                    "The source connective lexicon has to be a XML or TXT file"
                    )
        else:
            sys.exit(
                "If the source connectives are not in Italian, Spanish or "
                "German, you have to provide the Path to a connective lexicon"
                " with the argument '-sl'")

    align = FindAlignments(source_word_alignment, target_word_alignment,
                           Path(args.word_alignment),
                           Path(args.source_corpus), Path(args.target_corpus),
                           source_lex, target_lex)

    align.find_conns(lang="source", word_threshold=args.word_threshold,
                     phrase_threshold=args.phrase_threshold,
                     word_min_count=args.word_count,
                     phrase_min_count=args.phrase_count, limit=args.iterations)

    if args.show_relation:
        if args.source_lang == "it":
            s_rel = json_to_dict(
                Path("connectives_and_relations/it_relations.json"))
        elif args.source_lang == "de":
            s_rel = json_to_dict(
                Path("connectives_and_relations/de_relations.json"))
        elif args.source_lex and args.source_lex.endswith("xml"):
            s_rel = assign_relations(args.source_lex)
        else:
            s_rel = dict()

        if args.target_lang == "it":
            t_rel = json_to_dict(
                Path("connectives_and_relations/it_relations.json"))
        elif args.target_lang == "de":
            t_rel = json_to_dict(
                Path("connectives_and_relations/de_relations.json"))
        elif args.target_lex and args.target_lex.endswith("xml"):
            t_rel = assign_relations(args.target_lex)
        else:
            t_rel = dict()

        source_alignment = add_discourse_relation(
            align.source_conn_alignments, source_mapping=s_rel,
            target_mapping=t_rel)
        target_alignment = add_discourse_relation(
            align.target_conn_alignments, target_mapping=s_rel,
            source_mapping=t_rel)

    else:
        target_alignment = align.target_conn_alignments
        source_alignment = align.source_conn_alignments

    if target_alignment:
        save_alignments(
            f"{args.target_lang}_{args.source_lang}_connectives_alignment"
            f".json",
            target_alignment)
        save_alignments(
            f"{args.target_lang}_{args.source_lang}_connectives_alignment"
            f"_count.json", align.target_count)
    if source_alignment:
        save_alignments(
            f"{args.source_lang}_{args.target_lang}_connectives_alignment"
            f".json",
            source_alignment)
        save_alignments(
            f"{args.source_lang}_{args.target_lang}_connectives_alignment"
            f"_count.json", align.source_count)
