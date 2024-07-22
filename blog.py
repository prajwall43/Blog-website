from flask import Flask, render_template,request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import math

with open('config.json') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'ye-secrete-hai'

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class contacts(db.Model):
    Sr_no = db.Column(db.Integer, primary_key=True, nullable=False)
    Name = db.Column(db.String(30), unique=False, nullable=False)
    Email = db.Column(db.String(20), unique=False, nullable=False)
    Phon_no = db.Column(db.String(12), unique=True, nullable=False)
    Msg = db.Column(db.String(20), unique=True, nullable=False)
    Date = db.Column(db.String(20), unique=True, nullable=False)

class Posts(db.Model):
    Sr_no = db.Column(db.Integer, primary_key=True, nullable=False)
    Title = db.Column(db.String(30), unique=False, nullable=False)
    Slug = db.Column(db.String(20), unique=False, nullable=False)
    Content = db.Column(db.String(50), unique=True, nullable=False)
    tag_line = db.Column(db.String(50), unique=True, nullable=False)
    Date = db.Column(db.String(20), unique=True, nullable=False)
    img_file = db.Column(db.String(20), unique=True, nullable=False)
   
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))

    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']) : (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]
    if (page == 1):
        prev = '#' 
        next = "/?page=" + str(page + 1)  
    elif (page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"  
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)  
    return render_template("index.html", params=params, posts = posts, prev = prev, next= next)

@app.route("/about")
def about():
    return render_template("about.html", params=params)

@app.route("/edit/<string:Sr_no>", methods = ['GET', 'POST'])
def edit(Sr_no):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            req_title = request.form.get('Title')
            tag_line = request.form.get('tag_line')
            slug = request.form.get('Slug')
            content = request.form.get('Content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            if Sr_no == '0':
                post = Posts(Title = req_title, tag_line = tag_line, Slug = slug, Content = content, img_file = img_file, Date = date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(Sr_no = Sr_no).first()
                post.Title = req_title  
                post.tag_line  = tag_line
                post.Slug = slug
                post.Content = content
                post.img_file = img_file
                post.Date = date
                db.session.commit()
                return redirect("/edit/" + Sr_no)
        post = post = Posts.query.filter_by(Sr_no = Sr_no).first()            
        return render_template("edit.html", params = params, post = post, Sr_no = Sr_no)

@app.route("/delete/<string:Sr_no>", methods = ['GET', 'POST'])
def delete(Sr_no):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(Sr_no = Sr_no).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/")

@app.route("/dashboard", methods= ['GET', 'POST'])
def dashboard():

    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template("login.html", params=params, posts = posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_pass']):
            # set session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template("login.html", params=params, posts = posts)
    else:
        return render_template("dashboard.html", params=params)

@app.route("/post/<string:post_slug>", methods = ['GET'])
def post_route(post_slug):
    Post = Posts.query.filter_by(Slug = post_slug).first()
    return render_template("post.html", params = params, get_post = Post)

@app.route("/contact", methods = ['GET' , 'POST'])
def contact():
    if(request.method == 'POST'):
        name    = request.form.get('name')
        email   = request.form.get('email')
        phone   = request.form.get('phone')
        message = request.form.get('message')
        # contacts is classname
        entry = contacts(Name = name, Email=email, Phon_no = phone, Msg = message, Date = datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template("contact.html", params=params)

app.run(debug=True)