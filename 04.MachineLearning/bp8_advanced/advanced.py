from flask import Blueprint, render_template, request, session, g,current_app
from datetime import timedelta
from fbprophet import Prophet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.datasets import load_digits
import matplotlib.pyplot as plt
import joblib
import pandas as pd
from konlpy.tag import Okt
import os
from my_util.gangert_weather import *

advanced_bp = Blueprint('advanced_bp', __name__)

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
menu = {'ho':0, 'da':0, 'ml':10, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':1, 're':0, 'cu':0}

@advanced_bp.before_app_first_request
def before_app_first_request():
    global naver_count_lr, naver_count_nb, naver_tfidf_lr, naver_tfidf_nb
    global imdb_count_lr, imdb_tfidf_lr
    global news_count_lr, news_tfidf_lr, news_tfidf_sv
    print('============ Advanced Blueprint before_app_first_request() ==========')
    imdb_count_lr = joblib.load('static/model/imdb_count_lr.pkl')
    imdb_tfidf_lr = joblib.load('static/model/imdb_tfidf_lr.pkl')
    news_count_lr = joblib.load('static/model/news_count_lr.pkl')
    news_tfidf_lr = joblib.load('static/model/news_tfidf_lr.pkl')
    news_tfidf_sv = joblib.load('static/model/news_tfidf_sv.pkl')
    naver_count_lr = joblib.load('static/model/naver_count_lr.pkl')
    naver_count_nb = joblib.load('static/model/naver_count_nb.pkl')
    naver_tfidf_lr = joblib.load('static/model/naver_tfidf_lr.pkl')
    naver_tfidf_nb = joblib.load('static/model/naver_tfidf_nb.pkl')
    

@advanced_bp.route('/digits', methods=['GET', 'POST'])
def digits():
    if request.method == 'GET':
        return render_template('digits.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        index_list = list(range(index, index+5))
        digits = load_digits()
        df = pd.read_csv('static/data/digits_test.csv')
        img_index_list = df['index'].values
        target_index_list = df['target'].values
        index_list = img_index_list[index:index+5]

        scaler = joblib.load('static/model/digits_scaler.pkl')
        test_data = df.iloc[index:index+5, 1:-1]
        test_scaled = scaler.transform(test_data)
        label_list = target_index_list[index:index+5]
        lrc = joblib.load('static/model/digits_lr.pkl')
        svc = joblib.load('static/model/digits_sv.pkl')
        rfc = joblib.load('static/model/digits_rf.pkl')
        pred_lr = lrc.predict(test_scaled)
        pred_sv = svc.predict(test_scaled)
        pred_rf = rfc.predict(test_scaled)
        
        img_file_wo_ext = os.path.join(current_app.root_path, 'static/img/digit')
        for k, i in enumerate(index_list):
            plt.figure(figsize=(2,2))
            plt.xticks([]); plt.yticks([])
            img_file = img_file_wo_ext + str(k+1) + '.png'
            plt.imshow(digits.images[i], cmap=plt.cm.binary, interpolation='nearest')
            plt.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        result_dict = {'index':index_list, 'label':label_list,
                       'pred_lr':pred_lr, 'pred_sv':pred_sv, 'pred_rf':pred_rf}
        
        return render_template('digits_res.html', menu=menu, mtime=mtime,
                                result=result_dict, weather=get_weather_main())

@advanced_bp.route('/news', methods=['GET', 'POST'])
def news():
    target_names = ['alt.atheism', 'comp.graphics', 'comp.os.ms-windows.misc',
                    'comp.sys.ibm.pc.hardware', 'comp.sys.mac.hardware', 'comp.windows.x',
                    'misc.forsale', 'rec.autos', 'rec.motorcycles', 'rec.sport.baseball',
                    'rec.sport.hockey', 'sci.crypt', 'sci.electronics', 'sci.med',
                    'sci.space', 'soc.religion.christian', 'talk.politics.guns',
                    'talk.politics.mideast', 'talk.politics.misc', 'talk.religion.misc']
    if request.method == 'GET':
        return render_template('news.html', menu=menu, weather=get_weather_main())
    else:
        index = int(request.form['index'] or 0)
        df = pd.read_csv('static/data/news/test.csv')
        label = f'{df.target[index]} ({target_names[df.target[index]]})'
        test_data = []
        test_data.append(df.data[index])

        pred_c_lr = news_count_lr.predict(test_data)
        pred_t_lr = news_tfidf_lr.predict(test_data)
        pred_t_sv = news_tfidf_sv.predict(test_data)
        result_dict = {'index':index, 'label':label, 
                       'pred_c_lr':f'{pred_c_lr[0]} ({target_names[pred_c_lr[0]]})',
                       'pred_t_lr':f'{pred_t_lr[0]} ({target_names[pred_t_lr[0]]})',
                       'pred_t_sv':f'{pred_t_sv[0]} ({target_names[pred_t_sv[0]]})'}
        
        return render_template('news_res.html', menu=menu, news=df.data[index],
                                res=result_dict, weather=get_weather_main())

@advanced_bp.route('/imdb', methods=['GET', 'POST'])
def imdb():
    if request.method == 'GET':
        return render_template('imdb.html', menu=menu, weather=get_weather_main())
    else:
        test_data = []
        label = '직접 확인'
        if request.form['option'] == 'index':
            index = int(request.form['index'] or 0)
            df_test = pd.read_csv('static/data/IMDB_test.csv')
            test_data.append(df_test.iloc[index, 0])
            label = '긍정' if df_test.sentiment[index] else '부정'
        else:
            test_data.append(request.form['review'])

        pred_cl = '긍정' if imdb_count_lr.predict(test_data)[0] else '부정'
        pred_tl = '긍정' if imdb_tfidf_lr.predict(test_data)[0] else '부정'
        result_dict = {'label':label, 'pred_cl':pred_cl, 'pred_tl':pred_tl}
        return render_template('imdb_res.html', menu=menu, review=test_data[0],
                                res=result_dict, weather=get_weather_main())
                    
@advanced_bp.route('/naverMovie', methods=['GET', 'POST'])
def naverMovie():
    if request.method == 'GET':
        return render_template('naverMovie.html', menu=menu, weather=get_weather_main())
    else:
        stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다','을']
        okt = Okt()
        index = int(request.form['index'] or 0)
        # df_test = pd.read_table('static/data/naver/test_df.tsv')
        df_test = pd.read_csv('static/data/naver/test_df.tsv',sep='\t')
        test_data = []
        for sentence in df_test['document'][index]:
            temp_X = []
            temp_X = okt.morphs(sentence, stem=True)
            temp_X = ' '.join([word for word in temp_X if not word in stopwords]) 
            test_data.append(temp_X)
        label = '긍정' if df_test.label[index] else '부정'

        pred_c_lr = '긍정' if naver_count_lr.predict(test_data)[0] else '부정'
        pred_c_nb = '긍정' if naver_count_nb.predict(test_data)[0] else '부정'
        pred_t_lr = '긍정' if naver_tfidf_lr.predict(test_data)[0] else '부정'
        pred_t_nb = '긍정' if naver_tfidf_nb.predict(test_data)[0] else '부정'
        result_dict = {'label':label, 'pred_c_lr':pred_c_lr, 'pred_c_nb':pred_c_nb,
                        'pred_t_lr':pred_t_lr,'pred_t_nb':pred_t_nb}
        return render_template('naverMovie_res.html', menu=menu, review=df_test['document'][index],
                                res=result_dict, weather=get_weather_main())