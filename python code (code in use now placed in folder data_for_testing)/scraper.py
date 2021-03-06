import os
import requests
from bs4 import BeautifulSoup
from collections import Counter
import io
from urllib.request import urlretrieve
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

	for md_fl in md_files:
		md_fl = md_fl.rstrip()
		c = 0
		infile = open(md_fl, encoding="utf8")
		for line in infile:
			tokens = line.split('(')
			for token in tokens:
				if token.startswith("http://fivethirtyeight.com/features") or token.startswith("https://projects.fivethirtyeight.") or token.startswith("https://fivethirtyeight.com/features") or token.startswith("http://fivethirtyeight.com/datalab") or token.startswith("https://fivethirtyeight.com/datalab"):
					url = token.rstrip()
					url = clean_url(url)
					c += 1
					tuple = md_fl, url
					md_urls.append(tuple)

	return md_urls


def scrape(read_path):
	c = 0
	md_files = read_md_files(read_path)
	md_urls = get_md_urls(md_files)
	success_counter = 0

	#scrape articles from readme urls
	for x in md_urls:
		print(x)
		url_name = x[1].split('/')[-1]
		print(url_name)
		scraped_article_images = []
		image_urls = []
		folder = x[0][:-10]
		filename = folder[2:]
		url = x[1]
		img_counter = 0

		# load html content
		page = requests.get(url)
		soup = BeautifulSoup(page.text, 'html.parser')

		# scrape article text
		try:
			scraped_article_text = soup.find('article').text
			success_counter += 1
		except:
			print("{0} not found".format(url))

		# scrape and save images from article
		tags = [tag for tag in soup.find_all('article')]
		for tag in tags:
			imgTag = tag.find_all('img')
			for img in imgTag:
				img_counter += 1
				try:
					urlretrieve(img['src'], folder+"/"+url_name+"_image_"+str(img_counter)+".png")
				except:
					continue

			# scrape Viz tags????
			# VizTag = tag.find_all('section', {"class": "viz"})
			# for viz in VizTag:
			# 	img_counter += 1
			# 	urlretrieve(viz['src'], folder+"/"+url_name+"_image_"+str(img_counter)+".png")

		# save article text
		with io.open(folder+"/"+url_name+".txt", "w", encoding="utf-8") as outfile:
		    outfile.write(scraped_article_text)

		# print the scarped article
		print(folder+" Article scraped")
		print()

	# print amount of readme files found
	for x in md_files:
		c += 1
	print("Readme files found", c)

	# print amount of article urls found
	c = 0
	for x in md_urls:
		c += 1
	print("Article url's found", c)

	# print amount of articles scraped:
	print("Articles scraped", success_counter)


def main():
	scrape("./")


if __name__ == '__main__':
	main()