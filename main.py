from flask import Flask, request, render_template, make_response, redirect, flash, url_for,session,jsonify
from datetime import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from readfile import extract_text_from_pdf
from utils import plagueChecker
import json

plague = plagueChecker('361b62e1609a67f64296bf1958acafa7')
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = ['pdf']

app = Flask(__name__)
app.secret_key ="how do you do this"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plagiarism.db'
db = SQLAlchemy(app)


#models 
class User(db.Model):
    """Model for user accounts."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), unique=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

class Upload_S(db.Model):
    """Model for uploading files in database"""

    id=db.Column(db.Integer,primary_key=True)
    uploader_id = db.Column(db.Integer, nullable=False)
    data=db.Column(db.String(65000),nullable=False)
    created= db.Column(db.DateTime,default = dt.utcnow,nullable=False)
    admin=db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Upload_S {}>'.format(self.data[100:200])

class PlagueCheck(db.Model):
    """Model for uploading checked files in database"""

    id=db.Column(db.Integer,primary_key=True)
    checker_id = db.Column(db.Integer, nullable=False)
    checked_data = db.Column(db.String(65000),nullable=False)
    created = db.Column(db.DateTime,default = dt.utcnow,nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<PlagueCheck {}>'.format(self.data[100:200])


db.create_all()


@app.route('/', methods=['GET'])
@app.route('/home')
def hello():
    userid=session.get("userid")
    print(f'session username {userid}')
    user= User.query.filter_by(id = userid).first()
    return render_template('home.html', user = user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        formdata = request.form
        print(formdata)
        user= User.query.filter_by(email= formdata['email']).first()
        print(user.email)
        if user!= None:
            if user.password== formdata['password']:
                print("login success")
                session["userid"]= user.id
                return redirect('/home')
        print('login failed')        
    return render_template('login.html')

@app.route('/details')
def details():
    id=request.args.get('id')
    data = Upload_S.query.filter_by(id= id).first()
    
    return render_template('details.html',data=data)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        formdata = request.form

        user = User(username = formdata['username'], email=formdata['email'], password= formdata['password'], created= dt.today(), admin= False)
        print(user)
       
        db.session.add(user)
        db.session.commit()
    return render_template('register.html')


@app.route('/show')
def show():
    print(Upload_S.query.all())
    return ''



@app.route('/report')
def report():
    
    id=session.get('userid')
    user = User.query.filter_by(id = id).first()
    print(id)
    if(not id):
        return redirect('/login')

    data = Upload_S.query.filter_by(uploader_id= id)

    return render_template('report.html', data = data, user = user)





@app.route('/upload', methods=['POST', 'GET'])
def uploadFile():
    if request.method == 'POST':
        id=session.get('userid')
        if(not id):
            return redirect('/login')
        formdata= request.form
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

        if file:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

            uploadsfile = Upload_S(uploader_id = session.get('userid'), data= extract_text_from_pdf(upload_path), created= dt.today(), admin= False)

            print(uploadsfile)
            db.session.add(uploadsfile)
            db.session.commit()
           
    return render_template('uploadfile.html')


@app.route('/result')
def result():
   return render_template('results.html')


@app.route('/check')
def check():
    id=request.args.get('id')
    data = Upload_S.query.filter_by(id= id).first()
    # plagueresult = json.loads(plague.checkFullArticle(data.data))
    return render_template('check.html')
   



if __name__ == "__main__":
    app.run(debug=True)