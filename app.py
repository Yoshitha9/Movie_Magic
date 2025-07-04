from flask import Flask, render_template, request, redirect, url_for, session
import boto3
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# AWS Configuration
aws_region = 'us-east-1'
sns_topic_arn = 'arn:aws:sns:us-east-1:577638351818:movies'

# Initialize AWS Services
dynamodb = boto3.resource('dynamodb', region_name=aws_region)
sns = boto3.client('sns', region_name=aws_region)

# DynamoDB Tables
users_table = dynamodb.Table('Users')
bookings_table = dynamodb.Table('Bookings')

# Static movie list (no Movies table needed)
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

# SNS Email Notification
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
            'password': passwor

