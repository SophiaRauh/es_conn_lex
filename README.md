# Aligning Connectives
This program can be used to extract the word alignment based on a file in pharaoh format and to align connectives in two languages.

If you use the code for your research, please cite the following:

## Installation
The project is written with Python 3. Further requirements are:
* nltk
* pandas

The required version can be found in **requirements.txt**.

## Usage
#### 1. Extracting the word alignment
Based on a text file with the word alignment in pharaoh format and a parallel corpus, two JSON files with the alignments for the source-target languages and target-source languages are generated. Both files are required for the alignment of connectives and they are automatically saved in the same directory as the code.
```
python parse_alignments.py [-h] [-s SOURCE_LANG] [-t TARGET_LANG] word_alignment source_corpus target_corpus
```
| Positional Arguments | Explanation|
|----------|-------------------------------|
| _word\_alignment_ |  TXT file with word alignment in pharaoh format |
| _source\_corpus_ | Path to the source corpus with sentences as TXT file |
| _target\_corpus_ | Path to the target corpus with sentences as TXT file |

| Optional Arguments | Explanation| Example |
|----------|-------------------------------|-----|
| _-h, --help_ | Show this help message and exit | -h |
| _-s, --help_ | Source language code | -s de |
| _-t, --help_ | Target language code | -t it |

##### Example
```
python parse_all_alignments.py -s de -t it de_it_alignment.txt de_corpus.txt it_corpus.txt
```

#### 2. Alignment of Connectives
This file computes the alignment of connectives. The connectives alignments are saved as JSON files.
```
python conn_align.py [-h] [-s SOURCE_LANG] [-t TARGET_LANG] [-sr]
                     [-wt WORD_THRESHOLD] [-pt PHRASE_THRESHOLD]
                     [-i ITERATIONS] [-wc WORD_COUNT] [-pc PHRASE_COUNT]
                     [-sl SOURCE_LEX] [-tl TARGET_LEX]
                     word_alignment source_corpus target_corpus


```
| Positional Arguments | Explanation|
|----------|-------------------------------|
| _word\_alignment_ |  TXT file with word alignment in pharaoh format |
| _source\_corpus_ | Path to the source corpus with sentences as TXT file |
| _target\_corpus_ | Path to the target corpus with sentences as TXT file |

| Optional Arguments | Explanation| Example |
|----------|-------------------------------|-----|
| _-h_ | Show this help message and exit | -h |
| _-s_ | Source language code | -s de |
| _-t_ | Target language code | -t it |
| _-sr_ |  If specified, connectives are saved with corresponding discourse relation | -sr |
| _-wt_ | Relative word threshold in percent | -wt 0.03 |
| _-pt_ | Relative threshold for phrases in percent | -pt 0.02 |
| _-i_ | Number of iterations | -i 2 |
| _-wc_ | Absolute word threshold as count | -wc 40 |
| _-pc_ |  Absolute phrase threshold as count | -pc 20 |
| _-sl_ | Source connective lexicon, should be specified if it is not Italian or German, TXT or XML file | -sl "fr_lex.xml" |
| _-tl_ | Source connective lexicon, should be specified if it is not Italian or German, TXT or XML file | -tl "eng_lex.txt" |

##### Examples
```
python conn_align.py -s de -t it alignment.txt german.txt italian.txt
python conn_align.py -s de -t fr -tl fr_lex.xml alignment.txt german.txt french.txt
```

#### Notes
The folder *help\_functions* includes files to extract text examples from the corpus and a simple tokenizer for Italian and Spanish. They can be used separately.
Output files related to the bachelor thesis can be found in *results*. They include the new Spanish connective lexicon as XML and CSV file, as well as the connective aligments for German-Spanish, Spanish-German, Italian-Spanish, Spanish-Italian, German-Italian, and Italian-German.

## References
This work is based on the connective lexicons DiMLex and LICO.

Manfred Stede and Carla Umbach. 1998. DiMLex: A lexicon of discourse markers for text generation and understanding]. In _36th Annual Meeting of the Association for Computational Linguistics and 17th International Conference on Computational Linguistics, Volume 2_, pages 1238–1242, Montreal, Quebec, Canada. Association for Computational Linguistics.

Anna Feltracco, Elisabetta Jezek, Bernardo Magnini, and Manfred Stede (2016). LICO: A Lexicon of Italian Connectives. In _Proceedings of the 3rd Italian Conference on Computational Lingui-
stics (CLiC-it)_, pages 141–145, Napoli, Italy.


