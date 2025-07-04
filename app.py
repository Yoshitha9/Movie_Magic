from flask import Flask, render_template, request, redirect, url_for
import boto3
import uuid

app = Flask(__name__)

# AWS Configuration
aws_region = 'us-east-1'  # Replace with your region
sns_topic_arn = 'arn:aws:sns:us-east-1:577638351818:movies'  # Replace with your SNS Topic

# Initialize AWS Services
dynamodb = boto3.resource('dynamodb', region_name=aws_region)
sns = boto3.client('sns', region_name=aws_region)

# DynamoDB Tables
users_table = dynamodb.Table('Users')
movies_table = dynamodb.Table('Movies')
bookings_table = dynamodb.Table('Bookings')


sample_movies = [
    {
        "id": 1,
        "title": "GENTELMEN",
        "language": "Telugu",
        "poster_url": "/static/gentelmen.jpg",
        "showtimes": ["11:00 AM", "2:00 PM", "5:00 PM"]
    },
    {
        "id": 2,
        "title": "MAZAKA",
        "language": "Telugu",
        "poster_url": "/static/mazaka.jpeg",
        "showtimes": ["10:30 AM", "1:30 PM", "4:30 PM"]
    },
    {
        "id": 3,
        "title": "MUNNA",
        "language": "Telugu",
        "poster_url": "/static/munna.jpg",
        "showtimes": ["11:30 AM", "2:30 PM", "6:30 PM"]
    },
    {
        "id": 4,
        "title": "AKASHAM LO OKA THARA",
        "language": "Telugu",
        "poster_url": "/static/akashamlookathara.jpeg",
        "showtimes": ["10:00 AM", "1:00 PM", "4:00 PM"]
    },
    {
        "id": 5,
        "title": "BUSINESSMAN",
        "language": "Telugu",
        "poster_url": "/static/businessman.jpeg",
        "showtimes": ["12:00 PM", "3:00 PM", "6:00 PM"]
    },
    {
        "id": 6,
        "title": "COURT: STATE VS A NOBODY",
        "language": "Telugu",
        "poster_url": "/static/Court_-_State_Vs_A_Nobody.jpg",
        "showtimes": ["2:00 PM", "5:00 PM", "8:00 PM"]
    }
]



# Send Booking Confirmation via SNS
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
        print(f"❌ SNS publish failed: {e}")

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
            return "⚠️ Account with this email already exists. Please sign in or use a different email."

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

        response = users_table.get_item(Key={'email': email})
        user = response.get('Item')

        if user and user['password'] == password:
            return redirect(url_for('index'))
        else:
            return "Invalid email or password"
    return render_template("signin.html")

@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/movies')
def movies():
    response = movies_table.scan()
    movies = response.get('Items', [])
    return render_template("movies.html", movies=movies)

@app.route('/book/<int:movie_id>/<showtime>', methods=['GET', 'POST'])
def book(movie_id, showtime):
    if request.method == 'POST':
        seat_input = request.form['seat']
        seat_list = [s.strip() for s in seat_input.split(',') if s.strip()]
        num_tickets = len(seat_list)
        ticket_price = 150
        total = num_tickets * ticket_price

        movie_response = movies_table.get_item(Key={'id': movie_id})
        movie = movie_response.get('Item')
        if not movie:
            return "❌ Movie not found."

        booking_id = str(uuid.uuid4())

        bookings_table.put_item(Item={
            'booking_id': booking_id,
            'movie_id': movie_id,
            'movie_title': movie['title'],
            'showtime': showtime,
            'seats': seat_list,
            'num_tickets': num_tickets,
            'price_per_ticket': ticket_price,
            'total_amount': total
        })

        # Send SNS notification (optional email not used directly here)
        send_booking_email("booking@moviemagic.com", movie['title'], showtime, seat_input, booking_id)

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
    response = bookings_table.scan()
    bookings = response.get('Items', [])
    return render_template("mybookings.html", bookings=bookings)

if __name__ == '__main__':
    app.run(port=5000,host='0.0.0.0',debug=True)
