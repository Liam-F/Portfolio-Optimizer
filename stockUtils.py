import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo

'''
Global Variables
	noa: number of assets in portfolio
	dailyReturns: dataframe containing the log of the daily returns for each asset
'''

#Defining Constants
TRADING_DAYS_PER_YEAR = 252
MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52
HOURS_PER_DAY = 24.0
MINUTES_PER_DAY = 24.0 * 60.0
SECONDS_PER_DAY = MINUTES_PER_DAY * 60.0

'''
Use Yahoo Finance API to retreive CSV file for daily stock data 
Returns daily Adj Close values to pandas DataFrame
'''
def get_data(symbols, dates):
	global noa
	noa = len(symbols)

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
	global dailyReturns
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
Plots results of various random portfolio weights (monte carlo simulation), the optomized portfolios, the efficent frontier 

'''
def plot_data(numberOfSims, targetRets, targetVolits, resultSharpe, resultVar):
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
	#Colour the data points based on their sharpe ratio (simplified for risk free rate of return = 0)
	plt.figure(figsize=(8, 4))

	#Random Portfolios from the simulation
	plt.scatter(expectedPortVolit, expectedPortRet, c = expectedPortRet / expectedPortVolit, marker='o')
	#The Efficent Frontier
	plt.scatter(targetVolits, targetRets, c = targetRets / targetVolits, marker = 'x')
	#Min Variance Portfolio shown as yellow star
	plt.plot(statistics(resultVar['x'])[1], statistics(resultVar['x'])[0], 'y*', markersize = 20.0)
	#Max Sharpe Ratio to meet target return with lowest volitality shown as red star
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
[1] = weights for portfolio with lowest variance for the desired target return value 

'''
def optimize_portfolio(numberOfSims, target):
	#Fix a target return for the portfolio and we find the min volitality
	targetRets = np.linspace(0.0,target,50)
	targetVolits = []

	#Defining bounds for optimization
	#Bounds to be [0,1] for any given weight 
	bounds = tuple((0, 1) for x in range(noa))

	#Use evenly distributed weights as the inital starting point 
	initWeights = noa * [1.0 / noa]

	#Optimize Portfolio weights for the LOWEST variance (risk)
	constraints = ({'type': 'eq', 'fun': lambda x: (np.sum(x) - 1)})
	resultVar = spo.minimize(min_func_variance, initWeights, method = 'SLSQP', bounds = bounds, constraints = constraints)

	#Building Efficent Frontier
	for targetRet in targetRets:

		#Defining optimization constraints as a dictionary 
		#constraints to be that the sum of weights must equal 1 and that the expectedReturn of the portfolio meets the target
		cons = ({'type': 'eq', 'fun': lambda x: (np.sum(x) - 1)},
				   	   {'type': 'eq', 'fun': lambda x: statistics(x)[0] - targetRet})

		resultSharpe = spo.minimize(min_func_variance, initWeights, method = 'SLSQP', bounds = bounds, constraints = cons)

		#Creating points for efficent frontier
		targetVolits.append(resultSharpe['fun'])

	#resultSharpe now holds the result of weights for the portfolio that has the highest sharpe ratio FOR the specified target
	targetVolits = np.array(targetVolits)

	plot_data(numberOfSims, targetRets, targetVolits, resultSharpe, resultVar)
	return resultVar['x'].round(4), resultSharpe['x'].round(4)

'''
The first function we want to minimize is the negative of the sharpe ratio. We want to find the max sharpe ratio 
The second is the volatility of the portfolio
'''
def min_func_sharpe(weights): 
	return -(statistics(weights)[2])
def min_func_variance(weights):
	return (statistics(weights)[1])