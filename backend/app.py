from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import config
from models import db, User, Tour, Booking

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.config.from_object(config.Config)
db.init_app(app)

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()

# Главная страница с каталогом туров и поиском
@app.route("/", methods=["GET"])
def index():
    query = request.args.get("query", "")
    if query:
        tours = Tour.query.filter(Tour.destination.ilike(f"%{query}%") | Tour.name.ilike(f"%{query}%")).all()
    else:
        tours = Tour.query.all()
    return render_template("index.html", tours=tours, query=query)

# Страница тура и бронирование
@app.route("/tour/<int:tour_id>", methods=["GET", "POST"])
def tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    if request.method == "POST":
        if "user_id" not in session:
            flash("Пожалуйста, войдите в систему для бронирования")
            return redirect(url_for("login"))
        booking = Booking(user_id=session["user_id"], tour_id=tour_id)
        db.session.add(booking)
        db.session.commit()
        flash("Тур успешно забронирован!")
        return redirect(url_for("profile"))
    return render_template("tour.html", tour=tour)

# Вход
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Вход выполнен успешно!")
            return redirect(url_for("index"))
        flash("Неверное имя пользователя или пароль")
        return render_template("login.html")
    return render_template("login.html")

# Регистрация
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = generate_password_hash(request.form["password"])
    email = request.form["email"]
    user = User(username=username, password=password, email=email)  # Роль по умолчанию — user (задается в модели)
    try:
        db.session.add(user)
        db.session.commit()
        flash("Регистрация прошла успешно! Войдите в систему.")
        return redirect(url_for("login"))
    except:
        db.session.rollback()
        flash("Имя пользователя или email уже заняты")
        return redirect(url_for("login"))

# Профиль пользователя
@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    bookings = Booking.query.filter_by(user_id=user.id).all()
    tours_booked = [Tour.query.get(booking.tour_id) for booking in bookings]
    # Для админов показываем все туры
    tours_all = Tour.query.all() if user.role == 'admin' else []
    return render_template("profile.html", user=user, tours_booked=tours_booked, tours_all=tours_all)

# Добавление тура (только для админов)
@app.route("/add_tour", methods=["POST"])
def add_tour():
    if "user_id" not in session:
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    if user.role != 'admin':
        flash("У вас нет прав для добавления туров")
        return redirect(url_for("profile"))
    name = request.form["name"]
    destination = request.form["destination"]
    country = request.form["country"]
    price = float(request.form["price"])
    description = request.form["description"]
    tour = Tour(name=name, destination=destination, country=country, price=price, description=description)
    db.session.add(tour)
    db.session.commit()
    flash("Тур успешно добавлен!")
    return redirect(url_for("profile"))

# Подтверждение удаления тура (только для админов)
@app.route("/confirm_delete_tour/<int:tour_id>")
def confirm_delete_tour(tour_id):
    if "user_id" not in session or User.query.get(session["user_id"]).role != 'admin':
        flash("Доступ запрещен")
        return redirect(url_for("profile"))
    tour = Tour.query.get_or_404(tour_id)
    return render_template("confirm_delete.html", tour=tour)

# Удаление тура (только для админов)
@app.route("/delete_tour/<int:tour_id>", methods=["POST"])  # Изменено на POST
def delete_tour(tour_id):
    if "user_id" not in session:
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    if user.role != 'admin':
        flash("У вас нет прав для удаления туров")
        return redirect(url_for("profile"))
    tour = Tour.query.get_or_404(tour_id)
    # Удаляем все бронирования, связанные с этим туром
    Booking.query.filter_by(tour_id=tour_id).delete()
    db.session.delete(tour)
    db.session.commit()
    flash("Тур успешно удален!")
    return redirect(url_for("profile"))

# Страница управления пользователями (только для админов)
@app.route("/admin/users")
def admin_users():
    if "user_id" not in session or User.query.get(session["user_id"]).role != 'admin':
        flash("Доступ запрещен")
        return redirect(url_for("index"))
    users = User.query.all()
    return render_template("admin_users.html", users=users)

# Изменение роли пользователя (только для админов)
@app.route("/update_role/<int:user_id>", methods=["POST"])
def update_role(user_id):
    if "user_id" not in session or User.query.get(session["user_id"]).role != 'admin':
        flash("Доступ запрещен")
        return redirect(url_for("index"))
    user = User.query.get_or_404(user_id)
    new_role = request.form["role"]
    user.role = new_role
    db.session.commit()
    flash(f"Роль пользователя {user.username} изменена на {new_role}")
    return redirect(url_for("admin_users"))

# Выход
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Вы вышли из системы")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)