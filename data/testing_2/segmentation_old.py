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
from bs4 import BeautifulSoup
import spacy
from nltk.tag import StanfordNERTagger
from nltk.tag.stanford import CoreNLPNERTagger
from nltk.corpus import wordnet


def hypernymOf(synset1, synset2):
    """ Returns True if synset2 is a hypernym of
    synset1, or if they are the same synset.
    Returns False otherwise."""

    if synset1 == synset2:
        return True

    for hypernym in synset1.hypernyms():
        if synset2 == hypernym:
            return True
        if hypernymOf(hypernym, synset2):
            return True
    return False


def find_text_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return [path for path in paths if path.endswith(".txt") and not path.endswith("analysis.txt") and not path.endswith("amount.txt") and not path.endswith("_graphs.txt")]


def find_image_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return [path for path in paths if path.endswith(".png")]


def remove_article_words(tokens):
        clean_tokens = []
        word_filter = ['facebooktwitteremail', 'nobarlabels', 'nolinelabels', 'nolabels']
        for token in tokens:
            if token not in word_filter:
                clean_tokens.append(token)

        return clean_tokens, word_filter

# def remove_labels(tokens):
#         clean_tokens = []
#         word_filter = ['<bar>', '<line>', '</bar>', '</line>', '<nolabels>', '<nobarlabels>', '<nolinelabels>']
#         for token in tokens:
#             if token not in word_filter:
#                 clean_tokens.append(token)
#
#         return clean_tokens, word_filter


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def remove_punctuation(tokens):
    clean_tokens = []
    # keep '%' in punctuation
    punctuation = ['!', '"', '#', '$', '&', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', "=", '?',
        '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', '“', '’', '”', '—', "'", "<", ">"]  # don't remove < and >

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


def create_filter_names(args_filter_options):
    filters = ["".join(name) for name in args_filter_options.split("_")]
    names = []
    options = []
    for filter in filters:
        if filter == "True" or filter == "False" or not filter.isalpha():
            options.append(filter)
        else:
            names.append(filter)

    return names, options


