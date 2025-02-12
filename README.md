# Order book simulation development 

### Bachelor's project using python

## What is an order book?
An order book is an essential tool in the functioning of financial markets, especially in electronic markets. It represents an organized list of buy and sell orders for a specific asset, showing market depth and the price levels at which participants are willing to buy or sell.

For this project, we integrated key concepts to model real-market behavior such as: 
- Tick and Lot: Tick represents the smallest possible price movement for an asset. It plays a crucial role in determining price variations in the order book and Lot represents the minimum quantity or a multiple of an asset that can be traded. This affects how orders are placed and executed in the order book.

- Maker and Taker: the Maker is a market participant who provides liquidity by placing orders that are not immediately executed (limit orders), and the Taker, is a participant who removes liquidity by executing trades immediately against existing orders (market orders).

- Fixing system: Implementation of an efficient fixing mechanism to simulate the opening and closing fixings, as done in European markets. Fixing is a process used to determine the opening and closing prices of assets in financial markets.

## Introduction
