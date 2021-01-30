import numpy as np
import pickle
import pandas as pd
from collections import Counter
from sklearn import svm , neighbors
from sklearn.model_selection import cross_validate , train_test_split
from sklearn.ensemble import VotingClassifier , RandomForestClassifier


def process_data_for_labels(ticker):
    hm_days = 7 #how many days in future are we monitoring price
    df = pd.read_csv('sp500_compiled_closes.csv' , index_col=0)
    print(df.head())
    tickers = df.columns.values.tolist()
    df.fillna(0 , inplace=True)

    for i in range(1 , hm_days + 1):
        df['{}_{}d'.format(ticker , i)] = (df[ticker].shift(-i) - df[ticker])/df[ticker]
    
    df.fillna(0 , inplace=True)
    print(df)
    return tickers , df    
def buy_sell_hold(*args):
    cols = [c for c in args]
    pos_thresh = 0.029 #Percent change to trigger buy or sell
    neg_thresh = 0.023
    for col in cols :
        if  col > pos_thresh:
            return 1
        elif col < -neg_thresh:
            return -1
    return 0
def extract_featureset(ticker):
    hm_days = 7
    tickers , df = process_data_for_labels(ticker)
    df['{}_target'.format(ticker)] = list(map(buy_sell_hold ,*[df['{}_{}d'.format(ticker, i)]for i in range(1, hm_days+1)] ))
    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data Spread : ' , Counter(str_vals))

    df.fillna(0 , inplace=True)
    df = df.replace([np.inf , -np.inf], np.nan)
    df.dropna(inplace=True)
    df_vals = df[[ticker for ticker in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf , -np.inf],0)
    df_vals.fillna( 0 ,inplace=True)

    X , y = df_vals.values , df['{}_target'.format(ticker)].values
    return X , y , df


def ml_computer(ticker):
    X , y , df = extract_featureset(ticker)
    print('X : ' , X)
    print('Y :' , y)
    X_train , X_test , y_train , y_test = train_test_split(X, y , test_size=0.25)

    #clf = neighbors.KNeighborsClassifier() 
    clf = VotingClassifier([('lsvc' , svm.LinearSVC()) 
                           ,('knn'  , neighbors.KNeighborsClassifier())
                           ,('rfor' , RandomForestClassifier())])
    clf.fit(X_train , y_train)
    confidence = clf.score(X_test , y_test)
    print('Accuracy is : {}'.format(confidence) )
    #print(clf.weights)
    predictions = clf.predict(X_test)

    print('Predicted Spread :' , Counter(predictions))

    return confidence,df

ml_computer('BAC')