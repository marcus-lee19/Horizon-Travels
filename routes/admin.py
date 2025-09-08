from flask import Blueprint, Flask, render_template, request, session, redirect, url_for
import mysql.connector, dbfunc
from passlib.hash import sha256_crypt
from functools import wraps
import gc, re

bp = Blueprint('admin', __name__)

@bp.route('/admin')
def admin():
    if 'logged_in' in session and session.get('fname') and session.get('usertype') == 'admin':
        try:
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                print("Connected to the database")
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute("USE HORIZON_TRAVELS;")

                # Query for top customers
                try:
                    dbcursor.execute("""
                        SELECT 
                            u.fname, 
                            u.lname, 
                            SUM(
                                CASE 
                                    WHEN bs.refund_percent = 0 THEN t.seat_count
                                    WHEN bs.refund_percent = 60 THEN 0
                                    WHEN bs.refund_percent = 100 THEN 0
                                END
                            ) AS total_tickets,
                            SUM(t.price * (1 - bs.refund_percent / 100)) AS total_spent
                        FROM 
                            tickets t
                        JOIN 
                            user_accounts u ON t.user_id = u.userID
                        JOIN 
                            booking_status bs ON t.status_id = bs.status_id
                        GROUP BY 
                            u.userID
                        HAVING
                            total_spent > 0
                        ORDER BY 
                            total_spent DESC
                        LIMIT 5;
                    """)
                    top_users = dbcursor.fetchall()
                except Exception as e:
                    print(f"Error fetching top users: {e}")
                    top_users = []

                # Query for sales data for each journey
                try:
                    dbcursor.execute("""
                        SELECT 
                            f.depart AS departure,
                            f.arrive AS arrival,
                            SUM(
                                CASE 
                                    WHEN bs.refund_percent = 0 THEN t.seat_count
                                    ELSE 0
                                END
                            ) AS total_tickets_sold,
                            SUM(t.price * (1 - bs.refund_percent / 100)) AS total_sales
                        FROM 
                            tickets t
                        JOIN 
                            flight_times f ON t.flight_id = f.flight_id
                        JOIN 
                            booking_status bs ON t.status_id = bs.status_id
                        GROUP BY 
                            f.depart, f.arrive
                        HAVING
                            total_sales > 0
                        ORDER BY 
                            total_sales DESC;
                    """)
                    sales_data = dbcursor.fetchall()
                except Exception as e:
                    print(f"Error fetching sales data: {e}")
                    sales_data = []

                    # Query for refunds data for each journey
                try:
                    dbcursor.execute("""
                        SELECT 
                            f.depart AS departure,
                            f.arrive AS arrival,
                            SUM(
                                CASE 
                                    WHEN bs.refund_percent = 60 THEN t.seat_count
                                    WHEN bs.refund_percent = 100 THEN t.seat_count
                                    ELSE 0
                                END
                            ) AS total_refunded_seats,
                            SUM(
                                CASE 
                                    WHEN bs.refund_percent = 60 THEN t.price * 0.6
                                    WHEN bs.refund_percent = 100 THEN t.price
                                    ELSE 0
                                END
                            ) AS total_refunded_amount
                        FROM 
                            tickets t
                        JOIN 
                            flight_times f ON t.flight_id = f.flight_id
                        JOIN 
                            booking_status bs ON t.status_id = bs.status_id
                        GROUP BY 
                            f.depart, f.arrive
                        HAVING
                            total_refunded_amount > 0
                        ORDER BY 
                            total_refunded_amount DESC;
                    """)
                    refunds_data = dbcursor.fetchall()
                except Exception as e:
                    print(f"Error fetching refunds data: {e}")
                    refunds_data = []
                

                dbcursor.close()
                conn.close()

                return render_template(
                    'admin.html',
                    name=session['fname'],
                    top_users=top_users,
                    sales_data=sales_data,
                    refunds_data=refunds_data
                )
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('admin.html', name=session['fname'], error="Unable to fetch data.")
    else:
        return render_template('admin.html', name=None)
    