def generate_overview(read_path):

    # Construct Standford NER tagger
    st = StanfordNERTagger('stanford-ner-2018-10-16/classifiers/english.muc.7class.distsim.crf.ser.gz', 'stanford-ner-2018-10-16/stanford-ner-3.9.2.jar')

    ner_tagger = CoreNLPNERTagger()

    # print("Running pre-processing in following order:")
    # print("Lowercase text")
    # print("Tokenize by nltk.word_tokenize")
    # print("Remove punctuation")

    # filter_name = create_args_filter_name(args)  # create variable to name file as used filters for identification
    # print("Filters in use:",filter_name)
    print()

    # Collect article text files
    txt_files = find_text_files(read_path)

    # # Line graph intended message indicators from articles
    # article_filter_line = []
    #
    # # Bar chart intended message indicators from articles
    # article_filter_bar = []

    # list of stopwords
    Stopwords = stopwords.words('english')

    # lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Stemmer
    stemmer = PorterStemmer()

    # count tokens from all articles:
    c_raw = Counter()  # count tokens for each without pre-processing
    c_raw_total = Counter()  # count all article tokens without pre-processing
    c_article1 = Counter()  # count tokens with stemming and pos_tags NN, VB, JJ
    c_processed = Counter()  # count tokens for each article after pre-processing
    c_processed_total = Counter()  # count all article tokens after pre-processing

    # create labeled data lists to store all labeled data
    all_line_label_data = []  # store all line labeled data
    all_bar_label_data = []  # store all bar labeled data

    # create dictionary to store all pos tags
    all_pos_dict = defaultdict(list)

    # # data load notifier
    # if use_both_data or use_bar_data or use_line_data:
    #     print("Using labeled data only")
    # else:
    #     print("Using whole article text")
    #
    # print()





    # scrape tokens from articles in txt format
    for txt_file in txt_files:
        filename = txt_file.split(".")  #  save filename
        print("Read file:", filename[1])

        ########### open txt file from article:
        infile = open(txt_file, 'r', encoding="utf8", errors='ignore')
        content = infile.read().lower() ## lowercase pre-processing and store content as a string

        ########### tokenize by NLTK
        sentences = nltk.sent_tokenize(content) # = reading whole article text or labeled data (depends on arguments in terminal)

        for index, sentence in enumerate(sentences):
            no_ws_sentence = sentence.split()  #removed whitespaces
            no_ws_sentence = " ".join(no_ws_sentence)
            if no_ws_sentence.startswith(""):
                print("Sentence nr:", index)
                print("".join(no_ws_sentence))
                tokenized_sentence = nltk.word_tokenize(sentence)
                NER_tags = st.tag([word for word in tokenized_sentence])

                for tag in NER_tags:
                    if tag[1] != 'O': # nertags are tuples with item, tag

                        print("Sentence:", index, "tag:", tag)

                ####################################################################
                # WordNet tagger
                WN_tags = []
                original_tokens = []


                for token in tokenized_sentence:
                    original_tokens.append(token)
                    WN_TAG = ""
                    tag = nltk.pos_tag([token]) # get post tag from token
                    sett = False
                    lemma = lemmatizer.lemmatize(token, wordnet.NOUN)
                    Synsets = wordnet.synsets(lemma, pos="n")


                    ## get most frequent synset name from synsets
                    synsets = wordnet.synsets(token)
                    synset_name = ""
                    synset_counter = Counter()
                    for synset in synsets:
                        # print(synset.name())
                        synset_name = synset.name().split(".")[0]
                        synset_counter[synset_name] += 1
                        # print(synset_name)

                    if synset_counter[synset_name]:
                        print(token, "tagged as:", synset_counter.most_common(1)[0][0])

                    most_freq_synset_name = synset_counter.most_common(1)[0][0]
                    Synsets = wordnet.synsets(most_freq_synset_name, pos="n")







                    for synset in Synsets:

                        if hypernymOf(synset, , pos="n")[0]):
                            WN_TAG = synset.name()
                            sett = True
                            break

                        elif hypernymOf(synset, wordnet.synsets("attribute", pos="n")[0]):
                            WN_TAG = "ATTR"
                            sett = True
                            break

                        elif hypernymOf(synset, wordnet.synsets("location", pos="n")[0]):
                            WN_TAG = "LOCATION"
                            sett = True
                            break

                        elif hypernymOf(synset, wordnet.synsets("person", pos="n")[0]):
                            WN_TAG = "PERSON"
                            sett = True
                            break


                        # for instance in synset.instance_hypernyms():
                        #     if sett == False:
                        #
                        #
                        #         if hypernymOf(synset, wordnet.synsets("time_period", pos="n")[0]):
                        #             WN_TAG = "TIME"
                        #             sett = True
                        #             break
                        #
                        #         elif hypernymOf(synset, wordnet.synsets("attribute", pos="n")[0]):
                        #             WN_TAG = "ATTR"
                        #             sett = True
                        #             break
                        #
                        #         elif hypernymOf(synset, wordnet.synsets("location", pos="n")[0]):
                        #             WN_TAG = "LOCATION"
                        #             sett = True
                        #             break
                        #
                        #         elif hypernymOf(synset, wordnet.synsets("person", pos="n")[0]):
                        #             WN_TAG = "PER"
                        #             sett = True
                        #             break

                    if not sett:
                        WN_TAG = token

                    sett = False
                    WN_tags.append(WN_TAG)

                print()
                print()
                # End WordNet tagger
                ####################################################################
                # for tagx in WN_tags:
                #     if tagx != "X":
                #         print(token, tagx)

            print(" ".join(original_tokens))
            print(" ".join(WN_tags))



        # print(tokens)
        # ########### apply pre-processing:
        # tokens, removed_punctuation = remove_punctuation(tokens)
        # tokens, removed_article_words = remove_article_words(tokens)
        # tokens = minimum_length(tokens, minimum_token_length)  # filter out tokens if less then 4 characters

        # ########### apply n-grams processing by NLTK
        # bigrams = [" ".join(token) for token in nltk.bigrams(tokens)]
        # trigrams = [" ".join(token) for token in nltk.trigrams(tokens)]


        # #### POS TAGGING
        #
        # # pos tagging each article
        # pos_tags = nltk.pos_tag(tokens)
        # pos_dict = defaultdict(list)
        # for pos_tag in pos_tags:
        #     tag = pos_tag[1]
        #     token = pos_tag[0]
        #     pos_dict[tag].append(token)
        #     all_pos_dict[tag].append(token)

        # ########### token information
        # total_tokens = len(tokens)
        # types = len(set(tokens))
        # if total_tokens + types > 0:
        #     ttr = types/total_tokens
        # else:
        #     ttr = 0
        #
        # ########### count tokens after processing
        # # NOTE, count for all articles
        # for token in tokens:
        #     c_processed_total[token] += 1
        #
        # ########### count tokens after processing
        # # NOTE, count for each article
        # for token in tokens:
        #     c_processed[token] += 1

        #####begin article methods######
        ######### article 1:
        # """ article simple bar charts:
        # We compiled a set of helpful verbs and adjectives
        # (identified through our corpus study, WordNet [67] and a thesaurus [48]) and
        # manually divided them into similarity classes; for example, the verbs rise and
        # soar were placed in the same class, whereas the verbs lag and trail were placed in
        # a different class.
        # Adjectives derived from verbs, such as soaring, are treated as
        # verbs. We then used a part-of-speech tagger and a stemmer to implement a type
        # of shallow processing of captions to identify ) the presence of one of our verb
        # or adjective classes (adjectives and nouns derived from verbs, such as “soaring”,
        # are reduced to their root form and treated as verbs) and 2) nouns which match
        # the label of a data element in the bar chart. """

        # for token in pos_tags_in_article:
        #     c_article1_raw[token] += 1
        #
        # for token in pos_tags_in_article:
        #     stemmed = stemmer.stem(token)
        #     c_article1[stemmed] += 1

        #####end article methods######

        ######################################################
        #create directory name(s) where to store analysis file(s)
        new_filename = str(filename[1])
        new_filename = new_filename.split("/")
        new_filename = "".join(new_filename[1:-1])
        if not os.path.exists(new_filename+"/analysis/"):
            new_filename = str(filename[1])
            new_filename = new_filename.split("/")
            new_filename = "/".join(new_filename[1:-1])
            os.makedirs(new_filename+"/analysis/", exist_ok=True)

        # Collect number of graphs from article
        image_files = find_image_files(new_filename)

        # #create lists to store applied filters and options
        # names, options = create_filter_names(filter_name)
        #
        # short_file_name = "".join([x[:3]+"_" for x in filter_name.split("_")])

    #     # write article summaries
    #     with open(new_filename+"/analysis/"+short_file_name+"_analysis.txt", "w") as outfile:
    #         outfile.write("Article: "+new_filename+"\n\n")
    #         outfile.write("Tokenized by nltk.word_tokenize \n")
    #         outfile.write("Token analysis before pre-processing \n")
    #         outfile.write("Raw number of tokens: "+str(raw_total_tokens)+"\n")
    #         outfile.write("Raw number of types: "+str(raw_types)+"\n")
    #         outfile.write("Raw Type token ratio (higher = more diversity in language use): "+str(raw_ttr)+"\n\n")  # higher = more diverse in language
    #         outfile.write("100 most freq tokens before (pre)processing: \n"+str(c_raw.most_common(100))+"\n\n")
    #
    #         outfile.write("Applied pre-processing:\n")
    #         outfile.write("Lowercased all tokens \n")
    #         outfile.write("Tokens below minimum token length "+str(minimum_token_length)+" filtered out\n")
    #         outfile.write("Punctuation filtered out "+str(removed_punctuation)+"\n")
    #         outfile.write("Words filtered out: "+str(removed_article_words)+"\n\n")
    #
    #         outfile.write("Applied filters: \n")
    #         for name, option in zip(names, options):
    #             outfile.write(name+" = "+option+"\n")
    #         outfile.write("\n")
    #
    #         outfile.write("Token analysis after pre-processing \n")
    #         outfile.write("Number of tokens: "+str(total_tokens)+"\n")
    #         outfile.write("Number of types: "+str(types)+"\n")
    #         outfile.write("Type token ratio: "+str(ttr)+"\n")  # higher = more diverse in language
    #         outfile.write("\n")
    #
    #         outfile.write("Used nouns, verbs and adjectives in article: \n")
    #         outfile.write("(tokens separated by , ) \n")
    #         for tag, tokens in pos_dict.items():
    #             if tag.startswith("NN") or tag.startswith("V") or tag.startswith("J"):
    #                 # enable to show unique pos tagged tokens in analysis file
    #                 if unique_pos_tokens:
    #                     tokens = set(tokens)
    #                 line = tag,', '.join(tokens)
    #                 outfile.write(str(line)+'\n\n')
    #
    #         outfile.write("100 most freq tokens after processing: \n"+str(c_processed.most_common(100))+"\n")
    #
    #     # write amount of graphs in article
    #     with open(new_filename+"/analysis/amount_of_graphs.txt", "w") as outfile:
    #         outfile.write("Article: "+new_filename+"\n\n")
    #         outfile.write("Number of graphs: "+str(len(image_files))+"\n")
    #
    # print("Done reading.")
    #
    # ####### print results in terminal
    # print()
    # print("----------------------------------------------------------------------")
    # print("Overview of all data")
    # print("NOTE: All tokens converted to lowercase!")
    # print()
    # print("Raw token count: \n", c_raw_total.most_common(100))
    # print()
    # print("Processed token count: \n", c_processed_total.most_common(100))
    # print()
    # print(len(all_line_label_data), "# of line labels found")
    # print(len(all_bar_label_data), "# of bar labels found")
    # # print(len(pie_data), "# of pie labels found")
    # # print(len(scatter_data), "# of scatter labels found")

    # # write general overview
    # with open("general_analysis_"+short_file_name+"_analysis.txt", "w") as outfile:
    #     outfile.write("NOTE: All tokens converted to lowercase!\n")
    #     outfile.write("Applied filters: \n")
    #     for name, option in zip(names, options):
    #         outfile.write(name+" = "+option+"\n")
    #     outfile.write("\n")
    #     outfile.write("Raw 100 most freq tokens: \n"+str(c_raw_total.most_common(100))+"\n\n")
    #
    #     outfile.write("Used nouns, verbs and adjectives: \n")
    #     outfile.write("(tokens separated by , ) \n")
    #     for tag, tokens in all_pos_dict.items():
    #         if tag.startswith("NN") or tag.startswith("V") or tag.startswith("J"):
    #             # enable to show unique pos tagged tokens in analysis file
    #             if unique_pos_tokens:
    #                 tokens = set(tokens)
    #             line = tag,', '.join(tokens)
    #             outfile.write(str(line)+'\n\n')
    #
    #     outfile.write("Processed 100 most freq tokens: \n"+str(c_processed_total.most_common(100))+"\n")

    #####begin article methods######
    # generate overview of article methods
    # print("Article 1 token count: \n", c_article1_raw.most_common(50))
    # print()
    # print("Article 1 stemmed token count: \n", c_article1.most_common(50))
    #####end article methods######

    #  print labeled data
    # for bar in bar_data:
    #     print(bar)
    #
    # for line in line_data:
    #     print(line)
    #
    # for pie in pie_data:
    #     print(pie)


def main():
    # Read arguments
    parser = argparse.ArgumentParser(description='NN parameters')
    parser.add_argument('--stopwords', action='store_true', help='Filter stop words')
    parser.add_argument('--lemmatize', action='store_true', help='Use lemmatizer')
    parser.add_argument('--stemmer', action='store_true', help='Use stemmer')
    parser.add_argument('--minimumtokenlength', '--tl', type=int, default=2, help='Set minimum token length')
    parser.add_argument('--bigrams', action='store_true', help='Use bigrams')
    parser.add_argument('--trigrams', action='store_true', help='Use trigrams')
    parser.add_argument('--showuniquepostagtokens', '--upos', action='store_true', help='Show unique pos tagged tokens instead of all pos tagged tokens')
    parser.add_argument('--linelabelsonly', '--line', action='store_true', help='Use labeled line data as content')
    parser.add_argument('--barlabelsonly', '--bar', action='store_true', help='Use labeled bar data as content')
    parser.add_argument('--bothlabels', '--both', action='store_true', help='Use labeled bar and line data as content')

    args = parser.parse_args()

    generate_overview("./test")
    print("Done.")

if __name__ == '__main__':
    main()
