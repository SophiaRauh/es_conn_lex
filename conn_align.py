# -*- coding: utf-8 -*-

"""Organising the Output: Connectives Alignments and Visual Output"""

import argparse
from pathlib import Path

from conn_search import FindAlignments
from discourse_relations import (add_discourse_relation
                                 # filter_for_discourse_relation,
                                 # discourse_relation_mapping,
                                 # create_sankey_diagram)
                                 )
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
    # parser.add_argument("-dr", "--discourse_relation", type=str,
    #                     default="concession",
    #                     help="The discourse relation (e.g. 'concession')")
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
                        default=3, type=int, help="Number of iterations")
    parser.add_argument("-wc", "--word_count", action="store",
                        default=20, type=int,
                        help="Absolute word threshold as count")
    parser.add_argument("-pc", "--phrase_count", action="store",
                        default=10, type=int,
                        help="Absolute phrase threshold as count")
    # parser.add_argument("-g", "--german_first", action="store_true",
    #                     help="If specified, the first iteration starts with"
    #                     " German-French, default is French-German")

    args = parser.parse_args()

    # if args.german_first:
    #     language = "german"
    # else:
    #     language = "french"

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

    if args.target_lang == "it":
        target_lex = read_xml_lex(
            Path("connectives_and_relations/lico_d.xml"))
    elif args.target_lang == "es":
        target_lex = read_es_conns(
            Path("connectives_and_relations/spanish_conns.txt"))
    elif args.target_lang == "de":
        target_lex = read_xml_lex(
            Path("connectives_and_relations/dimlex.xml"))

    de_rel = json_to_dict(Path("connectives_and_relations/de_relations.json"))
    it_rel = json_to_dict(Path("connectives_and_relations/it_relations.json"))
    # fr_rel = json_to_dict(Path("connectives_and_relations/fr_relations.json"))
    # rel = json_to_dict(Path("connectives_and_relations/relations.json"))

    align = FindAlignments(source_word_alignment, target_word_alignment,
                           Path(args.word_alignment),
                           Path(args.source_corpus), Path(args.target_corpus),
                           source_lex, target_lex, args.source_lang,
                           args.target_lang)

    align.find_conns(lang="source", word_threshold=args.word_threshold,
                     phrase_threshold=args.phrase_threshold,
                     word_min_count=args.word_count,
                     phrase_min_count=args.phrase_count, limit=args.iterations)

    if args.show_relation:
        if "it" == args.source_lang and "de" == args.target_lang:
            source_alignment = add_discourse_relation(
                align.source_conn_alignments, source_mapping=it_rel,
                target_mapping=de_rel)
            target_alignment = add_discourse_relation(
                align.target_conn_alignments, target_mapping=it_rel,
                source_mapping=de_rel)
        elif "de" == args.source_lang and "it" == args.target_lang:
            source_alignment = add_discourse_relation(
                align.source_conn_alignments, source_mapping=de_rel,
                target_mapping=it_rel)
            target_alignment = add_discourse_relation(
                align.target_conn_alignments, target_mapping=de_rel,
                source_mapping=it_rel)
        elif "it" == args.source_lang:
            source_alignment = add_discourse_relation(
                align.source_conn_alignments, source_mapping=it_rel)
            target_alignment = add_discourse_relation(
                align.target_conn_alignments, target_mapping=it_rel)
        elif "it" == args.target_lang:
            source_alignment = add_discourse_relation(
                align.source_conn_alignments, target_mapping=it_rel)
            target_alignment = add_discourse_relation(
                align.target_conn_alignments, source_mapping=it_rel)
        elif "de" == args.source_lang:
            source_alignment = add_discourse_relation(
                align.source_conn_alignments, source_mapping=de_rel)
            target_alignment = add_discourse_relation(
                align.target_conn_alignments, target_mapping=de_rel)
        elif "de" == args.target_lang:
            source_alignment = add_discourse_relation(
                align.source_conn_alignments, target_mapping=de_rel)
            target_alignment = add_discourse_relation(
                align.target_conn_alignments, source_mapping=de_rel)
    else:
        target_alignment = align.target_conn_alignments
        source_alignment = align.source_conn_alignments

    if target_alignment:
        save_alignments(
            f"{args.target_lang}_{args.source_lang}_connectives_alignment"
            f".json",
            target_alignment)
        # fr_mapping = discourse_relation_mapping(align.fr_conn_alignments,
        #                                         fr_rel, de_rel)
        # create_sankey_diagram(fr_mapping, "fr", "de",
        #                       args.discourse_relation,
        #                       f"fr_de_{args.discourse_relation}_mapping.png")
    if source_alignment:
        save_alignments(
            f"{args.source_lang}_{args.target_lang}_connectives_alignment"
            f".json",
            source_alignment)
        # de_mapping = discourse_relation_mapping(align.de_conn_alignments,
        #                                         de_rel, fr_rel)
        # create_sankey_diagram(de_mapping, "de", "fr",
        #                       args.discourse_relation,
        #                       f"de_fr_{args.discourse_relation}_mapping.png")

    # TODO: create conn filter for all languages for false alignments
    # TODO: reduce "a pesar de" and throw out Spanish non-connectives
