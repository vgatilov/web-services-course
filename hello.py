from flask import Flask, escape, request, jsonify,abort, redirect, url_for, render_template, send_file
import pickle
import numpy as np
import pandas as pd
knn = pickle.load(open('knn.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get("name", "My Best Friend!")
    print('hi')
    return f'Hello, {escape(name)}!'

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % escape(username)

def mean(numbers):
    return float(sum(numbers))/max(1,len(numbers))

@app.route('/avg/<nums>')
def avg(nums):
    # show the user profile for that user
    nums = nums.split(',')
    nums = [float(num) for num in nums]
    nums_mean = mean(nums)
    print(nums)
    return str(nums_mean)

@app.route('/iris/<param>')
def iris(param):
    nums = param.split(',')
    nums = np.array([float(num) for num in nums]).reshape(1, -1)
    print(nums)
    return str(knn.predict(nums))

@app.route('/show_image')
def show_image():
    
    return '<img src="/static/setosa.jpg" alt="Italian Trulli">'

@app.route('/badrequest400')
def bad_request():
    return abort(400)

@app.route('/iris_post', methods=['POST'])
def add_message():
    try:
        content = request.json

        nums = content['flower'].split(',')
        nums = np.array([float(num) for num in nums]).reshape(1, -1)
        predict = {'class':str(knn.predict(nums)[0])}
        return jsonify(predict)
    except:
        return redirect(url_for('bad_request'))

from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    file = FileField()

@app.route('/submit', methods=('GET', 'POST'))
def submit():
    form = MyForm()
    if form.validate_on_submit():

        f = form.file.data
        filename = form.name.data + '.txt'
        #f.save(os.path.join(
        #    filename
        #))
        print('!!!!!!')
        df = pd.read_csv(f, header=None)
        print(df.head())
        predict = knn.predict(df)
        print(predict)
        result = pd.DataFrame(predict)
        result.to_csv(filename, index = False)
        return send_file(filename,
                     mimetype='text/csv',
                     attachment_filename=filename,
                     as_attachment=True)
    return render_template('submit.html', form=form)

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename + 'uploaded')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'file uploaded'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''