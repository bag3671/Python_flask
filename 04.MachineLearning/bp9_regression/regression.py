from flask import Blueprint, render_template, request, session, g,current_app
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import joblib
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

@rgrs_bp.route('/iris', methods=['GET', 'POST'])
def iris():
    menu = {'ho':0, 'da':0, 'ml':10, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 're':1, 'cu':0}
    if request.method == 'GET':
        return render_template('iris.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'])
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
