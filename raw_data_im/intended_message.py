import os
from collections import Counter
import io
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
import nltk

def find_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return [path for path in paths if path.endswith(".txt")]


def collect_intended_message(read_path):
    # Collect article text files
    txt_files = find_files(read_path)

    # counters:
    c_raw = Counter()  # count tokens without pre-processing
    c_filtered_stopwords = Counter()  # count tokens with stopwords filtered outs
    c_lemmatized = Counter()  # count tokens with lemmatization filter
    c_stemmed = Counter()  # count tokens with stemming filter
    c_lemmatized_stopwords = Counter()  # count tokens lemmatized and stop words filtered out
    c_lemmatized_stopwords_custom = Counter()  # count tokens lemmatized, stop words filtered out + custom filter
    c_lemmatized_stopwords_pos_tagged = Counter()  # count tokens lemmatized, stop words filtered out + pos_tags

    # custom word filter
    custom_filter = ['--', '-', '—', 'trump:', '...']

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
        txt_tokens = []
        verbs_in_article = []
        infile = open(txt_file, 'r',  errors='ignore')
        for line in infile:
            tokens = line.split()
            for token in tokens:
                token = token.lower()  # lowercase all the tokens!!!!!!
                c_raw[token] += 1  # raw token count
                txt_tokens.append(token)  # store tokens in list for pre-processing

        # filter stopwords
        stopwords_filtered = [word for word in txt_tokens if word not in Stopwords]
        for token in stopwords_filtered:
            c_filtered_stopwords[token] += 1  # count token

        # lemmatize tokens
        for token in txt_tokens:
            lemmatized = lemmatizer.lemmatize(token)
            c_lemmatized[lemmatized] += 1

        # Stem tokens
        for token in txt_tokens:
            stemmed = stemmer.stem(token)
            c_stemmed[stemmed] += 1

        # lemmatize and stopwords filter
        for token in stopwords_filtered:
            lemmatized = lemmatizer.lemmatize(token)
            c_lemmatized_stopwords[lemmatized] += 1

        # custom filter
        custom_filtered = [word for word in txt_tokens if word not in custom_filter]

        # lemmatize, stopwords and custom filter
        custom_and_stopwords_filtered = [word for word in custom_filtered if word not in Stopwords]
        for token in custom_and_stopwords_filtered:
            lemmatized = lemmatizer.lemmatize(token)
            c_lemmatized_stopwords_custom[lemmatized] += 1

        # pos tagging
        pos_tags = nltk.pos_tag(txt_tokens)
        for pos_tag in pos_tags:
            tag = pos_tag[1]
            token = pos_tag[0]
            if tag == "VB":
                verbs_in_article.append(token)  # collect verbs

        # lemmatize, stopwords and pos tagged VERBS
        pos_tag_and_stopwords_filtered = [word for word in verbs_in_article if word not in Stopwords]
        for token in pos_tag_and_stopwords_filtered:
            lemmatized = lemmatizer.lemmatize(token)
            c_lemmatized_stopwords_pos_tagged[lemmatized] += 1

    #print(verbs_in_article)
    #print(text)

    print("NOTE: All tokens converted to lowercase!")
    print()
    print("Raw token count: \n", c_raw.most_common(50))
    print()
    print("Stopwords filter token count: \n", c_filtered_stopwords.most_common(50))
    print()
    print("Lemmatization token count: \n", c_lemmatized.most_common(50))
    print()
    print("Stemming token count: \n", c_stemmed.most_common(50))
    print()
    print("Lemmatization and stopwords filter token count: \n", c_lemmatized_stopwords.most_common(50))
    print()
    print("Lemmatization, stopwords filter, custom filter token count: \n", c_lemmatized_stopwords_custom.most_common(50))
    print()
    print("Lemmatization, stopwords filter, custom filter token count: \n", c_lemmatized_stopwords_pos_tagged.most_common(50))

def main():
    collect_intended_message("./")


if __name__ == '__main__':
    main()
