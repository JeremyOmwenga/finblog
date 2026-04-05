---
title: "Statistical Foundations for Financial Modelling"
tag: "Quant"
date: "Apr 4, 2026"
excerpt: "Before the models, the algorithms, and the trading strategies, there is a small set of statistical ideas that almost everything else is built on. This is where it starts."
---

Most financial modelling literature assumes you already speak the language. This piece does not. It starts at the foundation — the handful of statistical concepts that appear, in one form or another, in nearly every quantitative finance application — and shows where each one actually shows up in practice.

## Mean, Variance, and Why They Are Not Enough

The **mean** (average) of a return series tells you the central tendency of the distribution — what a typical outcome looks like. The **variance** measures how spread out returns are around that mean. Its square root, the **standard deviation**, is the most common measure of risk in finance.

If a stock returns 2%, -1%, 3%, -2%, 1% over five days, the mean daily return is 0.6% and the standard deviation is approximately 1.85%.

The problem: mean and variance fully describe a distribution only if that distribution is normal (bell-shaped). Financial returns are not normal. They have **fat tails** — extreme outcomes happen far more often than a normal distribution predicts. The 2008 financial crisis was, under normal distribution assumptions, a multi-sigma event that should occur once in the lifetime of the universe. It did not.

This is why practitioners also look at **skewness** (asymmetry — do large losses happen more than large gains?) and **kurtosis** (tail thickness — how extreme are the extremes?). A return series with negative skew and high kurtosis is riskier than its standard deviation alone suggests.

## Correlation and Covariance

**Covariance** measures how two variables move together. **Correlation** normalises this to a scale of -1 to +1, making it comparable across different assets.

A correlation of +1 means two assets move in perfect lockstep. -1 means they move in perfect opposition. 0 means no linear relationship.

In portfolio construction this matters enormously. Harry Markowitz's core insight — the foundation of Modern Portfolio Theory — is that combining assets with low or negative correlations reduces portfolio variance without proportionally reducing expected return. Diversification, in other words, is a free lunch, but only to the extent that correlations stay low.

The trap: **correlations are not stable**. During market stress, correlations between risky assets tend to spike toward 1 as investors sell everything simultaneously. The diversification you modelled under normal conditions disappears exactly when you need it most.

## Regression

**Linear regression** estimates the relationship between a dependent variable and one or more independent variables. In finance the most common application is the **Capital Asset Pricing Model (CAPM)**:

```
Return = α + β × Market Return + ε
```

**Beta (β)** measures how sensitive an asset is to market movements. A beta of 1.2 means the asset tends to move 1.2% for every 1% the market moves. **Alpha (α)** is the intercept — the return unexplained by market exposure, often interpreted as manager skill or mispricing. **ε** is the error term — the residual noise the model does not capture.

Running this regression against historical data gives you estimates for α and β. The **R²** statistic tells you how much of the asset's return variation is explained by the market — a high R² means the asset is heavily market-driven; a low R² means there is significant idiosyncratic risk.

Multi-factor models (Fama-French three-factor, Carhart four-factor) extend this by adding additional explanatory variables — size, value, momentum — to capture return patterns that market beta alone misses.

## Volatility and Its Behaviour

**Volatility** — the standard deviation of returns over a rolling window — is not constant. It clusters. High-volatility periods tend to follow high-volatility periods. This phenomenon, called **volatility clustering**, is one of the most robust empirical findings in financial data.

The practical implication: a volatility estimate from a calm period will badly underestimate risk during turbulent ones. This is why risk models that use fixed historical volatility windows tend to be slow to react to regime changes.

**GARCH models** (Generalised Autoregressive Conditional Heteroskedasticity — a name designed to discourage casual interest) address this by modelling volatility as a time-varying process that responds to recent returns. The output is a conditional volatility estimate that adapts as market conditions change. GARCH is standard in options pricing, Value at Risk estimation, and risk management systems.

## Probability Distributions in Practice

Different financial variables are modelled with different distributions depending on what properties they need to capture:

**Normal distribution** — used for log-returns over short horizons as an approximation, despite its known shortcomings. Simple and mathematically tractable.

**Log-normal distribution** — if log-returns are normally distributed, prices themselves follow a log-normal distribution. This is the assumption underlying Black-Scholes options pricing. It ensures prices cannot go negative.

**Student's t-distribution** — similar to normal but with fatter tails, controlled by a degrees-of-freedom parameter. More honest about extreme outcomes. Increasingly used in risk models as a replacement for normal.

**Pareto / power law distributions** — extreme value theory suggests the tails of financial return distributions follow a power law. Used in stress testing and tail risk estimation.

The choice of distribution is a modelling decision with significant consequences. Assuming normality when the true distribution has fat tails means systematically underpricing tail risk — which is precisely what happened across the structured credit market in 2007-08.

## The Trap of Overfitting

A model that fits historical data perfectly is almost certainly useless for prediction. **Overfitting** occurs when a model captures the noise in the training data rather than the underlying signal. It will backtest beautifully and fail immediately in live conditions.

The standard safeguard is **out-of-sample testing** — train the model on one portion of the data, test it on a portion it has never seen. If performance degrades substantially out of sample, the model has overfit.

In quantitative finance, where there is enormous incentive to find patterns and enormous amounts of historical data to mine, overfitting is endemic. A strategy that appears to generate alpha in backtesting is far more likely to be a statistical artefact than a genuine edge.

> The most dangerous number in finance is a backtest Sharpe ratio you cannot explain from first principles.

---

These are the foundations. Mean, variance, correlation, regression, volatility modelling, distributions, and the discipline to distrust results that look too good. Everything more sophisticated — factor models, derivatives pricing, machine learning in finance — is built on top of this layer. Get the layer wrong and everything above it is unreliable.

*Next: time series analysis and why financial data is not like other data.*
