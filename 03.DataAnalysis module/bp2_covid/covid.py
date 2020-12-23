from flask import Blueprint, render_template, request, session, g
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta,datetime
import pandas as pd
from my_util.gangert_weather import *
import my_util.drawKorea as dk
import my_util.db_module as dm


covid_bp = Blueprint('covid_bp', __name__)

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

@covid_bp.route('/daily')
def daily():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    rows = dm.get_region_daily(date)

    return render_template('daily.html', menu=menu, weather=get_weather_main(),
                            date=date, rows=rows)
    
@covid_bp.route('/agender')
def agender():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    rows = dm.get_agender_daily(date)

    return render_template('agender.html', menu=menu, weather=get_weather_main(),
                            date=date, rows=rows)
    
