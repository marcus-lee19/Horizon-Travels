import mysql.connector, dbfunc
from flask import Blueprint, render_template, request, session, redirect 
from routes.auth import login_required
from datetime import datetime, timedelta
import random

DB_NAME = 'HORIZON_TRAVELS'
bp = Blueprint('bookings', __name__)

@bp.route('/bookings')
def bookings():
    # Render the bookings page with departure and arrival locations.
    conn = dbfunc.getConnection()
    if conn is not None and conn.is_connected():
        print('MySQL Connection is established')
        dbcursor = conn.cursor()
        dbcursor.execute("USE {};".format(DB_NAME))
        
        # Query for distinct departure locations
        dbcursor.execute("SELECT DISTINCT depart FROM flight_times;")
        departures = [row[0] for row in dbcursor.fetchall()]  # Extract departure locations into a list
        
        # Query for distinct arrival locations
        dbcursor.execute("SELECT DISTINCT arrive FROM flight_times;")
        arrivals = [row[0] for row in dbcursor.fetchall()]  # Extract arrival locations into a list
        
        dbcursor.close()
        conn.close()
        
        selected_arrival = request.args.get('arrival', '')  # Get the selected arrival location from query parameters
        # Pass departures and arrivals to the template
        return render_template('bookings.html', departures=departures, arrivals=arrivals, selected_arrival=selected_arrival)
    else:
        print('DB connection error')
        return 'DB connection error'

@bp.route('/flight-times')
def flight_times():
    # Display all available flight schedules.
    SELECT_statement = "SELECT depart, dep_time, arrive, arr_time, original_price FROM flight_times"
    conn = dbfunc.getConnection()
    if conn != None:
        print('MySQL Connection is established')
        dbcursor = conn.cursor()
        dbcursor.execute("USE {};".format(DB_NAME))
        dbcursor.execute(SELECT_statement)
        print("Database {} executed successfully." .format(SELECT_statement))
        rows = dbcursor.fetchall()  # Fetch all rows from the query result
        print("Total rows: ", dbcursor.rowcount)
        dbcursor.close()
        conn.close()
        return render_template('flight-times.html', resultset = rows)  # Pass the result set to the template
    else:
        print('DB connection error')
        return 'DB connection error'
    
@bp.route('/search-flights', methods=['POST'])
def search_flights():
    # Search for flights based on user input.
    try:
        # Get form data
        departure = request.form['departure']  # Departure location selected by the user
        arrival = request.form['arrival']  # Arrival location selected by the user
        flight_class = request.form['class']  # Flight class (Economy or Business)

        # Connect to the database
        conn = dbfunc.getConnection()
        if conn is not None and conn.is_connected():
            print("MySQL Connection is established")
            dbcursor = conn.cursor()
            dbcursor.execute("USE {};".format(DB_NAME))

            # Query flights based on departure and arrival
            query = """
                SELECT flight_id, depart, dep_time, arrive, arr_time, original_price
                FROM flight_times
                WHERE depart = %s AND arrive = %s;
            """
            dbcursor.execute(query, (departure, arrival))  # Use parameterized query to prevent SQL injection
            flights = dbcursor.fetchall()

            # Adjust prices for business class
            results = []
            for flight in flights:
                base_price = flight[5]  # Base price of the flight
                adjusted_price = base_price * 2 if flight_class == 'Business' else flight[5]  # Double the price for Business class
                results.append({
                    'flight_id': flight[0],
                    'depart': flight[1],
                    'dep_time': flight[2],
                    'arrive': flight[3],
                    'arr_time': flight[4],
                    'price': adjusted_price
                })

            dbcursor.close()
            conn.close()

            # Pass data to the search results page
            return render_template('search_results.html', flights=results, flight_class=flight_class)
        else:
            error = "Database connection error"
            print(error)
            return render_template('bookings.html', error=error)
    except Exception as e:
        error = f"An error occurred: {e}"
        print(error)
        return render_template('bookings.html', error=error)
    
