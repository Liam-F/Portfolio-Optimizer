import sys
import datetime
import pandas as pd
import numpy as np
import StockUtils

if (__name__ == "__main__"):

	symbols = []
	end_date = datetime.date.today()
	start_date = end_date.replace(year=end_date.year - 1)

	#Have to have min. 3 stocks and no duplicates
	while ((len(symbols) < 3) or len(symbols) != len(set(symbols))):
		print("\nYou must enter at least three unique stocks")
		symbols = raw_input("Enter all the stocks in your portfolio separated by commas: ")
		symbols = symbols.split(',')

	#Obtain data from these dates
	dates = pd.date_range(start_date, end_date)

	try:
		adj_close = StockUtils.get_data(symbols, dates)
		daily_returns = StockUtils.get_daily_returns(adj_close)
		StockUtils.init_portfolio(len(symbols), daily_returns)
		result = StockUtils.optimize_portfolio(number_of_sims = 2000)
	except Exception:
		print("\n\nSorry, it seems something went wrong. \nA symbol may have been entered incorrectly or an invalid date range was selected. \nPlease try again.")
		sys.exit()


	#Output Results
	print
	print ('Minimum Variance Portfolio (Yellow Star){0}'.format(result[0]))
	print ('Expected Returns: {0} \nExpected Volatility: {1} \nSharpe Ratio: {2}'
			.format(StockUtils.statistics(result[0])[0], 
					StockUtils.statistics(result[0])[1], 
					StockUtils.statistics(result[0])[2]))

	print 
	print ('\nMaximum Sharpe Ratio Portfolio (Red Star){0}'.format(result[1]))
	print ('Expected Returns: {0} \nExpected Volatility: {1} \nSharpe Ratio: {2}'
			.format(StockUtils.statistics(result[1])[0], 
					StockUtils.statistics(result[1])[1], 
					StockUtils.statistics(result[1])[2]))
