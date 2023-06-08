import os
import numpy as np
import layoutparser as lp
import lxml.etree as etree
import cv2
from pdf2image import convert_from_path
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from detection.line_detection import ResizeWithAspectRatio
from detection.table_detection import create_metadata, createCSV
from detection.utils import convertToJPG, CsvToJSON
from model import load, paths
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, origins="*")

xmlPath = './tableXML.xml'


@cross_origin()
@app.route('/generate', methods=['POST'])
def generate():
    files = request.files.getlist('file')
    for file in files:
        file.save('./savedImages/' + file.filename)
        image_name = file.filename

    # convertToJPG('./content/tables_sample.pdf')
    IMAGE_PATH = os.path.join('./savedImages/', image_name)
    # table_coords = load(IMAGE_PATH)
    image = cv2.imread(IMAGE_PATH)

    # x1, y1 = table_coords[0][0]
    # x2, y2 = table_coords[0][1]

    # 39 129 1027 312
    x1, y1 = 39, 129
    x2, y2 = 1027, 312
    print("{} {} {} {}", x1, y1, x2, y2)
    try:
        table_img = image[y1 - 30:y2 + 30, x1 - 30:x2 + 30]
    except:
        table_img = image

    root = etree.Element("document")
    root.append(create_metadata(table_img))
    myfile = open(xmlPath, "w")
    myfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    myfile.write(etree.tostring(root, pretty_print=True, encoding="unicode"))
    myfile.close()

    createCSV()

    json_data = CsvToJSON()
    return json_data


@app.route('/downloadXMl', methods=['POST'])
def downloadXML():
    filename = 'tableXML.xml'
    path = './' + filename
    return send_file(path, mimetype='text/xml', as_attachment=True)


@app.route('/downloadCSV', methods=['POST'])
def downloadCSV():
    filename = 'tableCSV.csv'
    path = './' + filename
    return send_file(path, mimetype='text/csv', as_attachment=True)


@app.route('/index')
def index():
    return render_template('index.html', name='PyCharm')


if __name__ == '__main__':
    print('staring server')
    app.run(host='0.0.0.0', port=8081)
