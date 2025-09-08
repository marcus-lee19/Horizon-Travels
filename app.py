from flask import Flask
from routes import main, auth, bookings, admin
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Register blueprints
app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(bookings.bp)
app.register_blueprint(admin.bp)

if __name__ == '__main__':
    app.run(debug=True)

#Student ID : 24017967
#Student Name : Marcus Lee
#Student Email : kun2.lee@live.uwe.ac.uk