@bp.route('/select-flight', methods=['POST'])
@login_required
def select_flight_date():
    # Allow users to select a flight date.
    try:
        # Get selected flight details from the form
        flight_id = request.form['flight_id']
        flight_class = request.form['flight_class']

        conn = dbfunc.getConnection()
        dbcursor = conn.cursor(dictionary=True)
        dbcursor.execute("USE {};".format(DB_NAME))
        query = "SELECT * FROM flight_times WHERE flight_id = %s"
        dbcursor.execute(query, (flight_id,))
        flight = dbcursor.fetchone()

        base_price = float(flight['original_price'])  # Ensure price is treated as a float
        adjusted_price = base_price * 2 if flight_class.lower() == 'business' else base_price
        flight['price'] = adjusted_price  # Update the price in the flight dictionary

        current_date = datetime.now().strftime('%Y-%m-%d')
        max_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')

        dbcursor.close()
        conn.close()
        return render_template('select_flight_date.html', flight=flight, flight_class=flight_class, current_date=current_date, max_date=max_date, total_price=adjusted_price)
    except Exception as e:
        error = f"An error occurred: {e}"
        print(error)
        return render_template('bookings.html', error=error)
    
@bp.route('/confirm-booking', methods=['POST'])
@login_required
def confirm_booking():
    # Confirm the booking and calculate discounts.
    try:
        # Get flight_id and other details from the form
        flight_id = request.form['flight_id']
        flight_date = request.form['flight_date']
        num_seats = int(request.form['num_seats'])
        flight_class = request.form['flight_class']

        # Define seat limits
        SEAT_LIMITS = {
            'business': 26,
            'economy': 104
        }

        # Query the database for flight details
        conn = dbfunc.getConnection()
        dbcursor = conn.cursor(dictionary=True)
        dbcursor.execute("USE {};".format(DB_NAME))
        query = "SELECT * FROM flight_times WHERE flight_id = %s"
        dbcursor.execute(query, (flight_id,))
        flight = dbcursor.fetchone()

        # Calculate total price
        price_per_seat = float(flight['original_price'])
        if flight_class.lower() == 'business':
            price_per_seat *= 2
        total_price = num_seats * price_per_seat

        # Calculate the number of days between the current date and the flight date
        current_date = datetime.now().date()
        max_date = (datetime.now() + timedelta(days=90)).date()
        flight_date_obj = datetime.strptime(flight_date, '%Y-%m-%d').date()
        days_difference = (flight_date_obj - current_date).days

        # Apply discount based on the number of days
        discount_percentage = 0
        if 80 <= days_difference <= 90:
            discount_percentage = 25
        elif 60 <= days_difference <= 79:
            discount_percentage = 15
        elif 45 <= days_difference <= 59:
            discount_percentage = 10

        discount_amount = (total_price * discount_percentage) / 100
        discounted_total_price = total_price - discount_amount

                # Check seat availability
        seat_limit = SEAT_LIMITS[flight_class.lower()]
        seat_query = """
            SELECT SUM(seat_count) AS booked_seats
            FROM tickets
            WHERE flight_id = %s AND class = %s AND flight_date = %s AND status_id = 1
        """
        flight_date = request.form.get('flight_date')
        dbcursor.execute(seat_query, (flight_id, flight_class, flight_date))
        result = dbcursor.fetchone()
        booked_seats = result['booked_seats'] or 0  # Default to 0 if no seats are booked
        available_seats = seat_limit - booked_seats

        if flight_date_obj.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
            error = "Flights operate Mondays to Fridays only."
            return render_template(
                'select_flight_date.html',
                flight=flight, 
                flight_class=flight_class, 
                current_date=current_date.strftime('%Y-%m-%d'),
                max_date=max_date.strftime('%Y-%m-%d'),
                total_price=price_per_seat,
                error=error
            )
        elif available_seats <= 0:
            # No seats available
            error = f"No {flight_class.lower()} seats available for {flight_date}. Please choose another date."
            dbcursor.close()
            conn.close()
            return render_template(
                'select_flight_date.html', 
                flight=flight, 
                flight_class=flight_class, 
                current_date=current_date.strftime('%Y-%m-%d'),
                max_date=max_date.strftime('%Y-%m-%d'),
                total_price=price_per_seat,
                error=error
                )
        elif num_seats > available_seats:
            # Not enough seats available
            error = f"Only {available_seats} {flight_class.lower()} seat(s) are available for {flight_date}. Please adjust your booking."
            dbcursor.close()
            conn.close()
            return render_template(
                'select_flight_date.html',
                flight=flight,
                flight_class=flight_class,
                flight_date=flight_date,
                current_date=current_date.strftime('%Y-%m-%d'),
                max_date=max_date.strftime('%Y-%m-%d'),
                total_price=price_per_seat,
                error=error
            )

        dbcursor.close()
        conn.close()

        # Pass data to the confirmation page
        return render_template(
            'confirm_booking.html',
            flight=flight,
            flight_date=flight_date,
            num_seats=num_seats,
            total_price=total_price,
            discounted_total_price=discounted_total_price,
            discount_percentage=discount_percentage,
            flight_class=flight_class
        )
    except Exception as e:
        error = f"An error occurred: {e}"
        print(error)
        return render_template('bookings.html', error=error)
    
