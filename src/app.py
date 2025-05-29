# app.py - обновленный серверный код
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_12345!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    completed_lessons = db.Column(db.JSON, default=json.dumps({}))  # Используем JSON-строку

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), default=datetime.now().strftime("%d.%m.%Y"))

# Данные курсов
COURSE_DATA = {
    "Начальный уровень": {
        "duration": 48,
        "teacher": "Анна Петрова",
        "lessons": [
            {"id": 1, "title": "Урок 1: Алфавит"},
            {"id": 2, "title": "Урок 2: Глаголы"},
            {"id": 3, "title": "Урок 3: Существительные"}
        ]
    },
    "Средний уровень": {
        "duration": 72,
        "teacher": "Иван Сидоров",
        "lessons": [
            {"id": 1, "title": "Урок 1: Идиомы"},
            {"id": 2, "title": "Урок 2: Чтение"},
            {"id": 3, "title": "Урок 3: Грамматика"}
        ]
    },
    "Продвинутый уровень": {
        "duration": 96,
        "teacher": "Мария Иванова",
        "lessons": [
            {"id": 1, "title": "Урок 1: Бизнес-письма"},
            {"id": 2, "title": "Урок 2: Переговоры"},
            {"id": 3, "title": "Урок 3: Презентации"}
        ]
    }
}


