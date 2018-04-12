import os
import cv2
import numpy as np
from PIL import Image
from flask import Flask, request, redirect, url_for, flash
from keras import backend as K
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from markupsafe import Markup
from werkzeug.utils import secure_filename

from flask import Flask, jsonify, render_template
from flask import request
urlDomain = 'http://127.0.0.1:5000/static/img/'
K.set_image_dim_ordering('th')

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'static/img')

UPLOAD_FOLDER = my_file

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def hello_world():
    return render_template("upload.html")

@app.route('/upload', methods=['GET','POST'])
def upload():
    resultTest = ''
    if request.method == 'POST':
        print('pod1')
        print(request.files)
        # check if the post request has the file part
        if 'photo' not in request.files:
            print('pod2')
            print(request.url)
            return redirect(request.url)
        print('pod3')
        file = request.files['photo']
        # if user does not select file, browser also
        # submit a empty part without filename
        print(file)
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            print(UPLOAD_FOLDER)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            f = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(f)
            imgURL   = urlDomain +  filename
            msg = predictionImage(filename)
            resultTest = msg
            return render_template('output.html',url = imgURL, name=resultTest )
            # return redirect(url_for('upload',
            #                         filename=filename))

    return str(resultTest)

def predictionImage(filename):
    fileimg = os.path.join(my_file, filename)
    print(fileimg)
    imageM = Image.open(fileimg)
    image = cv2.imread(fileimg)

    orig = image.copy()
    # pre-process the image for classification
    image = cv2.resize(image, (32, 32))
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    print("[INFO] loading network...")
    model = load_model("nude_not_nude.model")
    # print (model)
    # classify the input image
    # print(image)
    (notnude, nude) = model.predict(image)[0]
    # build the label
    label = "Nude" if nude > notnude else "Not Nude"
    proba = nude if nude > notnude else notnude
    label = "{}: {:.2f}%".format(label, proba * 100)
    print(label)
    return str(label)
if __name__ == '__main__':
    app.run()
