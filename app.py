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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                sql = "SELECT user_id, username, email FROM Users WHERE email = %s AND password_hash = %s"
                cursor.execute(sql, (email, password_hash))
                user = cursor.fetchone()

                if user:
                    session['user_id'] = user['user_id']
                    session['username'] = user['username']
                    session['email'] = user['email']  # Добавляем email в сессию
                    flash('Вы успешно вошли!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Неверный email или пароль.', 'danger')
                    return redirect(url_for('login'))

        except Exception as e:
            flash(f'Произошла ошибка: {str(e)}', 'danger')
            return redirect(url_for('login'))

        finally:
            if 'connection' in locals():
                connection.close()

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Получение данных из формы
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверка наличия обязательных полей
        if not username or not email or not password:
            flash('Пожалуйста, заполните все поля.', 'danger')
            return redirect(url_for('register'))

        # Хэширование пароля
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                # Вставка данных в таблицу Users
                sql = """
                    INSERT INTO Users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (username, email, password_hash))
                connection.commit()

            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Вы должны войти, чтобы увидеть личный кабинет.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session['username']
    email = session['email']  # Извлекаем email из сессии

    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            sql_bookings = """
                SELECT Tours.title, Bookings.status, Bookings.start_date, Bookings.end_date
                FROM Bookings
                JOIN Tours ON Bookings.tour_id = Tours.tour_id
                WHERE Bookings.user_id = %s
            """
            cursor.execute(sql_bookings, (user_id,))
            bookings = cursor.fetchall()

        return render_template('dashboard.html', username=username, email=email, bookings=bookings)

    except Exception as e:
        flash(f'Произошла ошибка: {str(e)}', 'danger')
        return redirect(url_for('index'))

    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Вы успешно вышли.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)