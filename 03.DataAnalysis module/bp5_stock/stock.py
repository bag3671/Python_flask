from flask import Flask, render_template, session, escape,request,Blueprint,current_app
from fbprophet import Prophet
from datetime import timedelta,datetime
import os
import logging
from logging.config import dictConfig
import pandas as pd
import pandas_datareader as pdr
import seaborn as sns
import folium
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)
from my_util.gangert_weather import get_gangseo_weather


#simple_bp = Blueprint('simple_bp', __name__, template_folder='templates')
stock_bp = Blueprint('stock_bp', __name__)
@stock_bp.before_app_first_request
def before_app_first_request():
    kospi_dict,kosdaq_dict = {},{}
    kospi = pd.read_csv('./static/data/KOSPI.csv', dtype={'종목코드': str})
    for i in kospi.index:
        kospi_dict[kospi['종목코드'][i]] = kospi['기업명'][i]
    kosdaq = pd.read_csv('./static/data/KOSDAQ.csv', dtype={'종목코드': str})
    for i in kosdaq.index:
        kosdaq_dict[kosdaq['종목코드'][i]] = kosdaq['기업명'][i]

@stock_bp.route('/stock', methods=['GET', 'POST'])
def stock():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':1, 'wc':0}
    if request.method == 'GET':
        print(get_gangseo_weather())
        return render_template('10.stock.html', menu=menu, weather=get_gangseo_weather(),
                                kospi=kospi_dict, kosdaq=kosdaq_dict)

    else:
        market = request.form['market']
        if market == 'KS':
            code = request.form['kospi_code']
            company = kospi_dict[code]
            code += '.KS'
        else:
            code = request.form['kosdaq_code']
            company = kosdaq_dict[code]
            code += '.KQ'
        learn_period = int(request.form['learn'])
        pred_period = int(request.form['pred'])
        today = datetime.now()
        start_learn = today - timedelta(days=learn_period*365)
        end_learn = today - timedelta(days=1)

        stock_data = pdr.DataReader(code, data_source='yahoo', start=start_learn, end=end_learn)
        df = pd.DataFrame({'ds': stock_data.index, 'y': stock_data.Close})
        df.reset_index(inplace=True)
        del df['Date']

        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=pred_period)
        forecast = model.predict(future)

        fig = model.plot(forecast);
        img_file = os.path.join(current_app.root_path, 'static/img/stock.png')
        fig.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('10.stock_res.html', menu=menu, weather=get_gangseo_weather(),
                                mtime=mtime, company=company, code=code)
