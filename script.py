from selenium import webdriver
from bs4 import BeautifulSoup
from os import path
import urllib2
import xlrd

class Manager(object):
	"""Manager for this ears script."""
	def __init__(self):
		self.browser = webdriver.Firefox()
		self.URL_BASE = 'http://www.streetinsider.com/ec_earnings.php?q='
		self.current_url = ''
		self.WEEKLIES_XLS_URL = 'https://www.cboe.com/publish/weelkysmf/weeklysmf.xls'
		self.WEEKLIES_XLS_FILE_LOCATION = path.abspath('./temp/weeklies.xls') 

	def buildURL(self, ticker):
		self.current_url = self.URL_BASE + ticker 
				
	def openURL(self):
		browser.get(self.current_url)

	def closeBrowser(self):
		self.browser.close()

	def start(self):
		pass

	def downloadExcel(self):
		print "Download Weeklies Excel document\n"
		response = urllib2.urlopen(self.WEEKLIES_XLS_URL)
		file_handler = open(self.WEEKLIES_XLS_FILE_LOCATION, 'wb')
		file_handler.write(response.read())
		file_handler.close()
		print "Succesflly saved Weeklies Excel document to disk"

	def loadExcelSheet(self):
		book = xlrd.open_workbook(self.WEEKLIES_XLS_FILE_LOCATION)
		sheet = book.sheet_by_index(0)
		print sheet.col(0)[3].value

	
# elem_list =browser.find_elements_by_class_name('is_hilite')
# elem_list =browser.find_element_by_class_name('earning_history')

# elem = browser.page_source()
# browser.close()
# souped = BeautifulSoup(elem)
# souped = BeautifulSoup(elem_list.get_attribute('innerHTML'))
# print souped.tbody.prettify()
# items = souped.find_all(class_ = "is_hilite")

# print(items[0].prettify())

test = Manager()
test.closeBrowser()
test.loadExcelSheet()