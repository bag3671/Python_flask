from flask import Blueprint, render_template, request, session
from flask import current_app, redirect, url_for
from datetime import datetime, timedelta
import os
import pandas as pd
from my_util.gangert_weather import *
import my_util.crawl_util as cu

crawl_bp = Blueprint('crawl_bp', __name__)

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
menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':1, 'st':0, 'wc':0}

@crawl_bp.route('/food', methods=['GET', 'POST'])
def food():
    if request.method == 'GET':
        place = request.args.get('place', '발산역')
        rest_list = cu.siksin(place)
        return render_template('food.html', menu=menu, weather=get_weather_main(),
                                rest_list=rest_list, place=place)
    else:
        place = request.form['place']
        return redirect(url_for('crawl_bp.food')+f'?place={place}')

@crawl_bp.route('/book')
def book():
    book_list = cu.interpark()
    return render_template('book.html', menu=menu, weather=get_weather_main(),
                            book_list=book_list)