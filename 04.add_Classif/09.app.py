from flask import Flask, render_template, session, escape,request
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
from my_util.gangert_weather import *

app = Flask(__name__)
app.secret_key = 'qwert123456'
kospi_dict, kosdaq_dict = {}, {}

with open("./logging.json", 'r') as file:
    config = json.load(file)
dictConfig(config)
app.logger

def get_weather_main():
    weather = None
    try:
        weather = session['weather']
    except:
        app.logger.debug("get new weather info")
        weather = get_gangseo_weather()
        session['weather'] = weather
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60)
    return weather

@app.before_first_request
def before_first_request():
    kospi = pd.read_csv('./static/data/KOSPI.csv', dtype={'종목코드': str})
    for i in kospi.index:
        kospi_dict[kospi['종목코드'][i]] = kospi['기업명'][i]
    kosdaq = pd.read_csv('./static/data/KOSDAQ.csv', dtype={'종목코드': str})
    for i in kosdaq.index:
        kosdaq_dict[kosdaq['종목코드'][i]] = kosdaq['기업명'][i]

@app.route('/')
def layout():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    return render_template('09.main.html',weather=get_weather_main(), menu=menu)

@app.route('/stock', methods=['GET', 'POST'])
def stock():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':1, 'wc':0}
    if request.method == 'GET':
        return render_template('10.stock.html', menu=menu, weather=get_weather_main(),
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
        app.logger.debug(f"get stock data: {code}")
        df = pd.DataFrame({'ds': stock_data.index, 'y': stock_data.Close})
        df.reset_index(inplace=True)
        del df['Date']

        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=pred_period)
        forecast = model.predict(future)

        fig = model.plot(forecast);
        img_file = os.path.join(app.root_path, 'static/img/stock.png')
        fig.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('10.stock_res.html', menu=menu, weather=get_weather_main(), 
                                mtime=mtime, company=company, code=code)

@app.route('/park', methods=['GET', 'POST'])
def park():
        menu = {'ho':0, 'da':1, 'ml':0, 'se':1, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
        df = pd.read_csv("./static/data/park2.csv")
        if request.method == 'GET': 
            gu_names = sorted(df['지역'].unique().tolist())
            park_names = sorted(df['공원명'].tolist())
            map = folium.Map(location=[37.5502,126.982],zoom_start=11,title="Your map title")
            for n in df.index:
                folium.CircleMarker([df['lng'][n],df['lat'][n]],
                                    radius = df['면적'][n]/500000,
                                    popup=df['공원명'][n],
                                    color='#3186cc',fill_color='#3186cc').add_to(map)
            img_file = os.path.join(app.root_path, 'static/data/park_map.html')
            map.save(img_file)
            mtime = int(os.stat(img_file).st_mtime)

            return render_template("park.html",menu=menu, weather=get_weather_main(), gu_names=gu_names, park_names=park_names,mtime=mtime)
        else:
            if request.form['check'] == 'park':
                park_name = request.form['park_name']
                park_one = df[df['공원명'] == park_name]
                park_result={'park_name':park_name,'area':round(park_one['면적'],2).tolist()[0],'gu':park_one['지역'].tolist()[0],'addr':park_one['공원주소'].tolist()[0]}
                map = folium.Map(location=[park_one['lng'],park_one['lat']],zoom_start=11)
                folium.CircleMarker([park_one['lng'],park_one['lat']],
                                    radius = float(park_one['면적'])/50000,
                                    tooltip=park_one['공원명'].tolist()[0],
                                    color='#3186cc',fill_color='#3186cc').add_to(map)
                map_file = os.path.join(app.root_path, 'static/data/park_map.html')
                map.save(map_file)
                mtime = int(os.stat(map_file).st_mtime)
                return render_template("park_res.html",menu=menu, weather=get_weather_main(),park_result=park_result,mtime=mtime)
            else:
                gu_name = request.form['gu_name']
                gu_park = df[df['지역'] == gu_name]
                map = folium.Map(location=[37.5502,126.982],zoom_start=11,title="Your map title")
                for n in gu_park.index:
                    folium.Marker([gu_park['lng'][n],gu_park['lat'][n]],
                                                    tooltip=df['공원명'][n],
                                                    color='#3186cc',fill_color='#3186cc').add_to(map)
                map_file = os.path.join(app.root_path, 'static/data/park_map.html')
                map.save(map_file)
                mtime = int(os.stat(map_file).st_mtime)
                return render_template("park_res2.html",menu=menu, weather=get_weather_main(),gu_name=gu_name,mtime=mtime)
@app.route('/park_gu/<option>')
def park_gu(option):
    menu = {'ho':0, 'da':1, 'ml':0, 'se':1, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    park_new = pd.read_csv('./static/data/park_info.csv')
    park_gu = pd.read_csv('./static/data/park_gu.csv')
    park_gu.set_index('지역', inplace=True)
    geo_str = json.load(open('./static/data/02. skorea_municipalities_geo_simple.json',
                         encoding='utf8'))
    map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')
    if option == 'area':
        map.choropleth(geo_data = geo_str,
                       data = park_gu['공원면적'],
                       columns = [park_gu.index, park_gu['공원면적']],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')
    elif option == 'count':
        map.choropleth(geo_data = geo_str,
                       data = park_gu['공원수'],
                       columns = [park_gu.index, park_gu['공원수']],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')
    elif option == 'area_ratio':
        map.choropleth(geo_data = geo_str,
                       data = park_gu['공원면적비율'],
                       columns = [park_gu.index, park_gu['공원면적비율']],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')
    elif option == 'per_person':
        map.choropleth(geo_data = geo_str,
                       data = park_gu['인당공원면적'],
                       columns = [park_gu.index, park_gu['인당공원면적']],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')

    for i in park_new.index:
        folium.CircleMarker([park_new.lat[i], park_new.lng[i]], 
                        radius=int(park_new['size'][i]),
                        tooltip=f"{park_new['공원명'][i]}({int(park_new.area[i])}㎡)",
                        color='green', fill_color='green').add_to(map)
    html_file = os.path.join(app.root_path, 'static/img/ x')
    map.save(html_file)
    mtime = int(os.stat(html_file).st_mtime)
    # option_dict = {'area':'공원면적', 'count':'공원수', 'area_ratio':'공원면적 비율', 'per_person':'인당 공원면적'}
    return render_template('park_gu.html', menu=menu, weather=get_weather_main(),
                            option=option, mtime=mtime)

@app.route('/crime')
def crime():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':1, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    return render_template("crime.html", menu=menu,weather=get_weather_main())

if __name__ == '__main__':
    app.run(debug=True)