from flask import Blueprint, Flask, render_template, request, session, redirect, url_for
import mysql.connector, dbfunc
from passlib.hash import sha256_crypt
from functools import wraps
import gc
import re



bp = Blueprint('auth', __name__)


@bp.route('/login', methods=["GET","POST"])
def login():
    form = {}
    error = ''
    try:    
        if request.method == "POST":            
            email = request.form['email']
            password = request.form['passwd']         
            form = request.form
            print('login start 1.1')
            
            if email and password:     
                conn = dbfunc.getConnection()
                if conn != None:  # Checking if connection is None                    
                    if conn.is_connected():  # Checking if connection is established                        
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()  # Creating cursor object     
                        dbcursor.execute("USE HORIZON_TRAVELS;")                                            
                        dbcursor.execute("SELECT userID, passwd, fname, lname, phnum, user_type FROM user_accounts WHERE email = %s;", (email,))  #parameterized query to prevent SQL injection                                              
                        data = dbcursor.fetchone()

                        if dbcursor.rowcount <1:  # This means no user exists                         
                            error = "Email is not registered. Please register first."
                            return render_template("login.html", error=error)
                        else:                            
                            # Verify password hash and password received from user                                                             
                            if sha256_crypt.verify(password, str(data[1])):                                
                                session['logged_in'] = True  # Set session variables
                                session['userID'] = data[0]
                                session['user'] = email
                                session['fname'] = data[2]
                                session['lname'] = data[3]
                                session['phnum'] = data[4]
                                session['usertype'] = str(data[5])                          
                                print("You are now logged in")       
                                                         
                                if session['usertype'] == 'admin':
                                    return redirect(url_for('admin.admin'))
                                else:
                                    return redirect(url_for('main.index'))
                            else:
                                error = "Invalid email or password. Please try again."
                                return render_template("login.html", form=form, error=error)
    except Exception as e:                
        error = str(e) + "Invalid credentials, try again."
        return render_template("login.html", form=form, error=error)   
    
    return render_template("login.html", form=form, error=error)

@bp.route('/register', methods=["GET","POST"])
def register():
    error = ''
    print('Register started')
    try:
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            phnum = request.form['phnum']
            password = request.form['passwd']
            confirm_password = request.form['confirm_passwd']  # Get the confirm password field

            # Check if passwords match
            if password != confirm_password:
                error = "Passwords do not match"
                print(error)
                return render_template('register.html', error=error)
            
            # Validate first name and last name
            name_pattern = r"^[A-Za-z]+$"  # Regex to allow only alphabets
            if not re.match(name_pattern, fname):
                error = "Names can only contain alphabets"
                print(error)
                return render_template('register.html', error=error)
            if not re.match(name_pattern, lname):
                error = "Names can only contain alphabets"
                print(error)
                return render_template('register.html', error=error)

            # Validate phone number
            phone_pattern = r"^\+?[0-9]+$"  # Regex to allow only numbers and an optional leading +
            if not re.match(phone_pattern, phnum):
                error = "Phone number can only contain numbers and an optional leading +"
                print(error)
                return render_template('register.html', error=error)

            if fname and lname and email and phnum and password:
                conn = dbfunc.getConnection()
                if conn and conn.is_connected():
                    print('MySQL Connection is established')
                    dbcursor = conn.cursor()
                    password = sha256_crypt.hash(str(password))  # Hash the password
                    dbcursor.execute("USE HORIZON_TRAVELS;")
                    Verify_Query = "SELECT * FROM user_accounts WHERE email = %s"
                    dbcursor.execute(Verify_Query, (email,))
                    rows = dbcursor.fetchall()
                    userID = dbcursor.lastrowid  # Get the last inserted ID
                    if dbcursor.rowcount > 0:
                        print("Email is already registered")
                        error = "Email is already registered"
                        return render_template('register.html', error=error)
                    else:
                        dbcursor.execute(
                            "INSERT INTO user_accounts (fname, lname, email, phnum, passwd) VALUES (%s, %s, %s, %s, %s)",
                            (fname, lname, email, phnum, password)
                        )
                        conn.commit()
                        print("User registered successfully")
                        dbcursor.close()
                        conn.close()
                        gc.collect()
                        session['logged_in'] = True
                        userID = dbcursor.lastrowid
                        session['userID'] = userID
                        session['user'] = email
                        session['fname'] = fname
                        session['lname'] = lname 
                        session['phnum'] = phnum
                        session['usertype'] = 'standard'
                        return render_template('success.html')
                else:
                    print('Connection error')
                    return 'DB Connection error'
            else:
                print('Empty parameters')
                error = "All fields are required"
                return render_template('register.html', error=error)
        else:
            return render_template('register.html', error=error)

    except Exception as e:
        return render_template('register.html', error=str(e))
    
