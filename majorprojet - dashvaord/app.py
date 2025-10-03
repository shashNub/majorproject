from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import csv
from scrape import scrape_and_save
import os
from werkzeug.security import generate_password_hash, check_password_hash
from organizations import ORGANIZATIONS

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

CSV_FILE = "freejobalert_latest_notifications.csv"
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.csv")

def init_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])

@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    jobs = []
    qualification = ""
    name = ""
    if request.method == "POST":
        qualification = request.form.get("qualification", "").lower()
        name = request.form.get("name", "").lower()
        scrape_and_save(CSV_FILE)
        with open(CSV_FILE, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check both qualification and name if provided
                qualification_match = not qualification or any(qualification in value.lower() for value in row.values())
                name_match = not name or (row.get('Name', '').lower() and name in row.get('Name', '').lower())
                
                if qualification_match and name_match:
                    jobs.append(row)
    return render_template("index.html", jobs=jobs, qualification=qualification, name=name, organizations=ORGANIZATIONS)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not os.path.exists(USERS_FILE):
            init_users_file()
            flash('Please register first')
            return redirect(url_for('register'))
        
        with open(USERS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username and check_password_hash(row['password'], password):
                    session['username'] = username
                    flash('Login successful!')
                    return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if not username or not password:
            flash('Username and password are required')
            return render_template("register.html")
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template("register.html")
        
        if not os.path.exists(USERS_FILE):
            init_users_file()
        
        # Check if username already exists
        with open(USERS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    flash('Username already exists')
                    return render_template("register.html")
        
        # Add new user
        with open(USERS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, generate_password_hash(password)])
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html")

@app.route("/get_job_data")
def get_job_data():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    jobs = []
    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(row)
    return jsonify(jobs)

if __name__ == "__main__":
    init_users_file()
    app.run(debug=True)