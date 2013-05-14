import urllib2
import re
from bs4 import BeautifulSoup
import dateutil.parser
import datetime
import math
import pickle
import unicodedata

class Article(object):
	def __init__(self, title, author, date):
		self.title = title
		self.author = author
		self.date = date
		self.comments = []

class Comment(object):
	def __init__(self, author, date, text):
		self.author = author
		self.date = date
		self.text = text

def scrapeComments(year, month, day, articleNum, commentPage):
	url = 'http://www.dailyprincetonian.com/%s/%s/%s/%s/comments/?p=%s' % (year, month, day, articleNum, commentPage)
	html = urllib2.urlopen(url).read()
	soup = BeautifulSoup(html)

	comments = []

	for commentHtml in soup.find('ul', {'class' : 'comments'}).findAll('li'):
		author = commentHtml.find('span', {'class' : 'post_username'}).text
		time = dateutil.parser.parse(commentHtml.find("div", {"class", "posted_at"}).text.replace('midnight', '12:00 a.m.').replace('noon', '12:00 p.m.'))
		text = commentHtml.find('div', {'class' : 'post_body'}).text.strip()
		comments.append(Comment(author, time, text))

	return comments

def scrapeArticle(year, month, day, articleNum):
	url = 'http://www.dailyprincetonian.com/%s/%s/%s/%s/' % (year, month, day, articleNum)
	html = urllib2.urlopen(url).read()
	soup = BeautifulSoup(html)
	title = soup.find("h1").text
	author = soup.find("span", {'class' : 'authors_people'}).text.strip()
	date = dateutil.parser.parse(soup.find("div", {"class", "published_date"}).text.split(':')[1].strip())
	numCommentPages = int(math.ceil(int(re.search('(\d+)', soup.find("div", {'id' : 'article_comments'}).find('h2').text).groups()[0]) / 10.0)) #int(math.ceil(float( / 10.0))

	article = Article(title, author, date)
	for commentPage in range(1, numCommentPages + 1):
		article.comments.extend(scrapeComments(year, month, day, articleNum, commentPage))
	return article

linkCache = {}

def scrapeIssue(year, month, day):
	url = 'http://www.dailyprincetonian.com/frontpage/%s/%s/%s/' % (year, month, day)
	try:
		html = urllib2.urlopen(url).read()
	except urllib2.HTTPError:
		return None

	articles = []

	links = re.findall('<a href="/(\d+)/(\d+)/(\d+)/(\d+)/"', html)
	for link in links:
		if link not in linkCache:
			articles.append(scrapeArticle(link[0], link[1], link[2], link[3]))
			linkCache[link] = True

	return articles

def scrapeSearchPage(url):
	try:
		html = urllib2.urlopen(url).read()
	except urllib2.HTTPError:
		return None

	articles = []

	links = re.findall('<a href="/(\d+)/(\d+)/(\d+)/(\d+)/"', html)
	for link in links:
		if link not in linkCache:
			articles.append(scrapeArticle(link[0], link[1], link[2], link[3]))
			linkCache[link] = True

	return articles

def writeBuffer(articles):
	filename = "corpus"
	f = open(filename, 'a')
	for article in articles:
		for comment in article.comments:
			text = unicodedata.normalize('NFKD', comment.text).encode('ascii', 'ignore')
			f.write(text + "\n")
	f.close()

def archiveByIssues():
	archive = []

	# years = map(str, range(2013, 2007, -1))
	years = ['2013']
	# months = map(str, range(1, 13))
	months = ['04', '05']
	days = map(str, range(1, 32))
	for year in years:
		for month in months:
			for day in days:
				issue = scrapeIssue(year, month, day)
				if issue:
					archive.extend(issue)

	return archive

def archiveBySearch():
	archive = []
	for page in range(1, 1500):
		print page
		url = 'http://www.dailyprincetonian.com/advanced_search/?end_date=&author=&text=a&section=Any&p=%d&start_date=' % page
		try:
			search = scrapeSearchPage(url)
			if search:
				archive.extend(search)
				writeBuffer(search)
		except:
			pass
	return archive

archiveBySearch()

# f = open('archive', 'w')
# pickle.dump(archiveByIssues(), f)
# f.close()

