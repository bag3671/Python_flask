import requests
from urllib.parse import urlparse

def get_gangseo_weather(lng = 126.849532173376, lat = 37.5509655144007):
    key_fd = open('D:/workspace/python_flask/04.MachineLearning/static/data/openweatherkey.txt',mode='r')
    openweather_key = key_fd.read(200)
    key_fd.close()
    lng = 126.849532173376
    lat = 37.5509655144007
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&units=metric&appid={openweather_key}&lang=kr'
    results = requests.get(url, verify=False).json()
    weather = results['weather'][0]
    main = results['main']
    tmp = main['temp']
    tmp_min = main['temp_min']
    tmp_max = main['temp_max']
    tmp = round(float(tmp),1)
    k = [weather,tmp,tmp_min,tmp_max]
    return k