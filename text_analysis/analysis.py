# -*- coding: utf-8 -*-
import os
from collections import Counter
import io
import nltk
from collections import defaultdict
import errno
import json
import pyexcel as pe
from pyexcel_xlsx import get_data
from pyexcel_xlsx import save_data
import spacy
from spacy import displacy

# Writing to an excel
# sheet using Python
import xlwt
from xlwt import Workbook



def find_text_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return [path for path in paths if path.endswith(".txt") and not path.endswith("analysis.txt") and not path.endswith("amount.txt") and not path.endswith("_graphs.txt") and not path.endswith("segmented.txt") and not path.endswith("with_labels.txt")]


def find_xlsx_file(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return [path for path in paths if path.endswith("article_text_analysis.xlsx")]


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def segmentate(read_path):
    # Collect article text files
    txt_files = find_text_files(read_path)

    # scrape tokens from articles in txt format
    for txt_file in txt_files:
        filename = txt_file.split(".")  #  save filename
        print("Read file:", filename[1])

        ######################################################
        #create directory name(s) where to store segmentation file(s)
        new_filename = str(filename[1])
        new_filename = new_filename.split("/")
        new_filename = "".join(new_filename[1:-1])
        if not os.path.exists(new_filename+"/segmentation/"):
            new_filename = str(filename[1])
            new_filename = new_filename.split("/")
            new_filename = "/".join(new_filename[1:-1])
            os.makedirs(new_filename+"/segmentation/", exist_ok=True)

        # print(new_filename)  # print directory name in terminal

        ########### open article txt file:
        infile = open(txt_file, 'r', encoding="utf8", errors='ignore')
        content = infile.read() ## lowercase pre-processing and store content as a string

        ########### Apply sentence tokenizer by NLTK
        sentences = nltk.sent_tokenize(content)

        with open(new_filename+"/segmentation/"+"segmented.txt", "w") as outfile:
            print(new_filename)
            for index, sentence in enumerate(sentences):
                no_ws_sentence = sentence.split()  #remove trailing whitespaces
                no_ws_sentence = " ".join(no_ws_sentence)
                # no_ws_sentence = sentence  #keep trailing whitespaces
                if no_ws_sentence.startswith(""):
                    outfile.write("Sentence nr: {0}".format(index))
                    outfile.write("\n")
                    outfile.write("".join(no_ws_sentence))
                    outfile.write("\n")
                    outfile.write("\n")
                    print("Sentence nr:", index)
                    print("".join(no_ws_sentence))
                    print()
                    print()


def analysis(read_path):
    # Collect text analysis file
    xlsx_file = './article_text_analysis.xlsx'
    print("Converting:", xlsx_file)
    data = get_data('./article_text_analysis.xlsx', start_row=1, start_column=3, column_limit=1)

    with open("article_text_analysis.txt", "w") as text_file:
        # print(json.dumps(data))
        for key, values in data.items():
            for item in values:
                sentence = str(item)
                sentence = sentence[2:-2]
                text = nltk.word_tokenize(sentence)
                string_text = str(text)
                bi_grams = nltk.bigrams(text)
                pos_tagged = nltk.pos_tag(text)
                pos_line = str(sentence) + "\n" + str(pos_tagged) + "\n\n"
                text_file.write(pos_line)
                print("Text:", text)
                print("Bi-grams:")
                for bigram in bi_grams:
                    print(bigram)
                print("Pos-tags", pos_line)
                print()

                nlp = spacy.load("en_core_web_sm")
                doc = nlp(string_text)
                for ent in doc.ents:
                    print("Entities:", ent.text, ent.start_char, ent.end_char, ent.label_)
                print()


def main():
    # segmentate("./")
    # print("Segmentation done.")
    analysis("./")

if __name__ == '__main__':
    main()
