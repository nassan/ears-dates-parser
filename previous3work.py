import pymongo
from sqlalchemy_declaration import Ticker, EarningsDay
from data_work import data_manager
import arrow
import requests
import csv
import StringIO
import logging


results  = data_manager.session.query(Ticker)

total_urls_skipped = 0
total_urls = 0


def getClosingPrices(ticker, earnings_date, weekly_expiration_date):
	earnings_date_closing_price = 0.0
	weekly_expiration_date_closing_price = 0.0

	# Lengthen the start and end arrow dates
	start_date = earnings_date.replace(weeks=-1)
	end_date = weekly_expiration_date.replace(weeks=+2)
	# base_url = "http://finance.yahoo.com/q/hp?s="
	base_url = "http://real-chart.finance.yahoo.com/table.csv?s="
	
	# Get the start date paramaters
	sm = str(int(start_date.format('MM'))-1)
	sd = start_date.format('D')
	sy = start_date.format('YYYY')

	# Get the end date parameters
	em = str(int(end_date.format('MM'))-1)
	ed = end_date.format('D')
	ey = end_date.format('YYYY')

	url = base_url + ticker \
	+ "&a=" + sm + "&b=" + sd + "&c=" + sy \
	+ "&d=" + em + "&e=" + ed + "&f=" + ey + "&g=d&ignore=.csv"

	# Download the csv with these parameters
	# print "URL:\t" + url
	result = list(csv.reader(StringIO.StringIO(requests.get(url).text)))
	result = result[1:]

	for row in result:
		# If it is the correct date for the earings report day
		if row[0] == earnings_date.format("YYYY-MM-DD"):
			# Then record the adjusted closing price
			earnings_date_closing_price = row[6]
	
	for row in result:
		# If it is the correct date for the earings report day
		if row[0] == weekly_expiration_date.format("YYYY-MM-DD"):
			# Then record the adjusted closing price
			weekly_expiration_date_closing_price = row[6]
	
	if 	earnings_date_closing_price == 0.0 or weekly_expiration_date_closing_price == 0.0:
		summary = "Missing date for ticker: " + ticker + "\tearnings date: " + earnings_date.format("YYYY-MM-DD") + \
		"\tweeklies expiration date: " + weekly_expiration_date.format("YYYY-MM-DD") + \
		"\turl: " + url + "\n"
		logging.warn(summary)
	
	return earnings_date_closing_price, weekly_expiration_date_closing_price

def datesForTicker(result_set, collection):
	global total_urls_skipped
	global total_urls
	ticker_urls_skipped = 0
	earning_days_and_weeklies_with_closing_prices = []
	
	for each in result_set.earnings_dates:
		total_urls = total_urls + 1
		try:
			each = arrow.get(each.date, "M/D/YY")
		except Exception, e:
			summary = "Couldn't parse date '" + each.date + "' for ticker " + result_set.name + ". Url Skipped."
			logging.warn(summary)
			continue
		
		
		# Find the next Friday for the earnings date
		each_friday = each
		
		while each_friday.weekday() != 4:
			each_friday = each_friday.replace(days=+1)	

		# If earnings was on a Thursday, get the weeklies for the following week
		# print "Checking if it is a Thursday..."
		if each.weekday() == 3:
			each_friday = each_friday.replace(weeks=+1)
		
		# print "\nDate of Earnings Report:\t" + each.format("dddd, MMMM D, YYYY")
		# print "Date of Weeklies Expiration:\t" + each_friday.format("dddd, MMMM D, YYYY")
		each_close, each_friday_close = getClosingPrices(result_set.name, each, each_friday)
		# Save those 2 dates into an array if the closing prices were found		
		if each_close != 0.0 and each_friday_close != 0.0:
			earning_days_and_weeklies_with_closing_prices.append({
				"date" : each.format("YYYY-MM-DD"),
				"date_closing_price" : each_close,
				"upcoming_weekly_expiration" : each_friday.format("YYYY-MM-DD"),
				"weekly_expiration_closing_price" : each_friday_close
				})
		else:
			ticker_urls_skipped = ticker_urls_skipped + 1

	# Insert the completed list as a single document into db
	document = {'ticker_name' : result_set.name,
							'list_of_earnings_dates' : earning_days_and_weeklies_with_closing_prices}
	
	collection.insert_one(document)
	
	total_urls_skipped = total_urls_skipped + ticker_urls_skipped

	if ticker_urls_skipped != 0:
		print "# of Urls skipped so far:\t" + str(total_urls_skipped)
	print "Success rate:\t" + str(100-(total_urls_skipped*100/total_urls)) + "%"


	
def start():
	client  = pymongo.MongoClient()

	db = client['ears']

	collection = db['ticker_info_test']

	logging.basicConfig(filename = 'monitor.log',
							filemode = 'w',
							datefmt ='%m/%d/%Y %I:%M:%S %p',
							format ='%(asctime)s \t\t%(message)s',
							level = logging.WARN)	

	for each in results:
		print "\nParsing closing dates for:\t" + each.name
		datesForTicker(each, collection)

start()
	# {"ticker_name" : "ABCD",
	# 	"parent_earnings_dates" : [
	# 		{ 
	# 		"date" : "1-1-14",
	# 		"oneearlier" : {
	# 			"date" : "1-1-13",
	# 			"date_close" : "100.00",
	# 			"next_weekly_expiration" : "this friday",
	# 			"next_weekly_expiration_close" : "110.00",
	# 			"moving_average" : "next_weekly_expiration_close / date_close"
	# 		},
	# 		"twoearlier" : {
	# 			"date" : "1-1-12",
	# 			"date_close" : "100.00",
	# 			"next_weekly_expiration" : "this friday",
	# 			"next_weekly_expiration_close" : "110.00",
	# 			"moving_average" : "next_weekly_expiration_close / date_close"
	# 		},
	# 		"threeearlier" : {
	# 			"date" : "1-1-11",
	# 			"date_close" : "100.00",
	# 			"next_weekly_expiration" : "this friday",
	# 			"next_weekly_expiration_close" : "110.00",
	# 			"moving_average" : "next_weekly_expiration_close / date_close"
	# 		},
	# 		"average_move" : "calculate average of the 3 moving averages",
	# 		"high_move" : "the highest of the 3 moving averages"

				
	# 	}

	# 	]

	# }