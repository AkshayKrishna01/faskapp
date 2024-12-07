from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os

app = Flask(__name__)

# Set the SECRET_KEY to enable session management
app.config['SECRET_KEY'] = os.urandom(24)  # Or replace with a manually generated secret key

# Connect to MySQL database (RDS instance)
db = pymysql.connect(
    host="database-1.cpigaywcw6ts.us-east-1.rds.amazonaws.com",
    user="admin",
    password="akshay2004.",
    database="nmdb"
)

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collect form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        try:
            with db.cursor() as cursor:
                # Check if the email already exists
                cursor.execute("SELECT email FROM usernm WHERE email = %s", (email,))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash("Account already exists. Please login!", "warning")
                    return redirect(url_for('register'))  # Stay on the same page with the error

                # If email is new, insert the user
                hashed_password = generate_password_hash(password)
                sql = "INSERT INTO usernm (first_name, last_name, email, password1) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (first_name, last_name, email, hashed_password))
                db.commit()  # Commit the transaction

                flash("Registration successful! You can now login.", "success")
                return redirect(url_for('login'))  # Redirect to login after successful registration
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            with db.cursor() as cursor:
                # Query the database for the user's password
                sql = "SELECT password1 FROM usernm WHERE email = %s"
                cursor.execute(sql, (email,))
                result = cursor.fetchone()

                if result and check_password_hash(result[0], password):
                    # Successful login
                    session['user_id'] = email  # Store user ID in session
                    return redirect(url_for('content'))
                else:
                    # Invalid credentials
                    flash("Invalid email or password. Please try again.", "danger")
        except pymysql.MySQLError as e:
            # Database error handling
            flash(f"Database error: {e}", "danger")

    return render_template('login.html')
@app.route('/content')
def content():
    return render_template('content.html')
@app.route('/dss')
def dss():
    return render_template('dss.html')

@app.route('/mdd')
def mdd():
    return render_template('mdd.html')

@app.route('/wdd')
def wdd():
    return render_template('wdd.html')


if __name__ == '__main__':
    app.run(debug=True)
