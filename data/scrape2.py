import os
import requests
from bs4 import BeautifulSoup
from collections import Counter
import io
import re

def find_files(directory):
	paths = []
	for root, directories, files in os.walk(directory):
		for filename in files:
			filepath = os.path.join(root, filename)
			paths.append(filepath)
	return [path for path in paths if path.endswith(".md")]


def read_md_files(read_path):
	print("reading .md files...")
	md_files = []
	for fl in find_files(read_path):
		md_files.append(fl)

	return md_files


def clean_url(url):
	if url[-1] == ".":
		url = url[:-1]

	if url[-1] == ")":
		url = url[:-1]

	if url[-1] == "/":
		url = url[:-1]

	return url


def get_md_urls(md_files):
	md_urls = []
	# c = 0
	for md_fl in md_files:
		md_fl = md_fl.rstrip()
		c = 0
		# with open(md_fl, "r") as infile:
		infile = open(md_fl, encoding="utf8")
		for line in infile:
			tokens = line.split('(')
			for token in tokens:
				if token.startswith("http://fivethirtyeight.com/features") or token.startswith("https://fivethirtyeight.com/features") or token.startswith("http://fivethirtyeight.com/datalab") or token.startswith("https://fivethirtyeight.com/datalab"):
					url = token.rstrip()
					url = clean_url(url)
					c += 1

		if c == 1:
			# print(md_fl)
			tuple = md_fl, url
			md_urls.append(tuple)

	return md_urls


def scrape(read_path):
	c = 0
	md_files = read_md_files(read_path)
	md_urls = get_md_urls(md_files)

	#scrape articles
	for x in md_urls:
		folder = x[0][:-10]
		filename = folder[2:]
		url = x[1]

		print(folder+" Article scraped")
		print()

		page = requests.get(url)
		soup = BeautifulSoup(page.text, 'html.parser')

		# Pull all text from the BodyText div
		# old one, not working for all articles:
		# y = soup.find(class_='type-fte_features').text

		# working: but got some trash
		# y = soup.find(class_='single-col').text

		# latest try , error is article not found
		y = soup.find('article').text
		with io.open(folder+"/"+filename+".txt", "w", encoding="utf-8") as outfile:
		    outfile.write(y)

	# #counters
	# for x in md_files:
	# 	c += 1
	# print(c)

	# c = 0
	# for x in md_urls:
	# 	c += 1
	# print(c)


def main():
	scrape("./")


if __name__ == '__main__':
	main()