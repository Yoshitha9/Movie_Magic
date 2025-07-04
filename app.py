from flask import Flask, render_template, request, redirect, url_for, session
import boto3
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key

# AWS Configuration
aws_region = 'us-east-1'
sns_topic_arn = 'arn:aws:sns:us-east-1:577638351818:movies'

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name=aws_region)
sns = boto3.client('sns', region_name=aws_region)

# DynamoDB Tables
users_table = dynamodb.Table('Users')
bookings_table = dynamodb.Table('Bookings')

# Movie list hardcoded
sample_movies = [
    {
        "id": 1,
        "title": "GENTELMEN",
        "language": "Telugu",
        "poster_url": "static/images/gentelmen.jpg",
        "showtimes": ["11:00 AM", "2:00 PM", "5:00 PM"]
    },
    {
        "id": 2,
        "title": "MAZAKA",
        "language": "Telugu",
        "poster_url": "static/images/mazaka.jpeg",
        "showtimes": ["10:30 AM", "1:30 PM", "4:30 PM"]
    },
    {
        "id": 3,
        "title": "MUNNA",
        "language": "Telugu",
        "poster_url": "static/images/munna.jpg",
        "showtimes": ["11:30 AM", "2:30 PM", "6:30 PM"]
    },
    {
        "id": 4,
        "title": "AKASHAM LO OKA THARA",
        "language": "Telugu",
        "poster_url": "static/images/akashamlookathara.jpeg",
        "showtimes": ["10:00 AM", "1:00 PM", "4:00 PM"]
    },
    {
        "id": 5,
        "title": "BUSINESSMAN",
        "language": "Telugu",
        "poster_url": "static/images/businessman.jpeg",
        "showtimes": ["12:00 PM", "3:00 PM", "6:00 PM"]
    },
    {
        "id": 6,
        "title": "COURT: STATE VS A NOBODY",
        "language": "Telugu",
        "poster_url": "static/images/Court_-_State_Vs_A_Nobody.jpg",
        "showtimes": ["2:00 PM", "5:00 PM", "8:00 PM"]
    }
]

# SNS email notification
def send_booking_email(email, movie, showtime, seat, booking_id):
    message = f"""
🎟 Booking Confirmed!

Movie: {movie}
Time: {showtime}
Seat(s): {seat}
Booking ID: {booking_id}

Thank you for booking with us!
"""
    try:
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="Your Movie Ticket Booking Confirmation"
        )
    except Exception as e:
        print("SNS Error:", e)

# Routes
@app.route('/')
def landing():
    return render_template("landing.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = users_table.get_item(Key={'email': email})
        if 'Item' in existing_user:
            return "⚠️ Account with this email already exists. Please sign in."

        users_table.put_item(Item={
            'email': email,
            'username': username,
            'password': password
        })
        return redirect(url_for('signin'))
    return render_template("signup.html")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_table.get_item(Key={'email': email}).get('Item')
        if user and user['password'] == password:
            session['email'] = email
            return redirect(url_for('index'))
        else:
            return "Invalid email or password"
    return render_template("signin.html")

@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/movies')
def movies():
    return render_template("movies.html", movies=sample_movies)

@app.route('/book/<int:movie_id>/<showtime>', methods=['GET', 'POST'])
def book(movie_id, showtime):
    movie = next((m for m in sample_movies if m["id"] == movie_id), None)
    if not movie:
        return "❌ Movie not found."

    if request.method == 'POST':
        seat_input = request.form['seat']
        seat_list = [s.strip() for s in seat_input.split(',') if s.strip()]
        num_tickets = len(seat_list)
        ticket_price = 150
        total = num_tickets * ticket_price
        booking_id = str(uuid.uuid4())

        email = session.get('email', 'guest@example.com')  # Fallback

        bookings_table.put_item(Item={
            'email': email,
            'booking_id': booking_id,
            'movie_id': movie_id,
            'movie_title': movie['title'],
            'showtime': showtime,
            'seats': seat_list,
            'num_tickets': num_tickets,
            'price_per_ticket': ticket_price,
            'total_amount': total
        })

        send_booking_email(email, movie['title'], showtime, seat_input, booking_id)

        return render_template(
            "confirmation.html",
            movie=movie,
            showtime=showtime,
            seat=seat_input,
            ticket_price=ticket_price,
            total=total,
            num_tickets=num_tickets
        )

    return render_template("book.html", movie_id=movie_id, showtime=showtime)

@app.route('/mybookings')
def mybookings():
    email = session.get('email')
    if not email:
        return "Please log in to view your bookings."

    response = bookings_table.scan()
    all_bookings = response.get('Items', [])
    user_bookings = [b for b in all_bookings if b['email'] == email]

    return render_template("mybookings.html", bookings=user_bookings)

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
