# Order book simulation development 

### Bachelor's project using python

## What is an order book?
An order book is an essential tool in the functioning of financial markets, especially in electronic markets. It represents an organized list of buy and sell orders for a specific asset, showing market depth and the price levels at which participants are willing to buy or sell.

For this project, we integrated key concepts to model real-market behavior such as: 
- Tick and Lot: Tick represents the smallest possible price movement for an asset. It plays a crucial role in determining price variations in the order book and Lot represents the minimum quantity or a multiple of an asset that can be traded. This affects how orders are placed and executed in the order book.

- Maker and Taker: the Maker is a market participant who provides liquidity by placing orders that are not immediately executed (limit orders), and the Taker, is a participant who removes liquidity by executing trades immediately against existing orders (market orders).

- Fixing system: Implementation of an efficient fixing mechanism to simulate the opening and closing fixings, as done in European markets. Fixing is a process used to determine the opening and closing prices of assets in financial markets.

## 1st part: Order management
We define the Order class, which allows participants to add or cancel orders. First, we initialize the necessary parameters to construct the order book, such as tick size and lot size. We then create two separate order books—one for buy orders and one for sell orders—to clearly distinguish between the two types of orders.

Each participant has three options:

- Add a buy order
- Add a sell order
- Cancel an existing order
To handle these actions, we define three main methods within this class. Additionally, we implement two functions with similar logic: one for adding a buy order and the other for adding a sell order. In each function, we store the participant’s input in a dictionary to facilitate data management.

Every submitted order must include the following information: Quantity, Price, Order type (buy or sell), Order reference and the Role: taker or maker
If the participant is a maker, they place an order in the book that will only be executed when a taker accepts it. If the participant is a taker, they will execute their order at the current market price.

We then define another function to execute an order when the participant is a taker, meaning they are willing to trade at the best available price. There is no need for a similar function for makers, as they set prices and wait for a counterparty to match their order.

The order book is sorted to highlight the most attractive orders for investors:

- The highest prices for buy orders
- The lowest prices for sell orders
For sell orders, we match with buy orders at an equal or higher price. Conversely, for buy orders, we match with sell orders at an equal or lower price. This ensures that buyers pay their intended price or less, while sellers receive their intended price or more.

We also remove fully executed buy or sell orders from the order book. If a taker cannot fully execute their order due to insufficient liquidity, the remaining quantity is added to the book as a maker order.

Additionally, we implement a method to display the order book. This method is not used in the main code but serves as a debugging tool to verify the functionality of our buy and sell order book.

A second method allows participants to cancel an existing order. Since we maintain separate books for buy and sell orders, it was more efficient to implement distinct methods for canceling buy and sell orders.

## 2nd part: Fixing Price Calculation
In this section, we implement a fixing method to determine the price of a financial asset at a given moment. The fixing price is defined as the price at which the maximum volume of orders can be executed. In other words, it is the price where the highest number of buyers and sellers agree to trade.

This method is commonly used before market opening and after market closing to establish a reference price for investors.

To calculate the fixing price:

1) We merge the buy and sell order books to consolidate all market participants' orders.
2) Orders are sorted by price to prioritize higher buy prices and lower sell prices, reflecting market dynamics where transactions are more frequent at these levels.
3) We initialize variables to track the maximum executable volume and the corresponding fixing price.
4) We iterate through each price level to compute the total executed volume and identify the optimal fixing price.

Then, for each price level,we calculate the total buy order quantity at that price or higher (total demand).We calculate also the total sell order quantity at that price or lower (total supply). The executed volume is the minimum of the total buy and sell volumes since transactions can only occur up to the available liquidity.
If a given price allows for a higher executed volume than the current maximum, we update the fixing price and volume.

At the end of the loop, we return the determined fixing price along with the corresponding maximum volume.

## 3rd part: Example implementation to test the class
We initialize an Ordre object with a tick size of 0.01 (the minimum price increment) and a lot size of 1 (the minimum tradeable unit). This instance will manage buy and sell orders in a structured order book.

We then add sell orders (maker role):

- Trader Alain places a sell order at 100.5 for 100 units.
- Trader Bernard places a sell order at 101 for 5 units.
Both traders are makers, meaning their orders are added to the order book and will remain until a counterparty (a taker) matches them.

- Trader George places a sell order at 98.5 as a maker. This is below existing buy orders, so it remains in the order book until a buyer (taker) matches it.

Next, we add buy orders (maker and taker roles):

- Trader Emma places a buy order at 99.5 for 2 units as a taker. Since George is selling at 98.5, her order is immediately executed at 98.5, buying 2 units from George.
- Trader José places a buy order at 102 for 3 units as a taker. Since 102 is higher than the available sell orders (e.g. George if remaining, Alain at 100.5 and Bernard at 101), the order is immediately executed, buying from the lowest-priced sell orders first.
- Trader Claude places a buy order at 101.5 for 3 units as a taker. The order is matched with existing sell orders at 100.5, starting with Alain’s offer if there’s remaining quantity.
- Trader Claude submits another buy order at 101.5 for 7 units as a taker. Since 101.5 is higher than the current best sell price, this order immediately executes, consuming the lowest-priced sell orders (Alain then Bernard if necessary).

We also have:

Trader Clara wants to buy 20 units at 99.5. If there are still sellers at or below that price (e.g. George if not fully matched), her order is partially or fully matched. Any unfilled quantity is added as a maker order at 99.5.

Finally, we display the order book to observe the state after transactions. We cancel the order made by trader Alain and again display the updated order book. This helps us verify that the cancellation was successful.




