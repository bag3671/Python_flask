from flask import Flask, render_template, session
from datetime import timedelta,datetime
from my_util.gangert_weather import *
from bp5_stock.stock import stock_bp
from bp1_seoul.seoul import seoul_bp
from bp3_carto.carto import carto_bp
from bp6_wordCloud.word import word_bp

app = Flask(__name__)
app.secret_key = 'qwert123456'
app.register_blueprint(stock_bp, url_prefix='/stock')
app.register_blueprint(seoul_bp, url_prefix='/seoul')
app.register_blueprint(carto_bp, url_prefix='/cartogram')
app.register_blueprint(word_bp, url_prefix='/word')

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

@app.route('/')
def index():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    return render_template('09.main.html',weather=get_weather_main(), menu=menu)

if __name__ == '__main__':
    app.run(debug=True)