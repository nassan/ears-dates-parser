from selenium import webdriver
from bs4 import BeautifulSoup
from os import path
import urllib2
import xlrd
from data_work import data_manager
from sqlalchemy_declaration import Ticker, EarningsDay
import logging

class BrowserManager(object):
	"""Manager for this ears script."""
	def __init__(self):
		self.driver = webdriver.Firefox()
		self.URL_BASE = 'http://www.streetinsider.com/ec_earnings.php?q='
		self.current_url = ''
		self.current_ticker = ''
	
	def buildURL(self, ticker):
		self.current_url = self.URL_BASE + ticker 
		self.current_ticker = ticker 
				
	def openURL(self):
			self.driver.get(self.current_url)

	def startScrape(self):
		scraper = ScraperManager(self.driver.page_source, self.current_ticker)

class ScraperManager(object):
	"""Manages all the scraping methods"""
	def __init__(self, source, ticker):
		self.source = source
		self.souped = BeautifulSoup(source)
		self.ticker = ticker
		self.start()

	def start(self):
		results = []
		
		 
		
		for result in self.souped.find_all(class_ = "earning_history"):
			tr_result  = result.find_all('tr') 
			results.extend(tr_result)

		# Remove classless tr elements
		removeClasslessTrElements = lambda x: True if x.has_attr('class') else False
		results = filter(removeClasslessTrElements,results)

		# Remove tr elements that have dates in the future
		removeFutureTrElements = lambda x: True if "is_future" not in x['class'] else False
		results = filter(removeFutureTrElements,results)

		results = map(lambda x: x.td.contents[0], results) 

		# Find that ticker in parent database and
		# get its id for foreign key of these results
		ticker_entity = data_manager.session.query(Ticker).\
			filter(Ticker.name == self.ticker).first()
		for each in results:
			ticker_entity.earnings_dates.append(EarningsDay(date = each))
		data_manager.session.commit()
		logging.info("Committed earnings dates to database for\t" + self.ticker)

class GeneralManager(object):
	"""Parent manager for the script"""
	def __init__(self):
		self.browser = BrowserManager()
		self.exceller = ExcelManager()
		logging.basicConfig(filename = 'monitor.log',
							filemode = 'w',
							datefmt ='%m/%d/%Y %I:%M:%S %p',
							format ='%(asctime)s \t\t%(message)s',
							level = logging.INFO)		
		
	def start(self):
		self.exceller.buildTickersList()
		# self.exceller.putTickerListToDB()
		print str(len(self.exceller.tickers_list)) + " total locations to parse:"
		counter = 0
		for ticker in self.exceller.tickers_list:
				self.browser.buildURL(ticker)
				logging.info('Scraping: ' + self.browser.current_url)
				self.browser.openURL()
				self.browser.startScrape()
				counter += 1
				print "Percentage completed:\t" + str((100 * float(counter))/float(len(self.exceller.tickers_list)))

		self.browser.driver.close()
		logging.info("Finished iterating through tickers. Database should contain all earnings dates.")
		
class ExcelManager(object):
	"""Manages all the work needed to get information from the excel sheet"""
	def __init__(self):
		self.WEEKLIES_XLS_URL = 'https://www.cboe.com/publish/weelkysmf/weeklysmf.xls'
		self.WEEKLIES_XLS_FILE_LOCATION = path.abspath('./temp/weeklies.xls') 
		self.excel_sheet = object
		self.tickers_list = []
		book = xlrd.open_workbook(self.WEEKLIES_XLS_FILE_LOCATION)
		self.excel_sheet = book.sheet_by_index(0)

	def downloadExcel(self):
		print "Downloading Weeklies Excel document\n"
		response = urllib2.urlopen(self.WEEKLIES_XLS_URL)
		file_handler = open(self.WEEKLIES_XLS_FILE_LOCATION, 'wb')
		file_handler.write(response.read())
		file_handler.close()
		print "Successfully saved Weeklies Excel document to disk"

	def buildTickersList(self):
		self.tickers_list = self.excel_sheet.col(0)

		# Get only the tickers
		getValue = lambda x:x.value
		self.tickers_list = map(getValue, self.tickers_list)

		# Remove duplicate columns
		self.tickers_list = list(set(self.tickers_list))

		# Remove Elements that contain empty strings or non ticker text
		removeNoneTickerElements = lambda x: True if len(x) is not 0 and len(x) <=5 else False
		self.tickers_list = filter(removeNoneTickerElements, self.tickers_list)
		
		#Sort alphabetically 
		self.tickers_list = sorted(self.tickers_list)

	def putTickerListToDB(self):
		for ticker_name in self.tickers_list:
			ticker_item = Ticker(name = ticker_name)
			data_manager.session.add(ticker_item)
		data_manager.session.commit()


test = GeneralManager()
test.start()