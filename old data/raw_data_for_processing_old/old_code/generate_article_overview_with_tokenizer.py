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

def find_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return [path for path in paths if path.endswith(".txt") and not path.endswith("summary.txt") and not path.endswith("tokenizer.txt")]


def remove_article_words(tokens):
        clean_tokens = []
        word_filter = ['facebooktwitteremail', '']
        for token in tokens:
            if token not in word_filter:
                clean_tokens.append(token)

        return clean_tokens


def remove_punctuation(tokens):
    clean_tokens = []
    # keep '%' in punctuation
    punctuation = ['!', '"', '#', '$', '&', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', "=", '>', '?',
        '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', '“', '’', '”', '—']

    for token in tokens:
        # print(token)
        clean_token = ""
        for char in token:
            if char not in punctuation:
                clean_token = clean_token + char
            else:
                clean_token = clean_token + ""
        if clean_token != "":
            clean_tokens.append(clean_token)

    return clean_tokens


def generate_overview(read_path):
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

    # scrape tokens from articles in txt format
    for txt_file in txt_files:
        # counters for each article:
        c_raw = Counter()  # count tokens without pre-processing
        c_filtered_stopwords = Counter()  # count tokens with stopwords filtered outs
        c_lemmatized = Counter()  # count tokens with lemmatization filter
        c_stemmed = Counter()  # count tokens with stemming filter
        c_lemmatized_stopwords = Counter()  # count tokens lemmatized and stop words filtered out
        c_lemmatized_stopwords_custom = Counter()  # count tokens lemmatized, stop words filtered out + custom filter
        c_lemmatized_stopwords_pos_tagged = Counter()  # count tokens lemmatized, stop words filtered out + pos_tags
        c_article1_raw = Counter()
        c_article1 = Counter()  # count tokens with stemming and pos_tags NN, VB, JJ

        txt_tokens = []  # create list to store tokens from article text
        pos_tags_in_article = []  # create list to store the pos tags

        filename = txt_file.split(".")  #  save filename

        # open txt file from article:
        infile = open(txt_file, 'r', encoding="utf8", errors='ignore')
        content = infile.read().lower()

        # tokenize by NLTK
        tokenized = nltk.word_tokenize(content)
        for token in tokenized:
            c_raw[token] += 1

        # apply pre-processing:
        tokenized = remove_punctuation(tokenized)
        tokenized = remove_article_words(tokenized)

        # # custom filter
        # custom_filtered = [word for word in tokenized if word not in custom_filter]

        # # lemmatize, stopwords and custom filter
        # custom_and_stopwords_filtered = [word for word in custom_filtered if word not in Stopwords]
        # for token in custom_and_stopwords_filtered:
        #     lemmatized = lemmatizer.lemmatize(token)
        #     c_lemmatized_stopwords_custom[lemmatized] += 1

        ################
        # pos tagging
        pos_tags = nltk.pos_tag(tokenized)
        pos_dict = defaultdict(list)
        for pos_tag in pos_tags:
            tag = pos_tag[1]
            token = pos_tag[0]
            # print(tag)
            if tag.startswith("V") or tag.startswith("J") or tag.startswith("NN"):  # JJR = comparative adjective (from article simple bar chart), NN = NOUN (from article), VB = Verb (from article)
                pos_tags_in_article.append(token)  # collect verbs and adjectives

            # store all POS tags in dictionary
            pos_dict[tag].append(token)


        ################
        # filter stopwords
        stopwords_filtered = [word for word in tokenized if word not in Stopwords]
        for token in stopwords_filtered:
            c_filtered_stopwords[token] += 1  # count token

        # lemmatize tokens
        for token in tokenized:
            lemmatized = lemmatizer.lemmatize(token)
            c_lemmatized[lemmatized] += 1

        # Stem tokens
        for token in tokenized:
            stemmed = stemmer.stem(token)
            c_stemmed[stemmed] += 1

        # lemmatize and stopwords filter
        for token in stopwords_filtered:
            lemmatized = lemmatizer.lemmatize(token)
            c_lemmatized_stopwords[lemmatized] += 1

        # lemmatize, stopwords and pos tagged VERBS
        pos_tag_and_stopwords_filtered = [word for word in pos_tags_in_article if word not in Stopwords]
        for token in pos_tag_and_stopwords_filtered:
            lemmatized = lemmatizer.lemmatize(token)
            c_lemmatized_stopwords_pos_tagged[lemmatized] += 1


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

        for token in pos_tags_in_article:
            c_article1_raw[token] += 1

        for token in pos_tags_in_article:
            stemmed = stemmer.stem(token)
            c_article1[stemmed] += 1

        ######################################################
        # write article summaries
        with open("."+filename[1]+"_summary_tokenizer.txt", "w") as outfile:
            outfile.write("POS tags: \n Tokens separated by ---- \n")
            for tag, tokens in pos_dict.items():
                if tag.startswith("NN") or tag.startswith("V") or tag.startswith("J"):
                    line = tag,'----'.join(tokens)
                    outfile.write(str(line)+'\n')


            outfile.write("\n")
            outfile.write("Token analysis after pre-processing \n")
            outfile.write("Number of tokens: "+str(len(tokenized))+"\n")
            outfile.write("Number of types: "+str(len(set(tokenized)))+"\n")
            outfile.write("Type token ratio: "+str(len(set(tokenized)) / len(tokenized))+"\n")  # higher = more diverse in language
            outfile.write("\n")
















    # ####### print results in terminal
    # print("NOTE: All tokens converted to lowercase!")
    # print()
    # print("Raw token count: \n", c_raw.most_common(50))
    # print()
    # print("Stopwords filter token count: \n", c_filtered_stopwords.most_common(50))
    # print()
    # print("Lemmatization token count: \n", c_lemmatized.most_common(50))
    # print()
    # print("Stemming token count: \n", c_stemmed.most_common(50))
    # print()
    # print("Lemmatization and stopwords filter token count: \n", c_lemmatized_stopwords.most_common(50))
    # print()
    # print("Lemmatization, stopwords filter, custom filter token count: \n", c_lemmatized_stopwords_custom.most_common(50))
    # print()
    # print("Lemmatization, stopwords filter, post_tagged (verbs) token count: \n", c_lemmatized_stopwords_pos_tagged.most_common(50))
    # print()
    # print("Article 1 token count: \n", c_article1_raw.most_common(50))
    # print()
    # print("Article 1 stemmed token count: \n", c_article1.most_common(50))


def main():
    generate_overview("./")
    print("Done.")

if __name__ == '__main__':
    main()