@app.route('/php')
def run_php():
    import subprocess
    try:
        result = subprocess.run(
            ['docker', 'run', '--rm', 
             '-v', f'{os.getcwd()}:/app', 
             '-w', '/app', 
             'php:8.3-cli', 'php', 'app.php'],
            capture_output=True, text=True, check=True
        )
        return jsonify({"output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr}), 500
    

@app.route('/')
def index():
    return render_template('about.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/reviews', methods=['GET', 'POST'])
def reviews_page():
    if request.method == 'POST':
        review_data = {
            "name": request.form.get('name'),
            "course": request.form.get('course'),
            "rating": int(request.form.get('rating')),
            "text": request.form.get('review'),
        }
        if not all(review_data.values()):
            flash('Заполните все обязательные поля', 'danger')
            return redirect(url_for('reviews_page'))
        new_review = Review(**review_data)
        db.session.add(new_review)
        db.session.commit()
        flash('Отзыв успешно опубликован!', 'success')
        return redirect(url_for('reviews_page'))
    reviews = Review.query.all()
    return render_template('Reviews.html', reviews=reviews)

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['logged_in'] = True
            session['user_email'] = email
            return redirect(url_for('profile'))
        else:
            flash('Неверные учетные данные', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash("Пароль должен содержать не менее 6 символов", "danger")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Пароли не совпадают", "danger")
            return redirect(url_for("register"))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile')
def profile():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    active_tab = request.args.get('tab', 'courses')
    
    # Подготовка данных о курсах
    course_progress = []
    if user.completed_lessons:
        try:
            completed_lessons = json.loads(user.completed_lessons)
            for course_name in completed_lessons:
                if course_name in COURSE_DATA:
                    lessons = completed_lessons[course_name]
                    total_lessons = len(COURSE_DATA[course_name]["lessons"])
                    completed_count = len(lessons)
                    percentage = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0
                    course_progress.append({
                        "name": course_name,
                        "completed_count": completed_count,
                        "total_lessons": total_lessons,
                        "percentage": percentage
                    })
        except json.JSONDecodeError:
            pass
            
    return render_template('profile.html', 
                         user=user,
                         active_tab=active_tab,
                         course_progress=course_progress)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/update_email', methods=['POST'])
def update_email():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    old_email = session['user_email']
    new_email = request.form.get('new_email')
    if User.query.filter_by(email=new_email).first():
        flash('Этот email уже занят', 'error')
    else:
        user = User.query.filter_by(email=old_email).first()
        user.email = new_email
        session['user_email'] = new_email
        db.session.commit()
        flash('Email успешно изменён', 'success')
    return redirect(url_for('profile', tab='settings'))

@app.route('/update_password', methods=['POST'])
def update_password():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    email = session['user_email']
    old_pass = request.form.get('old_password')
    new_pass = request.form.get('new_password')
    user = User.query.filter_by(email=email).first()
    if bcrypt.check_password_hash(user.password, old_pass):
        user.password = bcrypt.generate_password_hash(new_pass).decode('utf-8')
        db.session.commit()
        flash('Пароль успешно изменён', 'success')
    else:
        flash('Неверный текущий пароль', 'error')
    return redirect(url_for('profile', tab='settings'))

@app.route('/course/<course_name>')
def course_details(course_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    course_info = COURSE_DATA.get(course_name)
    
    if not course_info:
        flash('Курс не найден', 'danger')
        return redirect(url_for('courses'))
        
    # Получаем список завершенных уроков для этого курса
    completed_lessons = []
    if user.completed_lessons:
        try:
            lessons_data = json.loads(user.completed_lessons)
            completed_lessons = lessons_data.get(course_name, [])
        except json.JSONDecodeError:
            pass
            
    total_lessons = len(course_info["lessons"])
    completed_count = len(completed_lessons)
    
    # Рассчитываем процент
    percentage = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0
    
    # Помечаем уроки как завершенные
    for lesson in course_info["lessons"]:
        lesson["completed"] = lesson["id"] in completed_lessons
        
    return render_template('course_details.html', 
                          course_name=course_name,
                          course_info=course_info,
                          completed_count=completed_count,
                          total_lessons=total_lessons,
                          percentage=percentage)

@app.route('/complete_lesson/<course_name>/<int:lesson_id>', methods=['POST'])
def complete_lesson(course_name, lesson_id):
    if not session.get('logged_in'):
        return jsonify(success=False, error="Не авторизован"), 401
        
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    
    # Загружаем данные о завершенных уроках
    try:
        completed_lessons = json.loads(user.completed_lessons) if user.completed_lessons else {}
    except json.JSONDecodeError:
        completed_lessons = {}
        
    # Инициализируем список для курса, если его нет
    if course_name not in completed_lessons:
        completed_lessons[course_name] = []
        
    # Добавляем урок, если его еще нет
    if lesson_id not in completed_lessons[course_name]:
        completed_lessons[course_name].append(lesson_id)
        user.completed_lessons = json.dumps(completed_lessons)
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Урок уже завершен"), 400

@app.route('/update_progress/<course_name>')
def update_progress(course_name):
    if not session.get('logged_in'):
        return jsonify(error="Не авторизован"), 401
        
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    
    course_info = COURSE_DATA.get(course_name)
    if not course_info:
        return jsonify(error="Курс не найден"), 404
        
    try:
        completed_lessons = json.loads(user.completed_lessons) if user.completed_lessons else {}
    except json.JSONDecodeError:
        completed_lessons = {}
        
    lessons = completed_lessons.get(course_name, [])
    total_lessons = len(course_info["lessons"])
    completed_count = len(lessons)
    percentage = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0
    
    return jsonify(
        completed_count=completed_count,
        total_lessons=total_lessons,
        percentage=percentage
    )

@app.route('/api/user_progress')
def user_progress():
    if not session.get('logged_in'):
        return jsonify(error="Не авторизован"), 401
        
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    course_progress = []
    
    try:
        completed_lessons = json.loads(user.completed_lessons) if user.completed_lessons else {}
    except json.JSONDecodeError:
        completed_lessons = {}
        
    for course_name in completed_lessons:
        if course_name in COURSE_DATA:
            lessons = completed_lessons[course_name]
            total_lessons = len(COURSE_DATA[course_name]["lessons"])
            completed_count = len(lessons)
            percentage = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0
            course_progress.append({
                "name": course_name,
                "completed_count": completed_count,
                "total_lessons": total_lessons,
                "percentage": percentage
            })
            
    return jsonify(courses=course_progress)

@app.route('/enroll/<course_name>')
def enroll(course_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    
    # Проверяем, существует ли курс
    if course_name not in COURSE_DATA:
        flash('Курс не найден', 'danger')
        return redirect(url_for('courses'))
        
    try:
        completed_lessons = json.loads(user.completed_lessons) if user.completed_lessons else {}
    except json.JSONDecodeError:
        completed_lessons = {}
        
    # Добавляем курс, если его нет
    if course_name not in completed_lessons:
        completed_lessons[course_name] = []
        user.completed_lessons = json.dumps(completed_lessons)
        db.session.commit()
        flash(f'Вы успешно записаны на курс "{course_name}"!', 'success')
    else:
        flash(f'Вы уже записаны на курс "{course_name}"', 'info')
        
    return redirect(url_for('profile'))

    

# Создание таблиц
with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run(debug=True)