from flask import Flask, jsonify, json, request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'author': 'Vivek Singh Bhadauria',
        'author_url': 'http://viveksb007.wordpress.com/',
        'base_url': 'zeolearn.com/',
        'endpoints': {
            'Returns URLS of images': '/magazines/photos/{number of photos}',
            }
    })

@app.route('/magazines/photos/<number_of_images>', methods=['GET'])
def get_images_links(number_of_images):
    image_list = []

    response = requests.get('https://www.zeolearn.com/magazine/')
    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup.find_all('img'):
        image_list.append(tag['src'])
    image_data = {}

    if int(number_of_images) < len(image_list):
        for i in range(0, int(number_of_images)):
            image_data[str(i)] = image_list[i]
    else:
        for i in range(0, len(image_list)):
            image_data[str(i)] = image_list[i]
    return jsonify(image_data)

@app.route('/messages', methods = ['POST'])
def api_message():

    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data
    elif request.headers['Content-Type'] == 'application/json':
        return "Json Message: " + json.dumps(request.json)
    else:
        return "415 Unsopported Media Type ;"

if __name__ == '__main__':
    app.run()