@bp.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')
    
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:            
            print("You need to login first")
            #return redirect(url_for('login', error='You need to login first'))
            return render_template('login.html', error='You need to login first')    
    return wrap

@bp.route('/userinfo')
def userinfo():
    user_info = {
        'fname': session.get('fname'),
        'lname': session.get('lname'),
        'email': session.get('user'),
        'phone': session.get('phnum'),
        'usertype': session.get('usertype')
    }
    if user_info['usertype'] == 'admin':
        return render_template('admininfo.html', user_info=user_info)
    elif user_info['usertype'] == 'standard':
        return render_template('userinfo.html', user_info=user_info)

@bp.route('/change-password', methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == 'POST':
        try:
            # Get form data
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            # Validate new password and confirmation
            if new_password == current_password:
                error = "New password cannot be the same as current password"
                print(error)
                if session.get('usertype') == 'admin':
                    return render_template('admin_change_pw.html', error=error)
                else:
                    return render_template('change_password.html', error=error)
            elif new_password != confirm_password:
                error = "New passwords do not match"
                print(error)
                if session.get('usertype') == 'admin':
                    return render_template('admin_change_pw.html', error=error)
                else:
                    return render_template('change_password.html', error=error)

            # Get the current user's email from the session
            email = session.get('user')

            # Connect to the database
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                print("MySQL Connection is established")
                dbcursor = conn.cursor()
                dbcursor.execute("USE HORIZON_TRAVELS;")

                # Fetch the current password hash from the database
                dbcursor.execute("SELECT passwd FROM user_accounts WHERE email = %s;", (email,))
                data = dbcursor.fetchone()

                if data and sha256_crypt.verify(current_password, data[0]):
                    # Hash the new password and update it in the database
                    hashed_password = sha256_crypt.hash(new_password)
                    dbcursor.execute("UPDATE user_accounts SET passwd = %s WHERE email = %s;", (hashed_password, email))
                    conn.commit()
                    print("Password updated successfully")
                    dbcursor.close()
                    conn.close()

                    # Render success page based on usertype
                    if session.get('usertype') == 'admin':
                        return render_template('admin_pw_success.html')
                    else:
                        return render_template('pw_success.html')
                else:
                    error = "Current password is incorrect"
                    print(error)
                    if session.get('usertype') == 'admin':
                        return render_template('admin_change_pw.html', error=error)
                    else:
                        return render_template('change_password.html', error=error)
            else:
                error = "Database connection error"
                print(error)
                if session.get('usertype') == 'admin':
                    return render_template('admin_change_pw.html', error=error)
                else:
                    return render_template('change_password.html', error=error)
        except Exception as e:
            error = f"An error occurred: {e}"
            print(error)
            if session.get('usertype') == 'admin':
                return render_template('admin_change_pw.html', error=error)
            else:
                return render_template('change_password.html', error=error)
    else:
        # Render the change password form based on usertype
        if session.get('usertype') == 'admin':
            return render_template('admin_change_pw.html')
        else:
            return render_template('change_password.html')

@bp.route('/logout')
@login_required
def logout():
    # Clear the session to log the user out
    session.clear()
    print("User logged out successfully")
    gc.collect()
    # Redirect to the login page with a success message
    return render_template('login.html', error="You have been logged out.")

#Student ID : 24017967
#Student Name : Marcus Lee
#Student Email : kun2.lee@live.uwe.ac.uk