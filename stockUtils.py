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
	daily_returns: dataframe containing the log of the daily returns for each asset
'''
def init_portfolio(num_assets, df_daily_returns):
	global noa
	global daily_returns
	noa = num_assets
	daily_returns = df_daily_returns

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
	daily_returns = np.log(df / df.shift(1))
	#with daily returns since the first row will be zero we just discard it
	daily_returns = daily_returns[1:]
	return daily_returns

'''
Given a weight allocations for a portfolio return:
	[0]Expected Returns
	[1]Expected Volatility
	[2]Sharpe Ratio of the Portfolio
'''
def statistics(weights):
	weights = np.array(weights)
	#Simplified Sharpe ratio assuming that the risk free rate is zero 
	expected_portfolio_ret = np.sum(daily_returns.mean() * weights) * TRADING_DAYS_PER_YEAR
	expected_portfolio_volit = np.sqrt(np.dot(weights.T, np.dot(daily_returns.cov() * TRADING_DAYS_PER_YEAR, weights)))
	sharpe_ratio = expected_portfolio_ret / expected_portfolio_volit
	return np.array([expected_portfolio_ret,expected_portfolio_volit,sharpe_ratio])

'''
Plots results of various random portfolio weights (Monte Carlo simulation), the optimized portfolios, the efficient frontier 

'''
def plot_data(number_of_sims, target_rets, target_volits, result_var, result_sharpe):
	expected_portfolio_ret = []
	expected_portfolio_volit = []

	#Monte Carlo Simulation on various portfolio weights
	for i in range (number_of_sims):
		#Generate random portfolio weights that sum to 1
		weights = np.random.random(noa)
		weights = weights / np.sum(weights)

		#Expected Portfolio Return
		#In the sense that historical mean performance is assumed to be the best estimator for future (expected) performance.
		#Data multiplied by 252 so that it is annualized
		expected_portfolio_ret.append(statistics(weights)[0])

		#Expected Portfolio Volatility which = sqrt(Variance)
		expected_portfolio_volit.append(statistics(weights)[1])

	#Converting to numpy arrays 
	expected_portfolio_ret = np.array(expected_portfolio_ret)
	expected_portfolio_volit = np.array(expected_portfolio_volit)

	#Plot results of the simulation and optimization
	#Colour the data points based on their Sharpe ratio (simplified for risk free rate of return = 0)
	plt.figure(figsize=(8, 4))

	#Random Portfolios from the simulation
	plt.scatter(expected_portfolio_volit, expected_portfolio_ret, c = expected_portfolio_ret / expected_portfolio_volit, marker='o')
	#The Efficient Frontier
	plt.scatter(target_volits, target_rets, c = target_rets / target_volits, marker = 'x')
	#Min Variance Portfolio shown as yellow star
	plt.plot(statistics(result_var['x'])[1], statistics(result_var['x'])[0], 'y*', markersize = 20.0)
	#Max Sharpe Ratio to meet target return with lowest volatility shown as red star
	plt.plot(statistics(result_sharpe['x'])[1], statistics(result_sharpe['x'])[0], 'r*', markersize = 20.0)

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
def optimize_portfolio(number_of_sims):
	#Defining bounds for optimization
	#Bounds to be [0,1] for any given weight 
	bounds = tuple((0, 1) for x in range(noa))
	constraints = ({'type': 'eq', 'fun': lambda x: (np.sum(x) - 1)})

	#Use evenly distributed weights as the initial starting point 
	init_weights = noa * [1.0 / noa]
	
	#optimize portfolios
	opt_sharpe = spo.minimize(min_func_sharpe, init_weights, method = 'SLSQP', bounds = bounds, constraints = constraints)
	opt_variance = spo.minimize(min_func_variance, init_weights, method = 'SLSQP', bounds = bounds, constraints = constraints)

	#Building Efficient Frontier
	target_rets = np.linspace(0.0,(statistics(opt_sharpe['x'])[0]),50)
	target_volits = []
	for target_ret in target_rets:

		#Defining optimization constraints as a dictionary 
		#constraints to be that the sum of weights must equal 1 and that the expectedReturn of the portfolio meets the target
		cons = ({'type': 'eq', 'fun': lambda x: (np.sum(x) - 1)},
				   	   {'type': 'eq', 'fun': lambda x: statistics(x)[0] - target_ret})

		res = spo.minimize(min_func_variance, init_weights, method = 'SLSQP', bounds = bounds, constraints = cons)

		#Creating points for efficient frontier
		target_volits.append(res['fun'])

	#result_sharpe now holds the result of weights for the portfolio that has the highest Sharpe ratio FOR the specified target
	target_volits = np.array(target_volits)

	plot_data(number_of_sims, target_rets, target_volits, opt_variance, opt_sharpe)
	return opt_variance['x'].round(4), opt_sharpe['x'].round(4)

'''
The first function we want to minimize is the negative of the Sharpe ratio. We want to find the max Sharpe ratio 
The second is the volatility of the portfolio
'''
def min_func_sharpe(weights): 
	return -(statistics(weights)[2])
def min_func_variance(weights):
	return (statistics(weights)[1])