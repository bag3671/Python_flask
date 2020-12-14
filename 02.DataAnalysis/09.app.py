from flask import Flask, render_template, session, escape,request
from fbprophet import Prophet
from datetime import timedelta,datetime
import os
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
        print(today)

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

@app.route('/park')
def park():
        menu = {'ho':0, 'da':1, 'ml':0, 'se':1, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
        df = pd.read_csv("./static/data/seoulpark_result.csv")
        plt.figure(figsize=(10,10))
        sns.barplot(data=df.sort_values('면적대비 공원면적 비율',ascending=False).head(10),y='면적대비 공원면적 비율',x='지역')
        plt.title("구면적대비 공원면적 TOP10")
        img_file = os.path.join(app.root_path, 'static/img/구면적대비 공원면적 TOP10.png')
        plt.savefig(img_file)
        sns.lmplot(data = df,x='인구수',y='공원면적',size=6)
        plt.title("인구수대비 공원면적")
        img_file = os.path.join(app.root_path, 'static/img/인구수대비 공원면적.png')
        plt.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)
        park2 = pd.read_csv("./static/data/park2.csv")
        geo_path = './static/data/02. skorea_municipalities_geo_simple.json'
        geo_str = json.load(open(geo_path, encoding='UTF-8'))
        map = folium.Map(location=[37.5502,126.982],zoom_start=11,title="Your map title")
        df = df.set_index("지역")
        del df['Unnamed: 0'] 
        map.choropleth(geo_data = geo_str,
                        data = df,
                        columns=[df.index, '인당 면적비'],
                        fill_color = 'PuRd',
                        key_on = 'feature.id')
        for n in park2.index:
            folium.CircleMarker([park2['lng'][n],park2['lat'][n]],
                                radius = park2['면적'][n]/500000,
                                popup=park2['공원명'][n],
                                color='#3186cc',fill_color='#3186cc').add_to(map)
        title_html = '''
                    <h3 align="center" style="font-size:20px"><b>인당면적비와 공원크기</b></h3>
                    '''
        map.get_root().html.add_child(folium.Element(title_html))
        map.save("./static/data/park_map.html")
        return render_template("park.html",menu=menu, weather=get_weather_main(),mtime=mtime)

@app.route('/crime')
def crime():
    return render_template("crime.html")

if __name__ == '__main__':
    app.run(debug=True)