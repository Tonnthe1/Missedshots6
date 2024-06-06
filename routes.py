from flask import render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Event
from .mail import send_welcome_email, send_password_update_email
from flask import current_app as app
from . import db  # Import db here to avoid circular imports
import datetime
import os
from werkzeug.utils import secure_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            response = make_response(redirect(url_for('home')))
            if remember:
                expires = datetime.datetime.now() + datetime.timedelta(days=30)
                response.set_cookie('user_id', str(user.id), expires=expires)
            return response
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Account already exists', 'error')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully', 'success')
            send_welcome_email(email, password)
            session['user_id'] = new_user.id
            response = make_response(redirect(url_for('home')))
            if remember:
                expires = datetime.datetime.now() + datetime.timedelta(days=30)
                response.set_cookie('user_id', str(new_user.id), expires=expires)
            return response
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'user_id' in session or request.cookies.get('user_id'):
        session['user_id'] = session.get('user_id') or request.cookies.get('user_id')
        return render_template('home.html')
    return redirect(url_for('index'))

@app.route('/my_events')
def my_events():
    if 'user_id' in session:
        return render_template('my_events.html')
    return redirect(url_for('index'))

@app.route('/my_account', methods=['GET', 'POST'])
def my_account():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if request.method == 'POST':
            user.email = request.form['email']
            user.phone_number = request.form['phone_number']
            user.linkedin = request.form['linkedin']
            user.facebook = request.form['facebook']
            user.twitter = request.form['twitter']
            user.github = request.form['github']
            user.phone_visible = 'phone_visible' in request.form
            user.linkedin_visible = 'linkedin_visible' in request.form
            user.facebook_visible = 'facebook_visible' in request.form
            user.twitter_visible = 'twitter_visible' in request.form
            user.github_visible = 'github_visible' in request.form

            if request.form['password']:
                new_password = request.form['password']
                if check_password_hash(user.password, new_password):
                    flash('Cannot change to the same password.', 'error')
                else:
                    user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                    send_password_update_email(user.email, new_password)
                    flash('Password updated successfully', 'success')
            db.session.commit()
            flash('Account updated successfully', 'success')
        return render_template('my_account.html', user=user)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    response = make_response(redirect(url_for('index')))
    response.set_cookie('user_id', '', expires=0)
    return response

@app.route('/search_event', methods=['GET', 'POST'])
def search_event():
    if 'user_id' in session:
        if request.method == 'POST':
            query = request.form.get('query')
            events = Event.query.filter(Event.name.contains(query) | Event.tags.contains(query)).all()
            return render_template('search_event.html', events=events)
        else:
            events = Event.query.all()  # Display all events
            return render_template('search_event.html', events=events)
    return redirect(url_for('index'))

def create_upload_folder_if_not_exists():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' in session:
        if request.method == 'POST':
            name = request.form['name']
            address = request.form['address']
            time = request.form['time']
            tags = ','.join(request.form.getlist('tags'))
            online = 'online' in request.form
            creator_id = session['user_id']

            # Handle image upload
            image_file = request.files['image']
            if image_file and image_file.filename != '':
                create_upload_folder_if_not_exists()  # Ensure upload folder exists
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                image_url = url_for('static', filename='uploads/' + filename)
            else:
                image_url = None

            new_event = Event(
                name=name, 
                address=address, 
                time=datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M'), 
                online=online, 
                creator_id=creator_id, 
                tags=tags, 
                image_url=image_url
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Event created successfully', 'success')
            return redirect(url_for('search_event'))
        return render_template('create_event.html')
    return redirect(url_for('index'))

@app.route('/event/<int:event_id>')
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('view_event.html', event=event)
