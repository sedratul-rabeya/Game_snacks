from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
db = SQLAlchemy(app)
scores = [{"name": "Alice", "score": 95}, {"name": "Bob", "score": 88}]

@app.route('/get_scores')
def get_scores():
    return jsonify(scores)

if __name__ == '__main__':
    app.run(debug=True)

# Database Model
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    points = db.Column(db.Integer)

# Create tables
with app.app_context():
    db.create_all()

# GET API (all scores)
@app.route('/get_scores', methods=['GET'])
def get_scores():
    scores = Score.query.all()
    result = [{"id": s.id, "name": s.name, "points": s.points} for s in scores]
    return jsonify(result)

# POST API (add score)
@app.route('/add_score', methods=['POST'])
def add_score():
    data = request.get_json()
    new_score = Score(name=data['name'], points=data['points'])
    db.session.add(new_score)
    db.session.commit()
    return jsonify({"message": "Score added successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
