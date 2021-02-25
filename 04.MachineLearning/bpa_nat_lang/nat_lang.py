from flask import Blueprint, render_template, request, session, g,current_app
from datetime import timedelta
import pandas as pd
from my_util.gangert_weather import *
import numpy as np
import os
import requests
from urllib.parse import quote
import joblib,re,json
from konlpy.tag import Okt
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
global menu
menu = {'ho':0, 'da':0, 'ml':1, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 're':0, 'cu':0,'nl':1}

# @lang_bp.before_app_first_request
# def before_app_first_request():
#     global naver_tfidf_nb, imdb_tfidf_lr
#     print('============ Advanced Blueprint before_app_first_request() ==========')
#     naver_tfidf_nb = joblib.load('static/model/naver_tfidf_nb.pkl')
#     imdb_tfidf_lr = joblib.load('static/model/imdb_tfidf_lr.pkl')


@lang_bp.route('/trans', methods=['GET', 'POST'])
def trans():
   
    if request.method == 'GET':
        return render_template('trans.html', menu=menu, weather=get_weather_main())
    else:
        with open('static/keys/papago_key.json') as nkey:
            json_obj = json.load(nkey)
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

@lang_bp.route('/tts', methods=['GET', 'POST'])
def tts():
    if request.method == 'GET':
        return render_template('tts.html', menu=menu, weather=get_weather_main())
    else:
        text = request.form['text']
        speaker = request.form['speaker']
        pitch = request.form['pitch']
        speed = request.form['speed']
        volume = request.form['volume']
        emotion = request.form['emotion']

        with open('static/keys/clova_voice_key.json') as nkey:
            json_obj = json.load(nkey)
        client_id = list(json_obj.keys())[0]
        client_secret = json_obj[client_id]

        url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        val = {
            "speaker": speaker, "speed": speed, "text": text,
            "pitch": pitch, "volume": volume, "emotion": emotion
        }
        response = requests.post(url, data=val, headers=headers)
        rescode = response.status_code
        audio_file = os.path.join(current_app.root_path, 'static/img/cpv.mp3')
        if(rescode == 200):
            with open(audio_file, 'wb') as f:
                f.write(response.content)
        mtime = int(os.stat(audio_file).st_mtime)

        return render_template('tts_res.html', menu=menu, weather=get_weather_main(),
                                res=val, mtime=mtime)

# @lang_bp.route('/emotion', methods=['GET', 'POST'])
# def emotion():
#     if request.method == 'GET':
#         return render_template('emotion.html', menu=menu, weather=get_weather_main())
#     else:
#         text = request.form['text']

#         # 언어감지 카카오
#         with open('static/keys/kakaoaikey.txt') as kfile:
#             kai_key = kfile.read(100)
#         k_url = f'https://dapi.kakao.com/v3/translation/language/detect?query={quote(text)}'
#         result = requests.get(k_url,
#                               headers={"Authorization": "KakaoAK "+kai_key}).json()
#         lang = result['language_info'][0]['code']
#         print(lang)

#         # 파파고 번역 
#         # 한국어 => 영어
#         # 영어 => 한국어
#         # with open('static/keys/papago_key.json') as nkey:
#         #     json_obj = json.load(nkey)
#         # client_id = list(json_obj.keys())[0]
#         # client_secret = json_obj[client_id]
#         # url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
#         # headers = {
#         #     "X-NCP-APIGW-API-KEY-ID": client_id,
#         #     "X-NCP-APIGW-API-KEY": client_secret
#         # }
#         # if lang == 'kr':
#         #     val = {"source": 'ko', "target": 'en', "text": text}
#         # elif lang == 'en':
#         #     val = {"source": 'en', "target": 'ko', "text": text}
#         # else:
#         #     val = {"source": cn-, "target": 'en', "text": text}
#         # result = requests.post(url, data=val, headers=headers).json()
#         # tr_text = result['message']['result']['translatedText']
        
#         # 카카오 번역으로 다중언어가 가능하게
#         with open('static/keys/kakaoaikey.txt') as kfile:
#             kai_key = kfile.read(200)
#         url = 'https://kapi.kakao.com/v1/translation/translate'
#         headers={ "Authorization" : "KakaoAK "+kai_key}

#         if lang == 'en':
#             data = {"src_lang": lang, "target_lang": 'kr', "query": text}
#         else:
#             data = {"src_lang": lang, "target_lang": 'en', "query": text}
#         response = requests.post(url, headers=headers, data=data)
#         tr_text = response.json()['translated_text'][0][0]
        

#         okt = Okt()
#         stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다','을']
#         if lang == 'kr':
#             review = re.sub("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]", "", text)
#         else:
#             review = re.sub("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]", "", tr_text)
#         morphs = okt.morphs(review, stem=True) # 토큰화
#         ko_review = ' '.join([word for word in morphs if not word in stopwords]) # 불용어 제거
#         en_review = tr_text if lang == 'kr' else text

#         pred_ko = '긍정' if naver_tfidf_nb.predict([ko_review])[0] else '부정'
#         pred_en = '긍정' if imdb_tfidf_lr.predict([en_review])[0] else '부정'

#         if lang == 'kr':
#             res = {'src_text':text, 'dst_text':tr_text, 'src_pred':pred_ko, 'dst_pred':pred_en,'lang':lang}
#         else:
#             res = {'src_text':text, 'dst_text':tr_text, 'src_pred':pred_en, 'dst_pred':pred_ko,'lang':lang}

#         return render_template('emotion_res.html', res=res,
#                                 menu=menu, weather=get_weather_main())