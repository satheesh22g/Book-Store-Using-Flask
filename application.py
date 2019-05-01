import os
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_session import Session
from database import Base, Books, Reviews, Accounts
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine('sqlite:///books.db',connect_args={'check_same_thread': False},echo=True)
Base.metadata.bind = engine
db = scoped_session(sessionmaker(bind=engine))
questions = {
    "1": {
        "question": "Which city is the capital of Iran?",
        "options": [
            "Dhaka",
            "Kabul",
            "Tehran",
            "Istambul"],
        "answer": "Tehran"},
    "2": {
        "question": "What is the human bodys biggest organ?",
        "options": [
                    'The cerebrum',
                    'Epidermis',
                    'Ribs',
                    'The skin'],
        "answer": "The skin"},
    "3": {
        "question": "Electric current is typically measured in what units?",
        "options": [
            'joule',
            'Ampere',
            'Watt',
            'Ohm'],
        "answer": "Ampere"},
    "4": {
        "question": "Who was known as Iron man of India?",
        "options": [
            "Govind Ballabh Pant",
            "Jawaharlal Nehru",
            "Subhash Chandra Bose",
            "Sardar Vallabhbhai Patel"],
        "answer": "Sardar Vallabhbhai Patel"},
    "5": {
        "question": "What is the smallest planet in the Solar System?",
        "options": [
            "Mercury",
            "Mars",
            "Jupitar",
            "Neptune"],
        "answer": "Mercury"},
    "6": {
        'question': "What is the name of the largest ocean on earth?",
        "options": [
            "Atlantic",
            "Pacafic",
            "Indian Ocean",
            "Meditanarian"],
        "answer": "Pacafic"},
    "7": {
        'question': "What country has the second largest population in the world?",
        "options": [
            "Indonasia",
            "America",
            "India",
            "China"],
        "answer": "India"},
    "8": {
        'question': "Zurich is the largest city in what country?",
        "options": [
            "France",
            "Spain",
            "Scotland",
            "Switzerland"],
        "answer": "Switzerland"},
    "9": {
        'question': "What is the next prime number after 7?",
        "options": [
            "13",
            "9",
            "17",
            "11"],
        "answer": "11"},
    "10": {
        'question': "At what temperature is Fahrenheit equal to Centigrade?",
        "options": [
            "0 degrees ",
            "-40 degrees",
            "213 degrees",
            "-213 degrees"],
        "answer": "-40 degrees"}}


@app.route("/")
def index():

    return redirect(url_for('dashboard'))
@app.route("/books")
def dashboard():
   

    results = db.execute("SELECT * FROM books limit 10").fetchall()
    username = db.execute("SELECT username FROM accounts").fetchone()

    return render_template("menu.html",results=results,username=username)

@app.route("/register", methods=["GET", "POST"])
def register():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    message = None

    if request.method == "POST":
        try: 
            usern = request.form.get("username")
            passw = request.form.get("password")
            passw_hash = bcrypt.generate_password_hash(passw).decode('utf-8')

            result = db.execute("INSERT INTO accounts (username, password) VALUES (:u, :p)", {"u": usern, "p": passw_hash})
            db.commit()

            if result.rowcount > 0:
                session['user'] = usern
                return redirect(url_for('dashboard'))

        except exc.IntegrityError:
            message = "Username already exists."
            db.execute("ROLLBACK")
            db.commit()

    return render_template("registration.html", message=message)

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    message = None

    if request.method == "POST":
        usern = request.form.get("username")
        passw = request.form.get("password").encode('utf-8')
        result = db.execute("SELECT * FROM accounts WHERE username = :u", {"u": usern}).fetchone()

        if result is not None:
            print(result['password'])
            if bcrypt.check_password_hash(result['password'], passw) is True:
                session['user'] = usern
                return redirect(url_for('dashboard'))

        message = "Username or password is incorrect."
    return render_template("login.html", message=message)


@app.route("/search")
def searchbox():
    return render_template("search1.html")

@app.route("/dashboard/search", methods=["POST"])
def search():
    message = None
    query = request.form.get("searchbox")
    query = '%' + query.lower() + '%'
    results = db.execute("SELECT * FROM books WHERE lower(title) LIKE :q OR isbn LIKE :q OR lower(author) LIKE :q", {"q": query}).fetchall()
    return render_template("search.html", results=results)

@app.route('/quiz',methods=['GET', 'POST'])
def quiz():

    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        if "question" in session:
            entered_answer = request.form.get('answer', '')
            if questions.get(session["question"], False):
                if entered_answer != questions[session["question"]]["answer"]:
                   session["question"] = str(int(session["question"]) + 1)


                else:
                    
                    session["mark"] += 1
                    print(session["mark"])
                    
                    session["question"] = str(int(session["question"]) + 1)
                    if session["question"] in questions:
                        redirect(url_for('quiz'))
                    else:
                        return render_template(
                            "score.html", score=session["mark"])
            else:
                return render_template("score.html", score=session["mark"])

    if "question" not in session:
        session["question"] = "1"
        session["mark"] = 0

    elif session["question"] not in questions:
         session["question"] = str(int(session["question"]) - 10)
         session["question"] = "1"
         session["mark"] = 0
        


    return render_template("quiz.html",
                           question=questions[session["question"]]["question"],
                           question_number=session["question"],
                           options=questions[session["question"]]["options"],
                           score=session["mark"]
                           )



@app.route("/b/<string:isbn>", methods=["GET", "POST"])
def info(isbn):
    message = None
    if 'user' not in session:
        message = "You must login to access the book!"
        return redirect(url_for('login'))

    message = "You must login to access the book!"

    if request.method == "POST":
        comment = request.form.get("comment")
        my_rating = request.form.get("rating")
        book = db.execute("INSERT INTO reviews (acc_id, book_id, comment, rating) VALUES (:a, :b, :c, :r)", {"a": session['user'], "b": isbn, "c": comment, "r": my_rating})
        db.commit()

    book = db.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :q1", {"q1": isbn}).fetchall()

    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1O7xiWC9D6p2JmdhgX4LTw", "isbns": isbn})
    data = response.json()
    gr_rating = (data['books'][0]['average_rating'])

    return render_template("info.html", book_info=book, reviews=reviews, rating=gr_rating)

@app.route("/api/<string:isbn>")
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :q1", {"q1": isbn}).fetchall()
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1O7xiWC9D6p2JmdhgX4LTw", "isbns": isbn})
    data = response.json()['books'][0]
    
    return jsonify({
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "review_count": data['reviews_count'],
        "average_rating": data['average_rating']
    })

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
