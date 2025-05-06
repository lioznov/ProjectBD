from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum('admin', 'user'), nullable=False, default='user')

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    reviews = db.relationship('Review', backref='tour', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Рейтинг от 1 до 5
    comment = db.Column(db.Text, nullable=False)   # Текст отзыва

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=db.func.now())
    payment_status = db.Column(db.String(20), default='pending')  # Статус оплаты: pending, paid, failed