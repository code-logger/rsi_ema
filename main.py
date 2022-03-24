#importing libraries 
import talib 
import numpy as np
from binance.client import Client 
# custom libraries 
from config import API_KEY , API_SECRET, SYMBOL , TIME_FRAME, QUANTITY ,SHORT_RSI_TIMEFRAME, LONG_RSI_TIMEFRAME, EMA_TIMEFRAME
import math 
import time 

 # binance client 
client = Client(API_KEY, API_SECRET)


def get_quan(): # get price quantity 
    return client.get_symbol_ticker(symbol=SYMBOL)['price']


# custom function for rouding down value 

def round_down(coin, number):
    info = client.get_symbol_info('%sUSDT' % coin)
    step_size = [float(_['stepSize']) for _ in info['filters'] if _['filterType'] == 'LOT_SIZE'][0]
    step_size = '%.8f' % step_size
    step_size = step_size.rstrip('0')
    decimals = len(step_size.split('.')[1])
    return math.floor(number * 10 ** decimals) / 10 ** decimals

# writing to file 
def write_data(data):
    with open("data.txt",'a') as file:
        file.write(data)


def place_order(type_order): # placing order for both buy and sell 
    if(type_order == "BUY"):
        qnty = round(QUANTITY /get_quan() ,4) ; # rounding off quantity 
        order = client.create_order(symbol=SYMBOL, side=type_order,type="MARKET" , quantity=qnty)
        print(order) 
        dt = "BUY order at {}\n".format(order['fills'][0]['price'])
        print(dt)
        write_data(dt)
    else:
        data = client.get_all_orders(symbol=SYMBOL, limit=1) # get last order to know filled qnty 
        qnty = float(data[0]['executedQty'])
        order = client.create_order(symbol=SYMBOL, side=type_order, type="MARKET", quantity=qnty)
        print(order) 
        dt = "SELL order at {}\n".format(order['fills'][0]['price'])
        print(dt)
        write_data(dt) 


def get_data(): # getting historic klines data 
    return_data = []
    res = client.get_klines(symbol=SYMBOL,interval=TIME_FRAME,limit=200)
    for each in res:
        return_data.append(float(each[4])) #closing data is at  5 place 
    return np.array(return_data) 




def main(): # main entry function 
    print("Bot started....") 
    buy = True 
    sell = False # initially , we want to buy not sell 
    while True:  #the script should run all the time 
        dt = get_data() 
        rsi_short = talib.RSI(dt, SHORT_RSI_TIMEFRAME)
        rsi_long = talib.RSI(dt, LONG_RSI_TIMEFRAME)

        # calculating ema from rsi 
        ema_short = talib.EMA(rsi_short, EMA_TIMEFRAME)
        ema_long = talib.EMA(rsi_long, EMA_TIMEFRAME) 


        # conditions 
        if((ema_short[-1] > ema_long[-1] and ema_short[-2] < ema_long[-2] )and buy):
                place_order("BUY")
                buy = False; sell = True; #we have buyed , now we should sell 

        if((ema_long[-1] > ema_short[-1] and ema_long[-2] and ema_short[-2]) and sell):
            place_order("SELL")
            buy = True; sell = True; # sold now time for buying 
        time.sleep(2); #delay so rate limit is not hit 


if __name__ == "__main__":
    main() # running the main function 









