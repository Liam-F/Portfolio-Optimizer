# Portfolio-Optimizer
Statistical analysis tool that optimizes asset allocations of a stock portfolio to minimize volatility and maximize expected returns.
# Walkthrough
With Python 2.7 installed on your local environment run the program as such.

![alt tag](https://raw.githubusercontent.com/nav97/Portfolio-Optimizer/master/Screenshots/Capture1.PNG)

Once launched you will be prompted to enter information as per the format that follows in the example below. Start date and end date are used to specify the time frame for which the data is analyzed. For a realistic use case scenario the end date would be today's date so that the algorithm can determine the best asset allocation using all the data available at the time.

![alt tag](https://raw.githubusercontent.com/nav97/Portfolio-Optimizer/master/Screenshots/Capture2.PNG)

Once executed you will be presented a graph. Each dot is a randomly generated portfolio of different asset allocations. The yellow star represents the portfolio with the lowest associated risk and the red star represents the portfolio that meets the expected return specified as input. The crosses along the body of randomly generated portfolios represents the efficient frontier which is a concept in Modern Portfolio Theory (MPT) introduced by Harry Markowitz and others in 1952. More information on MPT can be found on the internet. The user will also be presented with the asset allocations of each portfolio as well as the expected returns, expected volatility, and Sharpe ratio of the respective portfolios.
![alt tag](https://raw.githubusercontent.com/nav97/Portfolio-Optimizer/master/Screenshots/Capture3.PNG)
![alt tag](https://raw.githubusercontent.com/nav97/Portfolio-Optimizer/master/Screenshots/Capture4.PNG)

#Libraries Required

SciPy - open-source software for mathematics, science, and engineering (pandas, matplotlib, NumPy)
