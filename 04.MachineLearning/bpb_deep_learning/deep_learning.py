from glob import glob
from tensorflow.keras.applications.resnet50 import ResNet50, decode_predictions
from tensorflow.keras.applications.resnet import ResNet101, decode_predictions
from tensorflow.keras.applications.inception_v3 import InceptionV3, decode_predictions
from tensorflow.keras.applications.vgg16 import VGG16, decode_predictions
from tensorflow.keras.applications.vgg19 import VGG19, decode_predictions
import pandas as pd
import cv2
import os
from skimage import io
from flask import Blueprint, render_template, request, session, g,current_app

deep_bp = Blueprint('deep_bp', __name__)

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
            'cf':0, 'ac':0, 're':0, 'cu':0,'nl':0,'im':1}
@deep_bp.route('/img', methods=['GET', 'POST'])
def img():
    if request.method == 'GET':
        return render_template('deep-learning-img.html', menu=menu, weather=get_weather_main())
    else:
        vgg16 = VGG16()
        vgg19 = VGG19()
        resnet50 = ResNet50()
        resnet101 = ResNet101()
        # inceptionv3 = InceptionV3()
        keras_dict = {'vgg16':vgg16,'vgg19':vgg19,'resnet50':resnet50,'resnet101':resnet101}
        
        f_img = request.files['img']
        file_img = os.path.join(current_app.root_path, 'static/upload/') +'img.jpg'
        f_img.save(file_img)
        current_app.logger.debug(f"{f_img}, {file_img}")
        img = io.imread(file_img)
        # # 불안정함
        # # img = cv2.imread(file, -1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img1 = cv2.resize(img, (224, 224))
        # img2 = cv2.resize(img, (299, 299))
        result_list = []
        name_list = []
        for key,value in keras_dict.items():
            yhat = value.predict(img1.reshape(-1, 224, 224, 3))
            label = decode_predictions(yhat)
            label = label[0][0]
            label_per = f'{label[1]}({round(label[2]*100, 1)}%)'
            result_list.append(label_per)
            name_list.append(key)
        mtime = int(os.stat(file_img).st_mtime)
        result_dic = {'result':result_list,'name':name_list,'img_name':f_img.filename,'num':len(name_list)}
        return render_template('deep-learnig-img-res.html', menu=menu, weather=get_weather_main(),result_dic = result_dic,mtime=mtime)