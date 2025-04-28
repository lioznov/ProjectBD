class Config:
    SECRET_KEY = "your-secret-key"  # Замените на случайный набор символов для безопасности
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:Bdh6kDbcA@localhost/travel_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False