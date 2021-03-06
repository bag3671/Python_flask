from flask import Blueprint, render_template, request, session, g,current_app
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.datasets import load_digits
import matplotlib.pyplot as plt
import joblib
import pandas as pd
import os
from my_util.gangert_weather import *

classify_bp = Blueprint('classify_bp', __name__)

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
            'cf':1, 'ac':0, 're':0, 'cu':0}

@classify_bp.route('/cancer', methods=['GET', 'POST'])
def cancer():
    
    if request.method == 'GET':
        return render_template('cancer.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        df = pd.read_csv('static/data/cancer_test.csv')
        scaler = MinMaxScaler()
        scaled_test = scaler.fit_transform(df.iloc[:, :-1])
        test_data = scaled_test[index, :].reshape(1,-1)
        label = df.iloc[index, -1]
        lrc = joblib.load('static/model/cancer_lr.pkl')
        svc = joblib.load('static/model/cancer_sv.pkl')
        rfc = joblib.load('static/model/cancer_rf.pkl')
        pred_lr = lrc.predict(test_data)
        pred_sv = svc.predict(test_data)
        pred_rf = rfc.predict(test_data)
        result = {'index':index, 'label':label,
                  'pred_lr':pred_lr[0], 'pred_sv':pred_sv[0], 'pred_rf':pred_rf[0]}
        org = dict(zip(df.columns[:-1], df.iloc[index, :-1]))
        return render_template('cancer_res.html', menu=menu, 
                                res=result, org=org, weather=get_weather_main())
                            
@classify_bp.route('/titanic', methods=['GET', 'POST'])
def titanic():
    
    if request.method == 'GET':
        return render_template('titanic_cls.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        df = pd.read_csv('static/data/titanic_test.csv')
        scaler = joblib.load('static/model/titanic_scaler.pkl')
        test_data = df.iloc[index, :-1].values.reshape(1,-1)
        test_scaled = scaler.transform(test_data)
        label = df.iloc[index, 0]
        lrc = joblib.load('static/model/titanic_lr.pkl')
        svc = joblib.load('static/model/titanic_sv.pkl')
        rfc = joblib.load('static/model/titanic_rf.pkl')
        pred_lr = lrc.predict(test_scaled)
        pred_sv = svc.predict(test_scaled)
        pred_rf = rfc.predict(test_scaled)
        result = {'index':index, 'label':label,
                  'pred_lr':pred_lr[0], 'pred_sv':pred_sv[0], 'pred_rf':pred_rf[0]}

        tmp = df.iloc[index, 1:].values
        value_list = []
        int_index_list = [0, 1, 3, 4, 6, 7]
        for i in range(8):
            if i in int_index_list:
                value_list.append(int(tmp[i]))
            else:
                value_list.append(tmp[i])
        org = dict(zip(df.columns[1:], value_list))
        return render_template('titanic_cls_res.html', menu=menu, 
                                res=result, org=org, weather=get_weather_main())

@classify_bp.route('/pima', methods=['GET', 'POST'])
def pima():
    
    if request.method == 'GET':
        return render_template('pima_cls.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        df = pd.read_csv('static/data/pima_test.csv')
        scaler = joblib.load('static/model/pima_scaler.pkl')
        test_data = df.iloc[index, :-1].values.reshape(1,-1)
        test_scaled = scaler.transform(test_data)
        label = df.iloc[index, -1]
        lrc = joblib.load('static/model/pima_lr.pkl')
        svc = joblib.load('static/model/pima_sv.pkl')
        rfc = joblib.load('static/model/pima_rf.pkl')
        pred_lr = lrc.predict(test_scaled)
        pred_sv = svc.predict(test_scaled)
        pred_rf = rfc.predict(test_scaled)
        result = {'index':index, 'label':label,
                  'pred_lr':pred_lr[0], 'pred_sv':pred_sv[0], 'pred_rf':pred_rf[0]}
        org = dict(zip(df.columns[:-1], df.iloc[index, :-1]))
        return render_template('pima_cls_res.html', menu=menu, 
                                res=result, org=org, weather=get_weather_main())

@classify_bp.route('/iris', methods=['GET', 'POST'])
def iris():
    
    if request.method == 'GET':
        return render_template('iris_cls.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        df = pd.read_csv('static/data/iris_test.csv')
        scaler = joblib.load('static/model/iris_scaler.pkl')
        test_data = df.iloc[index, :-1].values.reshape(1,-1)
        test_scaled = scaler.transform(test_data)
        label = df.iloc[index, -1]
        lrc = joblib.load('static/model/iris_lr.pkl')
        svc = joblib.load('static/model/iris_sv.pkl')
        rfc = joblib.load('static/model/iris_rf.pkl')
        pred_lr = lrc.predict(test_scaled)
        pred_sv = svc.predict(test_scaled)
        pred_rf = rfc.predict(test_scaled)

        species = ['Setosa', 'Versicolor', 'Virginica']
        result = {'index':index, 'label':f'{label} ({species[label]})',
                  'pred_lr':f'{pred_lr[0]} ({species[pred_lr[0]]})', 
                  'pred_sv':f'{pred_sv[0]} ({species[pred_sv[0]]})', 
                  'pred_rf':f'{pred_rf[0]} ({species[pred_rf[0]]})'}
        org = dict(zip(df.columns[:-1], df.iloc[index, :-1]))
        return render_template('iris_cls_res.html', menu=menu, 
                                res=result, org=org, weather=get_weather_main())

@classify_bp.route('/wine', methods=['GET', 'POST'])
def wine():
    
    if request.method == 'GET':
        return render_template('wine_cls.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        df = pd.read_csv('static/data/wine_test.csv')
        scaler = joblib.load('static/model/wine_scaler.pkl')
        test_data = df.iloc[index, :-1].values.reshape(1,-1)
        test_scaled = scaler.transform(test_data)
        label = df.iloc[index, -1]
        lrc = joblib.load('static/model/wine_lr.pkl')
        svc = joblib.load('static/model/wine_sv.pkl')
        rfc = joblib.load('static/model/wine_rf.pkl')
        pred_lr = lrc.predict(test_scaled)
        pred_sv = svc.predict(test_scaled)
        pred_rf = rfc.predict(test_scaled)
        result = {'index':index, 'label':label,
                  'pred_lr':pred_lr[0], 'pred_sv':pred_sv[0], 'pred_rf':pred_rf[0]}
        org = dict(zip(df.columns[:-1], df.iloc[index, :-1]))
        return render_template('wine_cls_res.html', menu=menu, 
                                res=result, org=org, weather=get_weather_main())