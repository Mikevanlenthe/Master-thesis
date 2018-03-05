import urllib3
from bs4 import BeautifulSoup

http = urllib3.PoolManager()

# specify the url
quote_page = 'https://fivethirtyeight.com/features/should-travelers-avoid-flying-airlines-that-have-had-crashes-in-the-past/'

# query the website and return the html to the variable ‘page’
page = http.request('POST', quote_page, fields={'hello': 'world'})
print(page)
# parse the html using beautiful soup and store in variable `soup`
soup = BeautifulSoup(page, 'html.parser')

# Take out the <div> of name and get its value
name_box = soup.find('article id', attrs={'class': 'post'})

#name = name_box.text.strip() # strip() is used to remove starting and trailing
print(name_box)