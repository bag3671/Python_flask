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
seoul_bp = Blueprint('seoul_bp', __name__)
menu = {'ho':0, 'da':1, 'ml':0, 'se':1, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}

@seoul_bp.route('/park', methods=['GET', 'POST'])
def park():
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
            img_file = os.path.join(current_app.root_path, './static/data/park_map.html')
            map.save(img_file)
            mtime = int(os.stat(img_file).st_mtime)

            return render_template("park.html",menu=menu, weather=get_gangseo_weather(), gu_names=gu_names, park_names=park_names,mtime=mtime)
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
                map_file = os.path.join(current_app.root_path, 'static/data/park_map.html')
                map.save(map_file)
                mtime = int(os.stat(map_file).st_mtime)
                return render_template("park_res.html",menu=menu, weather=get_gangseo_weather(),park_result=park_result,mtime=mtime)
            else:
                gu_name = request.form['gu_name']
                gu_park = df[df['지역'] == gu_name]
                map = folium.Map(location=[37.5502,126.982],zoom_start=11,title="Your map title")
                for n in gu_park.index:
                    folium.Marker([gu_park['lng'][n],gu_park['lat'][n]],
                                                    tooltip=df['공원명'][n],
                                                    color='#3186cc',fill_color='#3186cc').add_to(map)
                map_file = os.path.join(current_app.root_path, 'static/data/park_map.html')
                map.save(map_file)
                mtime = int(os.stat(map_file).st_mtime)
                return render_template("park_res2.html",menu=menu, weather=get_gangseo_weather(),gu_name=gu_name,mtime=mtime)
@seoul_bp.route('/park_gu/<option>')
def park_gu(option):
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
    html_file = os.path.join(current_app.root_path, 'static/img/park_gu.html')
    map.save(html_file)
    mtime = int(os.stat(html_file).st_mtime)
    option_dict = {'area':'공원면적', 'count':'공원수', 'area_ratio':'공원면적 비율', 'per_person':'인당 공원면적'}
    return render_template('park_gu.html', menu=menu, weather=get_gangseo_weather(),
                            option=option,option_dict=option_dict, mtime=mtime)
@seoul_bp.route('/crime/<option>')
def crime(option):
    crime = pd.read_csv('./static/data/crime.csv', index_col='구별')
    police = pd.read_csv('./static/data/police.csv')
    geo_str = json.load(open('./static/data/02. skorea_municipalities_geo_simple.json',
                         encoding='utf8'))
    option_dict = {'crime':'범죄', 'murder':'살인', 'rob':'강도', 'rape':'강간', 'thief':'절도', 'violence':'폭력',
                   'arrest':'검거율', 'a_murder':'살인검거율', 'a_rob':'강도검거율', 'a_rape':'강간검거율', 
                   'a_thief':'절도검거율', 'a_violence':'폭력검거율'}
    current_app.logger.debug(option_dict[option])

    map = folium.Map(location=[37.5502, 126.982], zoom_start=11)
    if option in ['crime', 'murder', 'rob', 'rape', 'thief', 'violence']:
        map.choropleth(geo_data = geo_str, data = crime[option_dict[option]],
               columns = [crime.index, crime[option_dict[option]]],
               fill_color = 'PuRd', key_on = 'feature.id')
    else:
        map.choropleth(geo_data = geo_str, data = crime[option_dict[option]],
               columns = [crime.index, crime[option_dict[option]]],
               fill_color = 'YlGnBu', key_on = 'feature.id')
        for i in police.index:
            folium.CircleMarker([police.lat[i], police.lng[i]], radius=10,
                                tooltip=police['관서명'][i],
                                color='crimson', fill_color='crimson').add_to(map)

    html_file = os.path.join(current_app.root_path, 'static/img/crime.html')
    map.save(html_file)
    mtime = int(os.stat(html_file).st_mtime)
    return render_template('crime.html', menu=menu, weather=get_gangseo_weather(),
                            option=option, option_dict=option_dict, mtime=mtime)