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


def generate_overview(read_path):

    # Construct Standford NER tagger
    st = StanfordNERTagger('stanford-ner-2018-10-16/classifiers/english.muc.7class.distsim.crf.ser.gz', 'stanford-ner-2018-10-16/stanford-ner-3.9.2.jar')
    ner_tagger = CoreNLPNERTagger()

    # Collect article text files
    txt_files = find_text_files(read_path)

    # list of stopwords
    Stopwords = stopwords.words('english')

    # lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Stemmer
    stemmer = PorterStemmer()

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
                NER_Tags = st.tag([word for word in tokenized_sentence])


                ####################################################################
                # WordNet tagger
                WN_tags = []
                original_tokens = []
                digit_tags = []

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
                        synset_name = synset.name().split(".")[0]
                        synset_counter[synset_name] += 1

                    if synset_counter[synset_name]:
                        # print(token, "tagged as:", synset_counter.most_common(1)[0][0])
                        most_freq_synset_name = synset_counter.most_common(1)[0][0]


                    for synset in Synsets:
                        if hypernymOf(synset, wordnet.synsets("attribute", pos="n")[0]):
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

                    if not sett:
                        WN_TAG = token

                    sett = False
                    WN_tags.append(WN_TAG)


                # End WordNet tagger
                ####################################################################

                    amount_words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

                    # digit tagger
                    if token.isdigit() or token in amount_words:
                        token = "AMOUNT"

                    digit_tags.append(token)

            # print(" " + " ".join(original_tokens), "ORIGINAL")
            print(" " + " ".join(WN_tags), "WN")
            ner_sentence = ""
            for ner_tag, og_token in zip(NER_Tags, original_tokens):
                if ner_tag[1] == "O":
                    ner_sentence = ner_sentence + " " + og_token
                else:
                    ner_sentence = ner_sentence + " " + ner_tag[1]
            print(ner_sentence, "NER")
            print(" " + " ".join(digit_tags), "AMOUNT")

            print()
            print()



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


def main():
    generate_overview("./alcohol-consumption")
    print("Done.")

if __name__ == '__main__':
    main()
