from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy import func, desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
from werkzeug.utils import secure_filename
import random
import string
from db_setup import Base, User, Post
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import os
from flask import make_response
import requests


app = Flask(__name__)

engine = create_engine('sqlite:///hack.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()


def setCookie(user):
    response = app.make_response(redirect(url_for('main')))
    cookie_value = '%s|%s' % (user.id, user.username)
    response.set_cookie('user_id', value=cookie_value)
    return response


def check_for_user():
    cookie_value = request.cookies.get('user_id')
    print cookie_value
    if cookie_value:
        params = cookie_value.split('|')
        user = session.query(User).filter(User.username == params[1]).filter(User.id == params[0]).first()
        print user
        return user


@app.route('/')
def main():
    user = check_for_user()
    return render_template('main.html',
                           user=user)


@app.route('/newpost', methods=['GET','POST'])
def newPost():
    if request.method == 'GET':
        user = check_for_user()
        if not user:
            return redirect(url_for('login'))
        return render_template('newpost.html',
                               user=user,
                               e=None)
    else:
        print 'POST'
        title = request.form['title']
        post = request.form['post']
        user_id = request.form['user_id']
        print title,post,user_id
        if title and post and user_id:
            post = Post(title=title,
                        desc=post,
                        user_id=user_id)
            session.add(post)
            session.commit()
            return redirect(url_for('main'))
        else:
            error = "All fields are required. Do not leave any blank."
            return render_template('newpost.html',
                                   user=user,
                                   e=None,
                                   error_message=error)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        user = check_for_user()
        if user:
            return redirect(url_for('main'))
        else:
            return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        user = session.query(User).filter(User.username == username).first()
        if user.password == password:
            return setCookie(user)
        else:
            error = 'Invalid username and/or password'
            return render_template('login.html',
                                   username=username,
                                   error=error)


@app.route('/logout')
def logout():
    response = app.make_response(redirect(url_for('main')))
    cookie_value = ''
    response.set_cookie('user_id', value=cookie_value)
    return response


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        email = request.form['email']

        if username and email and password and password == verify:
            user = User(name=name,
                        email=email,
                        username=username,
                        password=password)
            session.add(user)
            session.commit()
            return redirect(url_for('main'))


@app.route('/all')
def all():
    users = session.query(User).all()
    posts = session.query(Post).all()
    return render_template('all.html',
                           users=users,
                           posts=posts)





if __name__ == '__main__':
    app.secret_key = 'something'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)