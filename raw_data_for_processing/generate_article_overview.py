# -*- coding: utf-8 -*-
import os
from collections import Counter
import io
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
import nltk
from nltk import FreqDist
from collections import defaultdict
import argparse
import errno

def find_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return [path for path in paths if path.endswith(".txt") and not path.endswith("analysis.txt") and not path.endswith("amount.txt")]


def remove_article_words(tokens):
        clean_tokens = []
        word_filter = ['facebooktwitteremail', '']
        for token in tokens:
            if token not in word_filter:
                clean_tokens.append(token)

        return clean_tokens, word_filter


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def remove_punctuation(tokens):
    clean_tokens = []
    # keep '%' in punctuation
    punctuation = ['!', '"', '#', '$', '&', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', "=", '>', '?',
        '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', '“', '’', '”', '—', "'"]

    for token in tokens:
        clean_token = ""
        for char in token:
            if char not in punctuation:
                clean_token = clean_token + char
            else:
                clean_token = clean_token + ""
        if clean_token != "":
            clean_tokens.append(clean_token)

    return clean_tokens, punctuation


def minimum_length(tokens, length):
    tokens = [token for token in tokens if len(token) >= length]
    return tokens

def create_args_filter_name(args):
    args = str(args)
    args = args[10:-1]
    args = args.split(',')
    args = "".join(args)
    args = args.split("=")
    args = '_'.join(args)
    args = args.split()
    filter_name = '_'.join(args)

    return filter_name


