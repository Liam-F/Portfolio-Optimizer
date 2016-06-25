import sys
import pandas as pd
import numpy as np
import stockUtils



if (__name__ == "__main__"):

	#portfolio ticker input
	rawInput = raw_input("Enter all the stocks in your portfolio seperated by commas: ")
	symbols = rawInput.split(',')

	#Obtain data from these dates
	startDate = raw_input("Enter start date (YYYY-MM-DD): ") 
	endDate = raw_input("Enter end date (YYYY-MM-DD): ") 
	dates = pd.date_range(startDate, endDate)

	#Obtain target portfolio return from the user
	target = float(raw_input("Enter the target return as a decimal percentage value: "))

	adjClose = stockUtils.get_data(symbols, dates)
	dailyReturns = stockUtils.get_daily_returns(adjClose)

	#target is the targeted return value (as a decimal percentage) that you want to find the min risk portfolio for
	#lower target usually results in more evenly distributed weights
	result = stockUtils.optimize_portfolio(numberOfSims = 5000, target = target)

	#Output Results
	print
	print ('Minimum Variance Portfolio (Yellow Star){0}'.format(result[0]))
	print ('Expected Returns: {0} \nExpected Volatility: {1} \nSharpe Ratio: {2}'.format(stockUtils.statistics(result[0])[0], stockUtils.statistics(result[0])[1], stockUtils.statistics(result[0])[2]))

	print 
	print ('\nTarget Return Portfolio (Red Star){0}'.format(result[1]))
	print ('Expected Returns: {0} \nExpected Volatility: {1} \nSharpe Ratio: {2}'.format(stockUtils.statistics(result[1])[0], stockUtils.statistics(result[1])[1], stockUtils.statistics(result[1])[2]))
