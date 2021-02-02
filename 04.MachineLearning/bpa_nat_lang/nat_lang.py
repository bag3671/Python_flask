from flask import Blueprint, render_template, request, session, g,current_app
from datetime import timedelta
import pandas as pd
from my_util.gangert_weather import *
import numpy as np
import os
import requests
from urllib.parse import quote
import json
lang_bp = Blueprint('lang_bp', __name__)

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

@lang_bp.route('/trans', methods=['GET', 'POST'])
def trans():
    menu = {'ho':0, 'da':0, 'ml':1, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 're':0, 'cu':0}
    if request.method == 'GET':
        return render_template('trans.html', menu=menu, weather=get_weather_main())
    else:
        with open('static/keys/papago_key.json') as nkey:
            json_str = nkey.read(200)
        json_obj = json.loads(json_str)
        client_id = list(json_obj.keys())[0]
        client_secret = json_obj[client_id]
        text = request.form['text']
        lang = request.form['lang']
        url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
        val = {
            "source": 'ko',
            "target": lang,
            "text": text
            }
        headers = {
                    "X-NCP-APIGW-API-KEY-ID": client_id,
                    "X-NCP-APIGW-API-KEY": client_secret
        }
        response = requests.post(url,  data=val, headers=headers)
        rescode = response.status_code
        print(f'naver {rescode}')
        result = response.json()
        naver_trans = result['message']['result']['translatedText']

        with open('static/keys/kakaoaikey.txt') as kfile:
            kai_key = kfile.read(200)
        if lang == 'zh-CN':
                lang = 'cn'
        def kakao_trans(text):
            url = 'https://kapi.kakao.com/v1/translation/translate'
            headers={ "Authorization" : "KakaoAK "+kai_key}
            data = {"src_lang" : "kr",
                "target_lang" : lang,
                "query" : text }
            response = requests.post(url, headers=headers, data=data)
            rescode = response.status_code
            print(f'kakao {rescode}')
            return response.json()['translated_text']
        kaka_trans = kakao_trans(text)[0][0]
        return render_template('trans_res.html', menu=menu, weather=get_weather_main(),text=text,naver=naver_trans,kakao = kaka_trans)