def generate_overview(read_path, remove_stopwords, use_lemmatizer, minimum_token_length, use_stemmer, use_bigrams, use_trigrams, args):
    print("Running pre-processing in following order:")
    print("Lowercase text")
    print("Tokenize by nltk.word_tokenize")
    print("Remove punctuation")

    filter_name = create_args_filter_name(args)  # create variable to name file as used filters for identification
    print("Filters in use:",filter_name)
    print()

    # Collect article text files
    txt_files = find_files(read_path)

    # Line graph intended message indicators from articles
    article_filter_line = []
    # Bar chart intended message indicators from articles
    article_filter_bar = []

    # list of stopwords
    Stopwords = stopwords.words('english')

    # lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Stemmer
    stemmer = PorterStemmer()

    # count tokens from all articles:
    c_raw = Counter()  # count tokens without pre-processing
    c_article1 = Counter()  # count tokens with stemming and pos_tags NN, VB, JJ
    c_processed = Counter()  # count tokens after pre-processing

    # scrape tokens from articles in txt format
    for txt_file in txt_files:
        filename = txt_file.split(".")  #  save filename
        print("Read file:", filename[1])

        ########### open txt file from article:
        infile = open(txt_file, 'r', encoding="utf8", errors='ignore')
        content = infile.read().lower()

        ########### tokenize by NLTK
        tokens = nltk.word_tokenize(content)

        # count raw tokens by NLTK tokenizer
        # NOTE, count for all articles
        for token in tokens:
            c_raw[token] += 1

        raw_total_tokens = len(tokens)
        raw_types = len(set(tokens))
        raw_ttr = raw_types/raw_total_tokens

        ########### apply pre-processing:
        tokens, removed_punctuation = remove_punctuation(tokens)
        tokens, removed_article_words = remove_article_words(tokens)
        tokens = minimum_length(tokens, minimum_token_length)  # filter out tokens if less then 4 characters

        ########### apply n-grams processing by NLTK
        bigrams = [" ".join(token) for token in nltk.bigrams(tokens)]
        trigrams = [" ".join(token) for token in nltk.trigrams(tokens)]

        ### bigrams option
        if use_bigrams:
            tokens = tokens + bigrams

        ### trigrams option
        if use_trigrams:
            tokens = tokens + trigrams

        ########### apply processing:
        # remove stopwords
        if remove_stopwords:
            tokens = [token for token in tokens if token not in Stopwords]

        # lemmatize tokens
        if use_lemmatizer:
            tokens = [lemmatizer.lemmatize(token) for token in tokens]

        # Stem tokens
        if use_stemmer:
            tokens = [stemmer.stem(token) for token in tokens]

        # pos tagging
        pos_tags = nltk.pos_tag(tokens)
        pos_dict = defaultdict(list)
        for pos_tag in pos_tags:
            tag = pos_tag[1]
            token = pos_tag[0]
            # store all POS tags in dictionary
            pos_dict[tag].append(token)

        ########### token information
        total_tokens = len(tokens)
        types = len(set(tokens))
        ttr = types/total_tokens

        ########### count tokens after processing
        # NOTE, count for all articles
        for token in tokens:
            c_processed[token] += 1


        ######### article 1:
        """ article simple bar charts:
        We compiled a set of helpful verbs and adjectives
        (identified through our corpus study, WordNet [67] and a thesaurus [48]) and
        manually divided them into similarity classes; for example, the verbs rise and
        soar were placed in the same class, whereas the verbs lag and trail were placed in
        a different class.
        Adjectives derived from verbs, such as soaring, are treated as
        verbs. We then used a part-of-speech tagger and a stemmer to implement a type
        of shallow processing of captions to identify ) the presence of one of our verb
        or adjective classes (adjectives and nouns derived from verbs, such as “soaring”,
        are reduced to their root form and treated as verbs) and 2) nouns which match
        the label of a data element in the bar chart. """

        # for token in pos_tags_in_article:
        #     c_article1_raw[token] += 1
        #
        # for token in pos_tags_in_article:
        #     stemmed = stemmer.stem(token)
        #     c_article1[stemmed] += 1

        ######################################################

        # write article summaries
        with open("."+filename[1]+"_"+filter_name+"_analysis.txt", "w") as outfile:
            outfile.write("Tokenized by nltk.word_tokenize \n")
            outfile.write("Token analysis before pre-processing \n")
            outfile.write("Raw number of tokens: "+str(raw_total_tokens)+"\n")
            outfile.write("Raw number of types: "+str(raw_types)+"\n")
            outfile.write("Raw Type token ratio: "+str(raw_ttr)+"\n\n")  # higher = more diverse in language

            outfile.write("Applied pre-processing:\n")
            outfile.write("Lowercased all tokens \n")
            outfile.write("Tokens below minimum length: "+str(minimum_token_length)+" filtered out\n\n")
            outfile.write("Punctuation filtered out "+str(removed_punctuation)+"\n")
            outfile.write("Words filtered out: "+str(removed_article_words)+"\n\n")

            outfile.write("Applied filters:\n")
            outfile.write("Using stopwords filter = "+str(remove_stopwords)+"\n")
            outfile.write("Using lemmatizer = "+str(use_lemmatizer)+"\n")
            outfile.write("Using stemmer = "+str(use_stemmer)+"\n\n")

            outfile.write("Token analysis after pre-processing \n")
            outfile.write("Number of tokens: "+str(total_tokens)+"\n")
            outfile.write("Number of types: "+str(types)+"\n")
            outfile.write("Type token ratio: "+str(ttr)+"\n")  # higher = more diverse in language
            outfile.write("\n")

            outfile.write("Used nouns, verbs and adjectives in article: \n")
            outfile.write("(tokens separated by , ) \n")
            for tag, tokens in pos_dict.items():
                if tag.startswith("NN") or tag.startswith("V") or tag.startswith("J"):
                    line = tag,', '.join(tokens)
                    outfile.write(str(line)+'\n\n')

    ####### print results in terminal
    print()
    print("NOTE: All tokens converted to lowercase!")
    print()
    print("Raw token count: \n", c_raw.most_common(100))
    print()
    print("Processed token count: \n", c_processed.most_common(100))
    print()

    # write general overview
    with open(filter_name+"_general_analysis.txt", "w") as outfile:
        outfile.write("NOTE: All tokens converted to lowercase!\n")
        outfile.write("Filters:\n")
        outfile.write("Using stopwords filter = "+str(remove_stopwords)+"\n")
        outfile.write("Using lemmatizer = "+str(use_lemmatizer)+"\n")
        outfile.write("Using stemmer = "+str(use_stemmer)+"\n\n")
        outfile.write("Raw 100 most freq tokens: \n"+str(c_raw.most_common(100))+"\n\n")
        outfile.write("Processed 100 most freq tokens: \n"+str(c_processed.most_common(100))+"\n")

    # print("Article 1 token count: \n", c_article1_raw.most_common(50))
    # print()
    # print("Article 1 stemmed token count: \n", c_article1.most_common(50))


def main():
    # Read arguments
    parser = argparse.ArgumentParser(description='NN parameters')
    parser.add_argument('--stopwords', action='store_true', help='Filter stop words')
    parser.add_argument('--lemmatize', action='store_true', help='Use lemmatizer')
    parser.add_argument('--stemmer', action='store_true', help='Use stemmer')
    parser.add_argument('--tokenlength', '--tl', type=int, default=3, help='Set minimum token length')
    parser.add_argument('--bigrams', action='store_true', help='Use bigrams')
    parser.add_argument('--trigrams', action='store_true', help='Use trigrams')
    args = parser.parse_args()

    generate_overview("./", remove_stopwords = args.stopwords, use_lemmatizer = args.lemmatize, use_stemmer = args.stemmer, minimum_token_length = args.tokenlength, use_bigrams = args.bigrams, use_trigrams = args.trigrams, args = args)
    print("Done.")

if __name__ == '__main__':
    main()
