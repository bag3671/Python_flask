from flask import Blueprint, render_template, request, session, g,current_app
import urllib3
import json
import base64
import os
import json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

etri_bp = Blueprint('etri_bp', __name__)

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
            'cf':0, 'ac':0, 're':0, 'cu':0,'nl':0,'im':0,'et':1}
@etri_bp.route('/img', methods=['GET', 'POST'])
def img():
    if request.method == 'GET':
        return render_template('etri_image.html', menu=menu, weather=get_weather_main())
    else:
        with open('D:/Workspace/Python_flask/04.MachineLearning/static/data/etri_key.txt') as f:
            eai_key = f.read(100)
        openApiURL = "http://aiopen.etri.re.kr:8000/ObjectDetect"
        f_img = request.files['img']
        file_img = os.path.join(current_app.root_path, 'static/upload/') +'eimg.jpg'
        f_img.save(file_img)
        current_app.logger.debug(f"{f_img}, {file_img}")

        image_file = file_img
        _, image_type = os.path.splitext(image_file)
        image_type = '.jpg' if image_type == '.jpg' else '.jfif'
        with open(image_file,'rb') as f:
            imageContents = base64.b64encode(f.read()).decode("utf8")
        request_json = {
                    "access_key": eai_key,
                    "argument": {
                        "type": image_type[1:],
                        "file": imageContents
                    }
                }
        http = urllib3.PoolManager()
        response = http.request(
            "POST",
            openApiURL,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps(request_json)
        )
        current_app.logger.info(response.status)
        result = json.loads(response.data)
        image = Image.open(image_file)
        data_list = result['return_object']['data']
        draw = ImageDraw.Draw(image)
        name_list = []
        for data in data_list:
            name = data['class']
            x = int(data['x'])
            y = int(data['y'])
            w = int(data['width'])
            h = int(data['height'])
            name_list.append(name)
            font = ImageFont.truetype("arial",25)
            draw.text((x+10,y+10), name,font = font,fill=(255,255,255))
            draw.rectangle(((x,y),(x+w,y+h)),outline=(255,0,0),width=2)
        image.save(os.path.join(current_app.root_path, 'static/upload/') +'etri.jpg')
        mtime = int(os.stat(file_img).st_mtime)
        return render_template('etri_image_res.html', menu=menu, weather=get_weather_main(),mtime=mtime,names=name_list)