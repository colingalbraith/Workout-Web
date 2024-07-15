from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a random secret key

users_file = 'users.json'

def load_users():
    if not os.path.exists(users_file):
        return {}
    with open(users_file, 'r') as file:
        return json.load(file)

def save_users(users):
    with open(users_file, 'w') as file:
        json.dump(users, file)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users and users[email]['password'] == password:
            session['user'] = email
            today = datetime.today()
            return redirect(url_for('calendar', year=today.year, month=today.month))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email not in users:
            users[email] = {'password': password, 'workouts': {}}
            save_users(users)
            return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/calendar/<int:year>/<int:month>')
def calendar(year, month):
    if 'user' not in session:
        return redirect(url_for('index'))

    users = load_users()
    email = session['user']
    workouts = users[email]['workouts']

    days = month_days(year, month)
    prev_month = (datetime(year, month, 1) - timedelta(days=1)).replace(day=1)
    next_month = (datetime(year, month, 28) + timedelta(days=4)).replace(day=1)

    today = datetime.today().date()
    workout_data = {day.strftime('%Y-%m-%d'): workouts.get(day.strftime('%Y-%m-%d'), []) for day in days if day}

    return render_template('calendar.html', days=days, year=year, month=month, prev_month=prev_month, next_month=next_month, today=today, workouts=workout_data)
    
@app.route('/workout/<date>', methods=['GET', 'POST'])
def workout(date):
    if 'user' not in session:
        return redirect(url_for('index'))

    users = load_users()
    email = session['user']
    if date not in users[email]['workouts']:
        users[email]['workouts'][date] = []

    workouts = users[email]['workouts'][date]

    if request.method == 'POST':
        if request.form['action'] == 'Add Set':
            body_part = request.form['body_part']
            exercise = request.form['exercise']
            weight = request.form['weight']
            reps = request.form['reps']
            notes = request.form['notes']

            new_workout = {
                'body_part': body_part,
                'exercise': exercise,
                'weight': weight,
                'reps': reps,
                'notes': notes
            }

            workouts.append(new_workout)
            save_users(users)

        elif request.form['action'] == 'Delete':
            selected_sets = request.form.getlist('selected_sets')
            for index in sorted(selected_sets, reverse=True):
                del workouts[int(index)]
            save_users(users)

        return redirect(url_for('workout', date=date))

    last_body_part = request.form.get('last_body_part', '')
    last_exercise = request.form.get('last_exercise', '')

    return render_template('workout.html', date=date, workouts=workouts, last_body_part=last_body_part, last_exercise=last_exercise)


def month_days(year, month):
    first_day = datetime(year, month, 1)
    next_month = first_day.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    
    # Days of the current month
    current_month_days = [(first_day + timedelta(days=i)).date() for i in range((last_day - first_day).days + 1)]
    
    # Calculate padding for the first week
    start_padding = [None] * ((first_day.weekday() + 1) % 7)
    
    # Combine the padding and current month days
    days = start_padding + current_month_days
    
    # Add None to fill the last week if necessary
    while len(days) % 7 != 0:
        days.append(None)
    
    return days

if __name__ == '__main__':
    app.run(debug=True)
