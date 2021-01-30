import bs4 as bs
import pickle
import requests
import datetime as dt
import pandas_datareader.data as web
import pandas as pd 
import os
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import yfinance as yf


style.use('ggplot')

def save_sp500_ticks():
    response = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(response.text , 'lxml')
    table = soup.find('table' , {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.strip()
        tickers.append(ticker)
    tickers = [s.replace('\n', '') for s in tickers]
    with open("sp500tickers.pickle" , "wb") as f:
        pickle.dump(tickers , f)

    print(tickers)
    return tickers    

#save_sp500_ticks()


def get_ticker_data(reload_sp500 = False):
    if reload_sp500 :
        tickers = save_sp500_ticks()
    else:
        with open("sp500tickers.pickle", "rb") as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    start = dt.datetime(2000, 1 , 1)
    end   = dt.datetime(2020 , 12 , 31)    
    data = yf.download(tickers , start=start , end=end)
    data = data['Adj Close']
    data.to_csv('sp500_compiled_closes.csv')
    print(data)
    # for ticker in tickers:  
    #     ticker = ticker.replace('.', '-')          
    #     print(ticker)
    #     if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
    #         df = web.DataReader(ticker , 'yahoo' , start , end)
    #         df.to_csv('stock_dfs/{}.csv'.format(ticker))
    #     else:
    #         print("Already saved {}".format(ticker))

get_ticker_data(True)
def compile_data():
    main_df = pd.DataFrame()        
    for i,name in enumerate(os.listdir('stock_dfs')):
        df = pd.read_csv('stock_dfs/{}'.format(name))
        df.set_index('Date' , inplace=True)
        df.rename(columns={'Adj Close' : name.split('.')[0]} , inplace=True)
        df.drop(['Open', 'High' , 'Low' , 'Close' , 'Volume'] , 1  , inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df , how='outer')     

        if i % 10 == 0:
            print(i)
    print(main_df.head())        
    main_df.to_csv('sp500_compiled_closes.csv')            

def visualize_data():
    df = pd.read_csv('sp500_compiled_closes.csv')
    # df['AAPL'].plot()
    # plt.show()
    df_corr = df.corr()
    print(df_corr.head())

    data = df_corr.values ##Gives inner data
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    heatmap = ax.pcolor(data , cmap=plt.cm.RdYlGn) #Red is negative , yellow neutral , green positive 
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0])+0.5 , minor=False)
    ax.set_yticks(np.arange(data.shape[1])+0.5 , minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1 , 1)
    plt.tight_layout()
    plt.show()

#visualize_data()    