# alpaca-bot
Simple Bot Built for Alpaca

Uses pandas-ta as a foundation for technical indicators.
Designed to trade using a MACD indicator at a 1-minute interval. Live data is streamed directly from alpaca's API and analyzed by the bot before making trading decisions.

A simple trade logic has been implemented whereby the bot buys once the MACD crosses above the signal line and sell the entirety of the position once the MACD drops below. With some knowledge of pandas-ta and python, the bot can be easily altered to trade on other indicators, or based on longer time intervals.