@bp.route('/booking-success', methods=['POST'])
@login_required
def booking_success():
    # Save booking details and display success page.
    try:
        # Get booking details from the form
        flight_id = request.form['flight_id']
        flight_date = request.form['flight_date']
        num_seats = int(request.form['num_seats'])
        flight_class = request.form['flight_class']
        total_price = float(request.form['total_price'])
        user_id = session['userID']  # Assuming user_id is stored in the session

        # Query the database for flight details
        conn = dbfunc.getConnection()
        dbcursor = conn.cursor(dictionary=True)
        dbcursor.execute("USE {};".format(DB_NAME))
        query = "SELECT * FROM flight_times WHERE flight_id = %s"
        dbcursor.execute(query, (flight_id,))
        flight = dbcursor.fetchone()

        # Calculate total price
        price_per_seat = float(flight['original_price'])
        if flight_class.lower() == 'business':
            price_per_seat *= 2  # Double the price for business class
        total_price = num_seats * price_per_seat

        current_date = datetime.now().date()
        flight_date_obj = datetime.strptime(flight_date, '%Y-%m-%d').date()
        days_difference = (flight_date_obj - current_date).days

        # Apply discount based on the number of days
        discount_percentage = 0
        if 80 <= days_difference <= 90:
            discount_percentage = 25
        elif 60 <= days_difference <= 79:
            discount_percentage = 15
        elif 45 <= days_difference <= 59:
            discount_percentage = 10

        discount_amount = (total_price * discount_percentage) / 100
        discounted_total_price = total_price - discount_amount

        # Generate a random 8-digit reference number
        reference_number = ''.join([str(random.randint(0, 9)) for _ in range(8)])

        # Save the ticket to the database
        ticket_query = """
            INSERT INTO tickets (flight_id, user_id, reference, class, seat_count, price, flight_date, booking_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        dbcursor.execute(ticket_query, (
            flight_id,
            user_id,
            reference_number,
            flight_class,
            num_seats,
            discounted_total_price,
            flight_date,
            current_date
        ))
        conn.commit()

        dbcursor.close()
        conn.close()

        # Render the success page with ticket details
        return render_template(
            'ticket_success.html',
            reference_number=reference_number,
            flight=flight,
            flight_date=flight_date,
            num_seats=num_seats,
            total_price=total_price,
            discounted_total_price=discounted_total_price,
            discount_percentage=discount_percentage,
            flight_class=flight_class,
            booking_date=current_date
        )
    except Exception as e:
        error = f"An error occurred: {e}"
        print(error)
        return render_template('bookings.html', error=error)
    

    
@bp.route('/tickets')
@login_required
def tickets():
    # Display all active tickets for the user.
    try:
        user_id = session['userID']  # Assuming user_id is stored in the session

        # Query the database for tickets and join with flight_times to get flight details
        conn = dbfunc.getConnection()
        dbcursor = conn.cursor(dictionary=True)
        dbcursor.execute("USE {};".format(DB_NAME))
        query = """
            SELECT t.reference, t.class, t.seat_count, t.price, t.flight_date, t.booking_date, 
                   f.depart, f.dep_time, f.arrive, f.arr_time, bs.status_name
            FROM tickets t
            JOIN flight_times f ON t.flight_id = f.flight_id
            JOIN booking_status bs ON t.status_id = bs.status_id
            WHERE t.user_id = %s AND t.status_id = 1
        """
        dbcursor.execute(query, (user_id,))
        tickets = dbcursor.fetchall()

        # Automatically mark tickets as 'Used' if the flight date has passed
        current_date = datetime.now().date()
        for ticket in tickets:
            flight_date = ticket['flight_date']
            booking_date = ticket['booking_date']
            days_difference = (flight_date - booking_date).days

            # Apply discount logic
            discount_percentage = 0
            if 80 <= days_difference <= 90:
                discount_percentage = 25
            elif 60 <= days_difference <= 79:
                discount_percentage = 15
            elif 45 <= days_difference <= 59:
                discount_percentage = 10


            # Add discount details to the ticket
            ticket['discount_percentage'] = discount_percentage

            if flight_date < current_date:
                update_query = "UPDATE tickets SET status_id = 2 WHERE reference = %s"
                dbcursor.execute(update_query, (ticket['reference'],))
                conn.commit()

        dbcursor.close()
        conn.close()

        return render_template('tickets.html', tickets=tickets, current_date=current_date.strftime('%Y-%m-%d'))
    except Exception as e:
        error = f"An error occurred: {e}"
        print(error)
        return render_template('bookings.html', error=error)
    
@bp.route('/cancel-ticket', methods=['POST'])
@login_required
def cancel_ticket():
    # Handle ticket cancellation and refunds.
    try:
        # Get the reference number of the ticket to cancel
        reference = request.form['reference']
        user_id = session['userID']  # Ensure the user is logged in

        # Connect to the database
        conn = dbfunc.getConnection()
        dbcursor = conn.cursor(dictionary=True)
        dbcursor.execute("USE {};".format(DB_NAME))

        # Query the ticket details
        query = """
            SELECT t.flight_date, t.price, t.status_id
            FROM tickets t
            WHERE t.reference = %s AND t.user_id = %s
        """
        dbcursor.execute(query, (reference, user_id))
        ticket = dbcursor.fetchone()

        if not ticket:
            error = "Ticket not found."
            dbcursor.close()
            conn.close()
            return render_template('tickets.html', error=error)

        # Calculate the cancellation status based on the flight date
        flight_date = ticket['flight_date']
        current_date = datetime.now().date()
        days_difference = (flight_date - current_date).days

        if days_difference > 60:
            # Fully refunded
            new_status_id = 5  # Fully Refunded
        elif 30 <= days_difference <= 60:
            # Partially refunded
            new_status_id = 4  # Partially Refunded
        elif days_difference < 30:
            # Cancelled
            new_status_id = 3  # Cancelled
        else:
            error = "Invalid cancellation request."
            dbcursor.close()
            conn.close()
            return render_template('tickets.html', error=error)

        # Update the ticket status
        update_query = "UPDATE tickets SET status_id = %s WHERE reference = %s AND user_id = %s"
        dbcursor.execute(update_query, (new_status_id, reference, user_id))
        conn.commit()

        dbcursor.close()
        conn.close()

        # Redirect back to the tickets page
        return redirect('/tickets')
    except Exception as e:
        error = f"An error occurred: {e}"
        print(error)
        return render_template('/tickets', error=error)
    
@bp.route('/change-date', methods=['POST'])
@login_required
def change_date_page():
    # Render the page to change the flight date.
    try:
        reference = request.form['reference']
        user_id = session['userID']

        # Connect to the database
        conn = dbfunc.getConnection()
        dbcursor = conn.cursor(dictionary=True)
        dbcursor.execute("USE {};".format(DB_NAME))

        # Query the ticket details
        query = """
            SELECT t.reference, t.flight_date, t.class, t.seat_count, t.price, t.booking_date,
                   f.depart, f.dep_time, f.arrive, f.arr_time
            FROM tickets t
            JOIN flight_times f ON t.flight_id = f.flight_id
            WHERE t.reference = %s AND t.user_id = %s
        """
        dbcursor.execute(query, (reference, user_id))
        ticket = dbcursor.fetchone()

        # Calculate valid date range based on discount percentage
        booking_date = ticket['booking_date']
        current_date = datetime.now().date()

        # Calculate the number of days between the booking date and the flight date
        days_difference = (ticket['flight_date'] - booking_date).days

        # Dynamically calculate the discount percentage
        discount_percentage = 0
        if 80 <= days_difference <= 90:
            discount_percentage = 25
        elif 60 <= days_difference <= 79:
            discount_percentage = 15
        elif 45 <= days_difference <= 59:
            discount_percentage = 10

        if discount_percentage == 25:
            min_date = booking_date + timedelta(days=80)
            max_date = booking_date + timedelta(days=90)
        elif discount_percentage == 15:
            min_date = booking_date + timedelta(days=60)
            max_date = booking_date + timedelta(days=90)
        elif discount_percentage == 10:
            min_date = booking_date + timedelta(days=45)
            max_date = booking_date + timedelta(days=90)
        else:
            min_date = booking_date
            max_date = booking_date + timedelta(days=90)

        # Get today's date in the format YYYY-MM-DD
        current_date = datetime.now().strftime('%Y-%m-%d')

        dbcursor.close()
        conn.close()

        return render_template('change_date.html', ticket=ticket, current_date=current_date,min_date=min_date.strftime('%Y-%m-%d'),
            max_date=max_date.strftime('%Y-%m-%d'))
    except Exception as e:
        error = f"An error occurred: {e}"
        print(error)
        return render_template('change_date.html', error=error)
    
@bp.route('/update-date', methods=['POST'])
@login_required
def update_date():
    # Update the flight date for a ticket.
    try:
        # Get the reference number and new flight date from the form
        reference = request.form['reference']
        new_date = request.form['new_date']
        user_id = session['userID']  # Ensure the user is logged in

        # Define seat limits
        SEAT_LIMITS = {
            'business': 26,
            'economy': 104
        }

        # Connect to the database
        conn = dbfunc.getConnection()
        dbcursor = conn.cursor(dictionary=True)
        dbcursor.execute("USE {};".format(DB_NAME))

        # Query the ticket details
        ticket_query = """
            SELECT t.reference, t.flight_date, t.booking_date, t.flight_id, t.class, t.seat_count, f.depart, f.arrive
            FROM tickets t
            JOIN flight_times f ON t.flight_id = f.flight_id
            WHERE t.reference = %s AND t.user_id = %s
        """
        dbcursor.execute(ticket_query, (reference, user_id))
        ticket = dbcursor.fetchone()

        if not ticket:
            error = "Ticket not found."
            dbcursor.close()
            conn.close()
            return render_template('change_date.html', error=error)

        flight_id = ticket['flight_id']
        flight_class = ticket['class']
        num_seats = ticket['seat_count']
        current_flight_date = ticket['flight_date']
        

        # Check seat availability for the new date
        seat_limit = SEAT_LIMITS[flight_class.lower()]
        seat_query = """
            SELECT SUM(seat_count) AS booked_seats
            FROM tickets
            WHERE flight_id = %s AND class = %s AND flight_date = %s AND status_id = 1
        """
        dbcursor.execute(seat_query, (flight_id, flight_class, new_date))
        result = dbcursor.fetchone()
        booked_seats = result['booked_seats'] or 0  # Default to 0 if no seats are booked
        available_seats = seat_limit - booked_seats

        new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
        # Calculate valid date range based on discount percentage
        booking_date = ticket['booking_date']

        # Dynamically calculate the discount percentage
        days_difference = (new_date_obj - booking_date).days
        discount_percentage = 0
        if 80 <= days_difference <= 90:
            discount_percentage = 25
        elif 60 <= days_difference <= 79:
            discount_percentage = 15
        elif 45 <= days_difference <= 59:
            discount_percentage = 10

        if discount_percentage == 25:
            min_date = booking_date + timedelta(days=80)
            max_date = booking_date + timedelta(days=90)
        elif discount_percentage == 15:
            min_date = booking_date + timedelta(days=60)
            max_date = booking_date + timedelta(days=90)
        elif discount_percentage == 10:
            min_date = booking_date + timedelta(days=45)
            max_date = booking_date + timedelta(days=90)
        else:
            min_date = booking_date
            max_date = booking_date + timedelta(days=90)

        # Get today's date in the format YYYY-MM-DD
        current_date = datetime.now().strftime('%Y-%m-%d')

         # Check if the new date is the same as the current flight date
        if str(new_date) == str(current_flight_date):
            error = "The new flight date cannot be the same as the current flight date. Please choose a different date."
            dbcursor.close()
            conn.close()
            return render_template('change_date.html', ticket=ticket,current_date=current_date,min_date=min_date.strftime('%Y-%m-%d'),
            max_date=max_date.strftime('%Y-%m-%d'), error=error)
        elif new_date_obj.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
            error = "Flights operate Mondays to Fridays only. Please select a valid weekday."
            dbcursor.close()
            conn.close()
            return render_template('change_date.html', ticket=ticket,current_date=current_date,min_date=min_date.strftime('%Y-%m-%d'),
            max_date=max_date.strftime('%Y-%m-%d'), error=error)
        elif available_seats <= 0:
            # No seats available
            error = f"No {flight_class.lower()} seats are available for {new_date}. Please select another date."
            dbcursor.close()
            conn.close()
            return render_template('change_date.html', ticket=ticket,current_date=current_date,min_date=min_date.strftime('%Y-%m-%d'),
            max_date=max_date.strftime('%Y-%m-%d'), error=error)
        elif num_seats > available_seats:
            # Not enough seats available
            error = f"Only {available_seats} {flight_class.lower()} seat(s) are available for {new_date}. Please select another date."
            dbcursor.close()
            conn.close()
            return render_template('change_date.html', ticket=ticket,current_date=current_date,min_date=min_date.strftime('%Y-%m-%d'),
            max_date=max_date.strftime('%Y-%m-%d'), error=error)

        # Update the flight date in the database
        update_query = """
            UPDATE tickets
            SET flight_date = %s
            WHERE reference = %s AND user_id = %s
        """
        dbcursor.execute(update_query, (new_date, reference, user_id))
        conn.commit()

        # Query the updated ticket details
        query = """
            SELECT t.reference, t.flight_date, t.class, t.seat_count, t.price,
                   f.depart, f.dep_time, f.arrive, f.arr_time
            FROM tickets t
            JOIN flight_times f ON t.flight_id = f.flight_id
            WHERE t.reference = %s AND t.user_id = %s
        """
        dbcursor.execute(query, (reference, user_id))
        updated_ticket = dbcursor.fetchone()

        dbcursor.close()
        conn.close()

        return render_template('date_change_success.html', ticket=updated_ticket,discount_percentage=discount_percentage)
    except Exception as e:
        error = f"An error occurred: {e}"
        print(error)
        return render_template('change_date.html', error=error)
    
#Student ID : 24017967
#Student Name : Marcus Lee
#Student Email : kun2.lee@live.uwe.ac.uk