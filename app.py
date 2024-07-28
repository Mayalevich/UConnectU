from flask import Flask, request, render_template, redirect, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import spacy
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quickwell.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=True)

nlp = spacy.load("en_core_web_sm")

def analyze_text(text):
    doc = nlp(text)
    keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    sentiment = TextBlob(text).sentiment.polarity
    return keywords, sentiment

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_mood', methods=['POST'])
def add_mood():
    mood = request.form['mood']
    description = request.form['description']
    new_entry = MoodEntry(mood=mood, description=description)
    db.session.add(new_entry)
    db.session.commit()

    keywords, sentiment = analyze_text(description)
    recommendations = generate_recommendations(mood, keywords, sentiment)
    
    return render_template('recommendations.html', recommendations=recommendations)

def generate_recommendations(mood, keywords, sentiment):
    recommendations = []

    if sentiment < -0.5:
        recommendations.extend(["Talk to a friend or family member", "Consider seeing a therapist", "Write down your feelings"])
    elif sentiment < 0:
        recommendations.extend(["Watch a feel-good movie", "Do some light exercise", "Practice mindfulness"])
    elif sentiment < 0.5:
        recommendations.extend(["Take a short break", "Read a book", "Listen to some music"])
    else:
        recommendations.extend(["Keep up the good work!", "Share your positive energy", "Plan an enjoyable activity"])

    if 'walk' in keywords:
        recommendations.extend("Go for a walk")
    if 'meditate' in keywords:
        recommendations.extend("Try meditation")
    if 'exercise' in keywords:
        recommendations.extend("Join a fitness class")
    if 'book' in keywords:
        recommendations.extend("Visit a library or bookstore")

    if mood == 'sad':
        recommendations.extend(["Watch a comedy", "Call a loved one", "Do something creative"])
    elif mood == 'anxious':
        recommendations.extend(["Practice deep breathing exercises", "Try yoga", "Write in a journal"])
    elif mood == 'happy':
        recommendations.extend(["Share your happiness with others", "Engage in a fun activity", "Celebrate your mood"])
    elif mood == 'relaxed':
        recommendations.extend(["Maintain this state of mind", "Listen to relaxing music", "Enjoy a calm hobby"])

    return recommendations

@app.route('/school_input')
def school_input():
    faculties = ['Engineering']
    return render_template('school_input.html', faculties=faculties)

@app.route('/school_resources', methods=['POST'])
def school_resources():
    school = request.form['school']
    faculty = request.form['faculty']
    if school.lower() == 'university of waterloo' and faculty.lower() == 'engineering':
        return render_template('waterloo_resources.html', faculty=faculty)
    else:
        return "Resources for this school or faculty are not available yet."



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
