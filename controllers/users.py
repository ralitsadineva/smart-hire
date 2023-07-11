from flask import render_template, request, redirect, session
from google_service import get_google_client_id
import services.users as user_service

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #check if in database
        result = user_service.login(username, password)
        if result['success']:
            session['username'] = username
            session['user_id'] = result['user'][0]
            session['email'] = result['user'][1]
            session['avatar'] = result['user'][4]
            return redirect('/home')
        else:
            return render_template('login.html', client_id=get_google_client_id(), **result['error'])
    else:
        return render_template('login.html', client_id=get_google_client_id())

def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        #check if valid according to rules
        result = user_service.signup(email, username, password)
        if result['success']:
            return redirect('/login')
        else:
            return render_template('signup.html', client_id=get_google_client_id(), **result['error'])
    else:
        return render_template('signup.html', client_id=get_google_client_id())

def googleCallback():
    # Get authorization code Google sent back to you
    credential = request.form.get('credential')
    result = user_service.signin_google(credential)
    if result['success']:
        session['username'] = result['user'][2]
        session['user_id'] = result['user'][0]
        session['email'] = result['user'][1]
        session['avatar'] = result['user'][4]
        return redirect('/home')
    else:
        return render_template('signup.html', client_id=get_google_client_id(), **result['error'])

def logout():
    session.pop('username', None)
    return redirect('/')

def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        result = user_service.change_password(session['user_id'], old_password, new_password)
        if result['success']:
            session.pop('username', None)
            return redirect('/login')
        else:
            return render_template('change_password.html', **result['error'], avatar=session['avatar'])
    else:
        return render_template('change_password.html', avatar=session['avatar'])

def home():
    parameters = user_service.get_home(session['user_id'])
    return render_template('home.html', **parameters, avatar=session['avatar'])

def profile():
    if request.method == 'POST':
        avatar = request.files['avatar']
        result = user_service.update_avatar(session['user_id'], avatar)
        if result['success']:
            session['avatar'] = result['avatar']
            return redirect('/profile')
        else:
            return render_template('profile.html', **result['error'], username=session['username'], email=session['email'], avatar=session['avatar'])
        
    else:
        return render_template('profile.html', username=session['username'], email=session['email'], avatar=session['avatar'])
