from Utils import *
from KissParser import *

class KissCrawler(threading.Thread):
	def __init__(self, html=None):#, kissParser=KissParser('https://kissanime.to/MyList/1132864'), html=None):
		threading.Thread.__init__(self)
		# self.kissParser = kissParser if kissParser is not None else KissParser()
		self.scraper = GetScraper()
		self.animeEntities = []
		self.crawlers = []
		self.kissParsers = []
		self.html = html

	def run(self):
		self.GatherAnime(self.html)

	def GatherAnime(self, pageCount):
		html = self.SplitToListOfHtmls(self.html)
		crawlerRegexQuery = [r'<a\shref(?:[^\>])+>\s*(?P<AnimeName>[^\<]+)', r'<a\shref="(?P<Link>[^\"]+)']

		kissParser = KissParser('https://kissanime.to/MyList/1132864')
		kissParser.GetListOfKissAnimeEntities(crawlerHtmls=html, crawlerRegexQuery=crawlerRegexQuery)
		self.kissParsers.append(kissParser)
		# self.animeEntities += self.kissParser.animeEntities
		# self.kissParser.animeEntities = []

	def CrawlForAnime(self):
		pageCount = 0
		while True:
			# if pageCount == 1:
				# break;

			Debug.Log('[KissCrawler] Trying to connect to ', str('http://kissanime.to/AnimeList?page=' + str(pageCount)))
			# print('[KissCrawler] Trying to connect to', str('http://kissanime.to/AnimeList?page=' + str(pageCount)))
			response = ScrapeHtml(str(str('http://kissanime.to/AnimeList?page=' + str(pageCount))), scraper=self.scraper)
			if response is not None:
				# Debug.Log('[KissCrawler] Response code - ', response.status_code, ' contains \'Not found\' - ', str(self.ContainsNotFound(response.text)))
				
				if response.status_code != 200 or self.ContainsNotFound(RemoveHtmlTrash(str(response.content))):
					self.CleanUp()
					break;
			
				crawler = KissCrawler(html=RemoveHtmlTrash(str(response.content)))
				crawler.start()
				self.crawlers.append(crawler)
				time.sleep(1)
			else:
				Debug.Log('[KissCrawler] Something went wrong url=', str('http://kissanime.to/AnimeList?page=' + str(pageCount)))
				pageCount += 1
				continue

			if pageCount % 30 == 0:
				self.CleanUp()
			
			pageCount += 1	

	def CleanUp(self):
		Debug.Log('[KissCrawler] Periodical cleanup...')
		areAlive = True
		while areAlive:
			areAlive = False
			for crawler in self.crawlers:
				if crawler.isAlive():
					areAlive = True
					time.sleep(2)	

		# for crawler in self.crawlers:
		# 	for kissParser in crawler.kissParsers:
		# 		for animeEntity in kissParser.animeEntities:
		# 			animeEntity.Print()

		for crawler in self.crawlers:
			for kissParser in crawler.kissParsers:
				kissParser.SyncWithDatabase()	

		for crawler in self.crawlers:
			crawler.join(0.5)		

	def SplitToListOfHtmls(self, html):
		listOfHtmls = regex.split(r'(?:<tr>.+?<td)|(?:<tr\sclass=\"odd\")()', html)
		listOfHtmls = list(filter(None, listOfHtmls))
		return listOfHtmls[1:]

	def ContainsNotFound(self, html):
		regexResult = regex.findall(r'(Not\sfound)', RemoveHtmlTrash(html))
		if len(regexResult) == 1:
			return True
		else:
			return False


# total anime count in mal = 10856