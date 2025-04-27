from flask import Flask, render_template, request, flash, redirect, url_for, session
import pymysql
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Bdh6kDbcA',
    'db': 'Service',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.route('/', methods=['GET', 'POST'])
def index():
    # Проверка, авторизован ли пользователь
    username = session.get('username', None)
    role = session.get('role', 'user')
    user_id = session.get('user_id', None)

    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # Получаем список всех туров из базы данных
            sql_tours = "SELECT * FROM Tours"
            cursor.execute(sql_tours)
            tours = cursor.fetchall()

            # Обработка POST-запроса для бронирования туров
            if request.method == 'POST' and user_id:
                tour_id = request.form['tour_id']
                start_date = request.form['start_date']
                end_date = request.form['end_date']

                # Проверяем, существует ли выбранный тур
                sql_check_tour = "SELECT * FROM Tours WHERE tour_id = %s"
                cursor.execute(sql_check_tour, (tour_id,))
                tour = cursor.fetchone()

                if not tour:
                    flash('Выбранный тур не существует.', 'danger')
                    return redirect(url_for('index'))

                # Добавляем бронирование в базу данных
                sql_add_booking = """
                    INSERT INTO Bookings (user_id, tour_id, status, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_add_booking, (user_id, tour_id, 'booked', start_date, end_date))
                connection.commit()

                flash('Тур успешно забронирован!', 'success')
                return redirect(url_for('index'))

        return render_template('index.html', tours=tours, username=username, role=role)

    except Exception as e:
        flash(f'Произошла ошибка: {str(e)}', 'danger')
        return redirect(url_for('index'))

    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']  # Получаем роль из формы

            # Хэширование пароля
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Users (username, email, password_hash, role)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (username, email, password_hash, role))
                connection.commit()

            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('login'))

        except pymysql.err.IntegrityError:
            flash('Ошибка: Пользователь с таким email уже существует.', 'danger')
            return redirect(url_for('register'))

        except Exception as e:
            flash(f'Произошла ошибка: {str(e)}', 'danger')
            return redirect(url_for('register'))

        finally:
            if 'connection' in locals():
                connection.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # Получаем роль из формы

        # Хэширование пароля
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT user_id, username, email, role FROM Users WHERE email = %s AND password_hash = %s"
                cursor.execute(sql, (email, password_hash))
                user = cursor.fetchone()

                if user and user['role'] == role:  # Проверяем совпадение роли
                    session['user_id'] = user['user_id']
                    session['username'] = user['username']
                    session['email'] = user['email']
                    session['role'] = user['role']  # Сохраняем роль в сессии
                    flash('Вы успешно вошли!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Неверный email, пароль или роль.', 'danger')
                    return redirect(url_for('login'))

        except Exception as e:
            flash(f'Произошла ошибка: {str(e)}', 'danger')
            return redirect(url_for('login'))

        finally:
            if 'connection' in locals():
                connection.close()

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Вы должны войти, чтобы увидеть личный кабинет.', 'danger')
        return redirect(url_for('login'))

    role = session.get('role', 'user')

    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('У вас нет прав для доступа к этой странице.', 'danger')
        return redirect(url_for('index'))

    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            sql_tours = "SELECT * FROM Tours"
            cursor.execute(sql_tours)
            tours = cursor.fetchall()

        return render_template('admin_dashboard.html', username=session['username'], email=session['email'], tours=tours)

    except Exception as e:
        flash(f'Произошла ошибка: {str(e)}', 'danger')
        return redirect(url_for('index'))

    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/user_dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        flash('У вас нет прав для доступа к этой странице.', 'danger')
        return redirect(url_for('index'))

    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            sql_bookings = """
                SELECT 
                    Tours.title, 
                    Tours.description, 
                    Tours.price, 
                    Tours.country, 
                    Tours.city, 
                    Tours.vacation,
                    Bookings.status, 
                    Bookings.start_date, 
                    Bookings.end_date
                FROM Bookings
                JOIN Tours ON Bookings.tour_id = Tours.tour_id
                WHERE Bookings.user_id = %s
            """
            cursor.execute(sql_bookings, (session['user_id'],))
            bookings = cursor.fetchall()

        return render_template('user_dashboard.html', username=session['username'], email=session['email'], bookings=bookings)

    except Exception as e:
        flash(f'Произошла ошибка: {str(e)}', 'danger')
        return redirect(url_for('index'))

    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/add_tour', methods=['POST'])
def add_tour():
    if session.get('role') != 'admin':
        flash('У вас нет прав для выполнения этого действия.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        country = request.form['country']
        city = request.form['city']
        vacation = request.form.get('vacation')

        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Tours (title, description, price, country, city, vacation)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (title, description, price, country, city, vacation))
            connection.commit()

        flash('Тур успешно добавлен!', 'success')
        return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f'Произошла ошибка: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/delete_tour/<int:tour_id>', methods=['GET'])
def delete_tour(tour_id):
    if session.get('role') != 'admin':
        flash('У вас нет прав для выполнения этого действия.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            sql = "DELETE FROM Tours WHERE tour_id = %s"
            cursor.execute(sql, (tour_id,))
            connection.commit()

        flash('Тур успешно удален!', 'success')
        return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f'Произошла ошибка: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('role', None)
    flash('Вы успешно вышли.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)