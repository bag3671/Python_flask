from flask import Blueprint, render_template, request, session, g,current_app
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import joblib
from fbprophet import Prophet
from datetime import datetime, timedelta
import pandas_datareader as pdr
import pandas as pd
from my_util.gangert_weather import *
from my_util.module import pca_accuracy,draw_compare
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os

rgrs_bp = Blueprint('rgrs_bp', __name__)

def get_weather_main():
    weather = None
    try:
        weather = session['weather']
    except:
        current_app.logger.info("get new weather info")
        weather = get_gangseo_weather()
        session['weather'] = weather
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=60)
    return weather
menu = {'ho':0, 'da':0, 'ml':10, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 're':1, 'cu':0}

@rgrs_bp.route('/iris', methods=['GET', 'POST'])
def iris():
    if request.method == 'GET':
        return render_template('iris.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        feature_name = request.form['feature']
        column_dict = {'sl':'Sepal length', 'sw':'Sepal width', 
                       'pl':'Petal length', 'pw':'Petal width', 
                       'species':['Setosa', 'Versicolor', 'Virginica']}
        column_list = list(column_dict.keys())

        df = pd.read_csv('static/data/iris_train.csv')
        df.columns = column_list
        X = df.drop(columns=feature_name, axis=1).values
        y = df[feature_name].values

        lr = LinearRegression()
        lr.fit(X, y)
        weight, bias = lr.coef_, lr.intercept_

        df_test = pd.read_csv('static/data/iris_test.csv')
        df_test.columns = column_list
        X_test = df_test.drop(columns=feature_name, axis=1).values[index]
        pred_value = np.dot(X_test, weight.T) + bias

        x_test = list(df_test.iloc[index,:-1].values)
        x_test.append(column_dict['species'][int(df_test.iloc[index,-1])])
        org = dict(zip(column_list, x_test))
        pred = dict(zip(column_list[:-1], [0,0,0,0]))
        pred[feature_name] = np.round(pred_value, 2)
        return render_template('iris_res.html', menu=menu, weather=get_weather_main(),
                                index=index, org=org, pred=pred, feature=column_dict[feature_name])

kospi_dict, kosdaq_dict, nyse_dict, nasdaq_dict = {}, {}, {}, {}
# @rgrs_bp.before_app_first_request
# def before_app_first_request():
#     kospi = pd.read_csv('./static/data/KOSPI.csv', dtype={'종목코드': str})
#     for i in kospi.index:
#         kospi_dict[kospi['종목코드'][i]] = kospi['기업명'][i]
#     kosdaq = pd.read_csv('./static/data/KOSDAQ.csv', dtype={'종목코드': str})
#     for i in kosdaq.index:
#         kosdaq_dict[kosdaq['종목코드'][i]] = kosdaq['기업명'][i]
#     nyse = pd.read_excel('./static/data/NYSE.xlsx', dtype={'Ticker': str}, engine='openpyxl')
#     for i in nyse.index:
#         nyse_dict[nyse['Ticker'][i]] = nyse['Company'][i]
#     nasdaq = pd.read_excel('./static/data/NASDAQ.xlsx', dtype={'Ticker': str}, engine='openpyxl')
#     for i in nasdaq.index:
#         nasdaq_dict[nasdaq['Ticker'][i]] = nasdaq['Company'][i]

# @rgrs_bp.route('/stock', methods=['GET', 'POST'])
# def stock():
#     if request.method == 'GET':
#         return render_template('stock.html', menu=menu, weather=get_weather_main(),
#                                 kospi=kospi_dict, kosdaq=kosdaq_dict, 
#                                 nyse=nyse_dict, nasdaq=nasdaq_dict)
#     else:
#         market = request.form['market']
#         if market == 'KS':
#             code = request.form['kospi_code']
#             company = kospi_dict[code]
#             code += '.KS'
#         elif market == 'KQ':
#             code = request.form['kosdaq_code']
#             company = kosdaq_dict[code]
#             code += '.KQ'
#         elif market == 'NY':
#             code = request.form['nyse_code']
#             company = nyse_dict[code]
#         else:
#             code = request.form['nasdaq_code']
#             company = nasdaq_dict[code]
#         learn_period = int(request.form['learn'])
#         pred_period = int(request.form['pred'])
#         current_app.logger.debug(f'{market}, {code}, {learn_period}, {pred_period}')

#         today = datetime.now()
#         start_learn = today - timedelta(days=learn_period*365)
#         end_learn = today - timedelta(days=1)

#         stock_data = pdr.DataReader(code, data_source='yahoo', start=start_learn, end=end_learn)
#         current_app.logger.info(f"get stock data: {company}({code})")
#         df = pd.DataFrame({'ds': stock_data.index, 'y': stock_data.Close})
#         df.reset_index(inplace=True)
#         try:
#             del df['Date']
#         except:
#             current_app.logger.error('Date error')

#         model = Prophet(daily_seasonality=True)
#         model.fit(df)
#         future = model.make_future_dataframe(periods=pred_period)
#         forecast = model.predict(future)

#         fig = model.plot(forecast);
#         img_file = os.path.join(current_app.root_path, 'static/img/stock.png')
#         fig.savefig(img_file)
#         mtime = int(os.stat(img_file).st_mtime)

#         return render_template('stock_res.html', menu=menu, weather=get_weather_main(), 
#                                 mtime=mtime, company=company, code=code)

@rgrs_bp.route('/diabetes', methods=['GET', 'POST'])
def diabetes():
    if request.method == 'GET':
        return render_template('diabetes.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        feature = request.form['feature']
        df = pd.read_csv('static/data/diabetes_train.csv')
        X = df[feature].values.reshape(-1,1)
        y = df.target.values

        lr = LinearRegression()
        lr.fit(X, y)
        weight, bias = lr.coef_, lr.intercept_

        df_test = pd.read_csv('static/data/diabetes_test.csv')
        X_test = df_test[feature][index]
        y_test = df_test.target[index]
        pred = np.round(X_test * weight[0] + bias, 2)

        y_min = np.min(X) * weight[0] + bias
        y_max = np.max(X) * weight[0] + bias
        plt.figure()
        plt.scatter(X, y, label='train')
        plt.plot([np.min(X), np.max(X)], [y_min, y_max], 'r', lw=3)
        plt.scatter([X_test], [y_test], c='r', marker='*', s=100, label='test')
        plt.grid()
        plt.legend()
        plt.title(f'Diabetes target vs. {feature}')
        img_file = os.path.join(current_app.root_path, 'static/img/diabetes.png')
        plt.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        result_dict = {'index':index, 'feature':feature, 'y':y_test, 'pred':pred}
        return render_template('diabetes_res.html', res=result_dict, mtime=mtime,
                                menu=menu, weather=get_weather_main())

@rgrs_bp.route('/boston', methods=['GET', 'POST'])
def boston():
    if request.method == 'GET':
        feature_list = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 
                        'TAX', 'PTRATIO', 'B', 'LSTAT']
        return render_template('boston.html', feature_list=feature_list,
                               menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        feature_list = request.form.getlist('feature')
        df = pd.read_csv('static/data/boston_train.csv')
        X = df[feature_list].values
        y = df.target.values

        lr = LinearRegression()
        lr.fit(X, y)
        weight, bias = lr.coef_, lr.intercept_

        df_test = pd.read_csv('static/data/boston_test.csv')
        X_test = df_test[feature_list].values[index, :]
        y_test = df_test.target[index]
        pred = np.dot(X_test, weight.T) + bias      
        pred = np.round(pred, 2)                    

        result_dict = {'index':index, 'feature':feature_list, 'y':y_test, 'pred':pred}
        org = dict(zip(df.columns[:-1], df_test.iloc[index, :-1]))
        return render_template('boston_res.html', res=result_dict, org=org,
                               menu=menu, weather=get_weather_main())