@bp.route('/flight-schedules', methods=['GET', 'POST'])
def manage_flight_schedules():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute("USE HORIZON_TRAVELS;")

                # Fetch all flight schedules
                dbcursor.execute("SELECT * FROM flight_times;")
                flight_schedules = dbcursor.fetchall()

                dbcursor.close()
                conn.close()

                return render_template(
                    'manage_flight_schedules.html',
                    flight_schedules=flight_schedules
                )
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('manage_flight_schedules.html', error="Unable to fetch flight schedules.")
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/add-flight', methods=['GET', 'POST'])
def add_flight_schedule():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute("USE HORIZON_TRAVELS;")

                if request.method == 'POST':
                    # Handle adding a new flight
                    depart = request.form['depart']
                    arrive = request.form['arrive']
                    dep_time = request.form['dep_time']
                    arr_time = request.form['arr_time']
                    price = float(request.form['price'])

                    try:
                        dbcursor.execute("""
                            INSERT INTO flight_times (depart, arrive, dep_time, arr_time, price)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (depart, arrive, dep_time, arr_time, price))
                        conn.commit()
                        message = "Flight schedule added successfully."
                        return render_template('add_flight_schedule.html', message=message)
                    except Exception as e:
                        print(f"Error adding flight schedule: {e}")
                        error = "Failed to add flight schedule."
                        return render_template('add_flight_schedule.html', error=error)

                dbcursor.close()
                conn.close()

                return render_template('add_flight_schedule.html')
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('add_flight_schedule.html', error="Unable to add flight schedule.")
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/edit-flight', methods=['POST'])
def edit_flight():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            # Retrieve flight data from the form
            flight_data = {
                'flight_id': request.form['flight_id'],
                'depart': request.form['depart'],
                'arrive': request.form['arrive'],
                'dep_time': request.form['dep_time'],
                'arr_time': request.form['arr_time'],
                'price': request.form['price']
            }

            # Render the edit flight page with pre-filled data
            return render_template('edit_flight_schedule.html', flight=flight_data)
        except Exception as e:
            print(f"An error occurred: {e}")
            return redirect(url_for('admin.manage_flight_schedules', error="Unable to load flight details."))
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/update-flight', methods=['POST'])
def update_flight():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute("USE HORIZON_TRAVELS;")

                # Get form data
                flight_id = request.form['flight_id']
                depart = request.form['depart']
                arrive = request.form['arrive']
                dep_time = request.form['dep_time']
                arr_time = request.form['arr_time']
                price = float(request.form['price'])
    

                # Update the flight details
                try:
                    dbcursor.execute("""
                        UPDATE flight_times
                        SET depart = %s, arrive = %s, dep_time = %s, arr_time = %s, original_price = %s
                        WHERE flight_id = %s
                    """, (depart, arrive, dep_time, arr_time, price, flight_id))
                    conn.commit()

                    dbcursor.execute("SELECT * FROM flight_times;")
                    flight_schedules = dbcursor.fetchall()

                    dbcursor.close()
                    conn.close()

                    # Pass success message to the template
                    return render_template(
                        'manage_flight_schedules.html',
                        flight_schedules=flight_schedules,
                        success="Flight schedule updated successfully."
                    )
                except Exception as e:
                    print(f"Error updating flight schedule: {e}")
                    return render_template('edit_flight_schedule.html', error="Failed to update flight schedule.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('edit_flight_schedule.html', error="Unable to update flight schedule.")
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/delete-flight', methods=['POST'])
def delete_flight_schedule():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor()
                dbcursor.execute("USE HORIZON_TRAVELS;")

                flight_id = request.form['flight_id']

                try:
                    dbcursor.execute("DELETE FROM flight_times WHERE flight_id = %s", (flight_id,))
                    conn.commit()
                    return redirect(url_for('admin.manage_flight_schedules', success="Flight schedule deleted successfully."))
                except Exception as e:
                    print(f"Error deleting flight schedule: {e}")
                    return redirect(url_for('admin.manage_flight_schedules', error="Failed to delete flight schedule."))
        except Exception as e:
            print(f"An error occurred: {e}")
            return redirect(url_for('admin.manage_flight_schedules', error="Unable to delete flight schedule."))
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/view-bookings', methods=['GET'])
def view_bookings():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute("USE HORIZON_TRAVELS;")

                # Fetch all bookings (tickets) with statuses
                dbcursor.execute("""
                    SELECT 
                        t.reference AS ticket_reference,
                        u.fname AS first_name,
                        u.lname AS last_name,
                        f.depart AS depart,
                        f.arrive AS arrive,
                        t.flight_date AS flight_date,
                        t.class AS flight_class,
                        t.seat_count AS seats_booked,
                        t.price AS total_price,
                        bs.status_name AS booking_status
                    FROM 
                        tickets t
                    JOIN 
                        user_accounts u ON t.user_id = u.userID
                    JOIN 
                        flight_times f ON t.flight_id = f.flight_id
                    JOIN 
                        booking_status bs ON t.status_id = bs.status_id
                    ORDER BY 
                        t.flight_date DESC;
                """)
                bookings = dbcursor.fetchall()

                dbcursor.close()
                conn.close()

                return render_template('view_bookings.html', bookings=bookings)
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('view_bookings.html', error="Unable to fetch bookings.")
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/manage-users', methods=['GET'])
def manage_users():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute("USE HORIZON_TRAVELS;")

                # Fetch all user accounts
                dbcursor.execute("""
                    SELECT userID, fname, lname, email, phnum
                    FROM user_accounts where user_type = 'standard'
                    ORDER BY fname ASC;
                """)
                users = dbcursor.fetchall()

                dbcursor.close()
                conn.close()

                if not users:
                    return render_template('manage_users.html', users=[], error="No user accounts found.")

                return render_template('manage_users.html', users=users)
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('manage_users.html', error="Unable to fetch user accounts.")
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/edit-user', methods=['POST'])
def edit_user():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            user_data = {
                'userID': request.form['userID'],
                'fname': request.form['fname'],
                'lname': request.form['lname'],
                'email': request.form['email'],
                'phnum': request.form['phnum']
            }
            return render_template('edit_user.html', user=user_data)
        except Exception as e:
            print(f"An error occurred: {e}")
            return redirect(url_for('admin.manage_users', error="Unable to load user details."))
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/update-user', methods=['POST'])
def update_user():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            # Establish database connection
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute("USE HORIZON_TRAVELS;")

                # Get form data
                user_id = request.form.get('userID')
                fname = request.form.get('fname')
                lname = request.form.get('lname')
                email = request.form.get('email')
                phnum = request.form.get('phnum')

                # Update user details in the database
                try:
                    dbcursor.execute("""
                        UPDATE user_accounts
                        SET fname = %s, lname = %s, email = %s, phnum = %s
                        WHERE userID = %s
                    """, (fname, lname, email, phnum, user_id))
                    conn.commit()

                    # Fetch updated user list
                    dbcursor.execute("""
                        SELECT userID, fname, lname, email, phnum
                        FROM user_accounts where user_type = 'standard'
                        ORDER BY fname ASC;
                    """)
                    users = dbcursor.fetchall()

                    dbcursor.close()
                    conn.close()

                    # Render the manage_users.html template with a success message
                    return render_template('manage_users.html', users=users, success="User details updated successfully.")
                except Exception as e:
                    print(f"Error updating user details: {e}")
                    # Fetch user list even if the update fails
                    dbcursor.execute("""
                        SELECT userID, fname, lname, email, phnum
                        FROM user_accounts
                        ORDER BY fname ASC;
                    """)
                    users = dbcursor.fetchall()

                    dbcursor.close()
                    conn.close()

                    # Render the manage_users.html template with an error message
                    return render_template('manage_users.html', users=users, error="Failed to update user details.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('manage_users.html', error="Unable to process the request.")
    else:
        return redirect(url_for('auth.login'))
    
@bp.route('/delete-user', methods=['POST'])
def delete_user():
    if 'logged_in' in session and session.get('usertype') == 'admin':
        try:
            conn = dbfunc.getConnection()
            if conn and conn.is_connected():
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute("USE HORIZON_TRAVELS;")

                # Get userID from the form
                user_id = request.form['userID']

                # Delete the user from the database
                try:
                    dbcursor.execute("DELETE FROM user_accounts WHERE userID = %s", (user_id,))
                    conn.commit()

                    # Fetch updated user list
                    dbcursor.execute("""
                        SELECT userID, fname, lname, email, phnum
                        FROM user_accounts
                        ORDER BY fname ASC;
                    """)
                    users = dbcursor.fetchall()

                    dbcursor.close()
                    conn.close()

                    # Render the manage_users.html template with a success message
                    return render_template('manage_users.html', users=users, success="User deleted successfully.")
                except Exception as e:
                    print(f"Error deleting user: {e}")
                    return render_template('manage_users.html', error="Failed to delete user.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('manage_users.html', error="Unable to process the request.")
    else:
        return redirect(url_for('auth.login'))
    
#Student ID : 24017967
#Student Name : Marcus Lee
#Student Email : kun2.lee@live.uwe.ac.uk