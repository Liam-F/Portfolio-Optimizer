import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo

#Defining Constants
TRADING_DAYS_PER_YEAR = 252
MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52
HOURS_PER_DAY = 24.0
MINUTES_PER_DAY = 24.0 * 60.0
SECONDS_PER_DAY = MINUTES_PER_DAY * 60.0

'''
Global Variables
	noa: number of assets in portfolio
	dailyReturns: dataframe containing the log of the daily returns for each asset
'''
def init_Portfolio(numberOfAssets, dfDailyReturns):
	global noa
	global dailyReturns
	noa = numberOfAssets
	dailyReturns = dfDailyReturns

'''
Use Yahoo Finance API to retrieve CSV file for daily stock data 
Returns daily Adj Close values to pandas DataFrame
'''
def get_data(symbols, dates):
	df = pd.DataFrame(index = dates)

	for symbol in symbols:
		df_temp = pd.read_csv("http://real-chart.finance.yahoo.com/table.csv?s=" + symbol,
								index_col = 'Date', 
								parse_dates = True, 
								usecols = ['Date', 'Adj Close'], 
								na_values = ['nan'])

		df_temp = df_temp.sort_index()
		df_temp = df_temp.rename(columns={'Adj Close': symbol})

		df = df.join(df_temp, how = 'inner')
	return df

'''
Given DataFrame of daily Adj Close values calculate and 
Return daily returns 
'''
def get_daily_returns(df):
	dailyReturns = np.log(df / df.shift(1))
	#with daily returns since the first row will be zero we just discard it
	dailyReturns = dailyReturns[1:]
	return dailyReturns

'''
Given a weight allocations for a portfolio return:
	[0]Expected Returns
	[1]Expected Volatility
	[2]Sharpe Ratio of the Portfolio
'''
def statistics(weights):
	weights = np.array(weights)
	#Simplified Sharpe ratio assuming that the risk free rate is zero 
	expectedPortRet = np.sum(dailyReturns.mean() * weights) * TRADING_DAYS_PER_YEAR
	expectedPortVolit = np.sqrt(np.dot(weights.T, np.dot(dailyReturns.cov() * TRADING_DAYS_PER_YEAR, weights)))
	sharpeRatio = expectedPortRet / expectedPortVolit
	return np.array([expectedPortRet,expectedPortVolit,sharpeRatio])

'''
Plots results of various random portfolio weights (Monte Carlo simulation), the optimized portfolios, the efficient frontier 

'''
def plot_data(numberOfSims, targetRets, targetVolits, resultVar, resultSharpe):
	expectedPortRet = []
	expectedPortVolit = []

	#Monte Carlo Simulation on various portfolio weights
	for i in range (numberOfSims):
		#Generate random portfolio weights that sum to 1
		weights = np.random.random(noa)
		weights = weights / np.sum(weights)

		#Expected Portfolio Return
		#In the sense that historical mean performance is assumed to be the best estimator for future (expected) performance.
		#Data multiplied by 252 so that it is annualized
		expectedPortRet.append(statistics(weights)[0])

		#Expected Portfolio Volatility which = sqrt(Variance)
		expectedPortVolit.append(statistics(weights)[1])

	#Converting to numpy arrays 
	expectedPortRet = np.array(expectedPortRet)
	expectedPortVolit = np.array(expectedPortVolit)

	#Plot results of the simulation and optimization
	#Colour the data points based on their Sharpe ratio (simplified for risk free rate of return = 0)
	plt.figure(figsize=(8, 4))

	#Random Portfolios from the simulation
	plt.scatter(expectedPortVolit, expectedPortRet, c = expectedPortRet / expectedPortVolit, marker='o')
	#The Efficient Frontier
	plt.scatter(targetVolits, targetRets, c = targetRets / targetVolits, marker = 'x')
	#Min Variance Portfolio shown as yellow star
	plt.plot(statistics(resultVar['x'])[1], statistics(resultVar['x'])[0], 'y*', markersize = 20.0)
	#Max Sharpe Ratio to meet target return with lowest volatility shown as red star
	plt.plot(statistics(resultSharpe['x'])[1], statistics(resultSharpe['x'])[0], 'r*', markersize = 20.0)

	plt.grid(True)
	plt.xlabel('Expected Volatility')
	plt.ylabel('Expected Return')
	plt.colorbar(label='Sharpe Ratio')
	plt.show()

'''
Optimize portfolio weights by phrasing the task as a minimization problem

Returns optimized portfolio weights
[0] = weights for portfolio with minimum variance
[1] = weights for portfolio with maximum Sharpe ratio

'''
def optimize_portfolio(numberOfSims):
	#Defining bounds for optimization
	#Bounds to be [0,1] for any given weight 
	bounds = tuple((0, 1) for x in range(noa))
	constraints = ({'type': 'eq', 'fun': lambda x: (np.sum(x) - 1)})

	#Use evenly distributed weights as the initial starting point 
	initWeights = noa * [1.0 / noa]
	
	#optimize portfolios
	optSharpe = spo.minimize(min_func_sharpe, initWeights, method = 'SLSQP', bounds = bounds, constraints = constraints)
	optVariance = spo.minimize(min_func_variance, initWeights, method = 'SLSQP', bounds = bounds, constraints = constraints)

	#Building Efficient Frontier
	targetRets = np.linspace(0.0,(statistics(optSharpe['x'])[0]),50)
	targetVolits = []
	for targetRet in targetRets:

		#Defining optimization constraints as a dictionary 
		#constraints to be that the sum of weights must equal 1 and that the expectedReturn of the portfolio meets the target
		cons = ({'type': 'eq', 'fun': lambda x: (np.sum(x) - 1)},
				   	   {'type': 'eq', 'fun': lambda x: statistics(x)[0] - targetRet})

		res = spo.minimize(min_func_variance, initWeights, method = 'SLSQP', bounds = bounds, constraints = cons)

		#Creating points for efficient frontier
		targetVolits.append(res['fun'])

	#resultSharpe now holds the result of weights for the portfolio that has the highest Sharpe ratio FOR the specified target
	targetVolits = np.array(targetVolits)

	plot_data(numberOfSims, targetRets, targetVolits, optVariance, optSharpe)
	return optVariance['x'].round(4), optSharpe['x'].round(4)

'''
The first function we want to minimize is the negative of the Sharpe ratio. We want to find the max Sharpe ratio 
The second is the volatility of the portfolio
'''
def min_func_sharpe(weights): 
	return -(statistics(weights)[2])
def min_func_variance(weights):
	return (statistics(weights)[1])