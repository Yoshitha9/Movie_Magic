from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Updated movies_data: "LEGEND" removed, three new entries added
movies_data = [
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

@app.route('/')
def landing():
    return render_template("landing.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        return redirect(url_for('signin'))
    return render_template("signup.html")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        return redirect(url_for('index'))
    return render_template("signin.html")

@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/movies')
def movies():
    return render_template("movies.html", movies=movies_data)

@app.route('/book/<int:movie_id>/<showtime>', methods=['GET', 'POST'])
def book(movie_id, showtime):
    if request.method == 'POST':
        seat_input = request.form['seat']
        seat_list = [s.strip() for s in seat_input.split(',') if s.strip()]
        num_tickets = len(seat_list)
        movie = next((m for m in movies_data if m["id"] == movie_id), None)
        ticket_price = 150
        total = num_tickets * ticket_price

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

if __name__ == '__main__':
    app.run(debug=True)
