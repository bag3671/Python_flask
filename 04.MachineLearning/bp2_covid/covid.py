from flask import Blueprint, render_template, request, session, g
from flask import current_app,redirect,url_for
from werkzeug.utils import secure_filename
from datetime import timedelta,datetime
import pandas as pd
import os
from my_util.gangert_weather import *
import my_util.drawKorea as dk
import my_util.db_module as dm
import my_util.covid_util as cu



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

menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
@covid_bp.route('/daily')
def daily():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    rows = dm.get_region_daily(date)

    return render_template('daily.html', menu=menu, weather=get_weather_main(),
                            date=date, rows=rows)

@covid_bp.route('/update_daily/<date>')    
def update_daily(date):
    rows = dm.get_region_daily(date)
    print('date',date)
    if len(rows) == 0:
        cu.get_region_by_date(date)

    return redirect(url_for('covid_bp.daily')+f'?date={date}')

@covid_bp.route('/agender')
def agender():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    rows = dm.get_agender_daily(date)

    return render_template('agender.html', menu=menu, weather=get_weather_main(),
                            date=date, rows=rows)

@covid_bp.route('/update_agender/<date>')
def update_agender(date):
    rows = dm.get_agender_daily(date)
    if len(rows) == 0:
        cu.get_agender_by_date(date)

    return redirect(url_for('covid_bp.agender')+f'?date={date}')

@covid_bp.route('/drawCovid/<option>')
def drawCovid(option):
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    rows = dm.select_covid_incDec()
    if option == 'monthly': 
        img_file = os.path.join(current_app.root_path, 'static/img/monthly_covid.png')
        df = pd.DataFrame(rows,columns={'date':0,'region':1,'count':2})
        dm.saving_covid_plt(df,img_file)
        mtime = int(os.stat(img_file).st_mtime)
    elif option == 'countMonthly':
        img_file = os.path.join(current_app.root_path, 'static/img/countMonthly.png')
        df = pd.DataFrame(rows,columns={'date':0,'region':1,'count':2})
        dm.saving_covid_plt2(df,img_file)
        mtime = int(os.stat(img_file).st_mtime)
    elif option == 'monthArea':
        img_file = os.path.join(current_app.root_path, 'static/img/monthArea.png')
        df = pd.DataFrame(rows,columns={'date':0,'region':1,'count':2})
        month = '12월'
        # index_list = dm.saving_covid_plt3(df,img_file,month)
        mtime = int(os.stat(img_file).st_mtime)
    return render_template('drawCovid.html',menu=menu, weather=get_weather_main(),
                            mtime=mtime,option=option)
    