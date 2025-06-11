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

COURSE_DATA = {
    "Начальный уровень": {
        "duration": 48,
        "teacher": "Анна Петрова",
        "lessons": [
            {
                "id": 1,
                "title": "Алфавит и базовые фразы",
                "duration": 20,
                "difficulty": "Начальная",
                "type": "text",
                "theory": "<p>Английский алфавит состоит из 26 букв. Каждая буква имеет своё название и звучание.</p><p>Основные фразы для знакомства:</p><ul><li>Hello! - Привет!</li><li>My name is... - Меня зовут...</li><li>Nice to meet you! - Приятно познакомиться!</li></ul>",
                "assignment": "<p>Составьте 3 предложения о себе, используя изученные фразы.</p>"
            },
            {
                "id": 2,
                "title": "Глагол to be",
                "duration": 25,
                "difficulty": "Начальная",
                "type": "choice",
                "theory": "<p>Глагол <strong>to be</strong> (быть) - один из основных глаголов в английском языке. Его формы: am, is, are.</p><p>Правила использования:</p><ul><li>I <strong>am</strong> - Я есть</li><li>He/She/It <strong>is</strong> - Он/Она/Оно есть</li><li>You/We/They <strong>are</strong> - Ты/Вы/Мы/Они есть</li></ul>",
                "assignment": "<p>Выберите правильную форму глагола to be:</p>",
                "options": [
                    "I ___ a student. (am)",
                    "She ___ from London. (is)",
                    "We ___ happy. (are)",
                    "It ___ a book. (is)",
                    "You ___ my friend. (are)"
                ],
                "answer": 0  # Индекс правильного ответа (0 для первого вопроса)
            },
            {
                "id": 3,
                "title": "Артикли a/an",
                "duration": 30,
                "difficulty": "Начальная",
                "type": "choice",
                "theory": "<p>Артикли <strong>a</strong> и <strong>an</strong> используются перед исчисляемыми существительными в единственном числе.</p><p>Правила:</p><ul><li><strong>a</strong> - перед словами, начинающимися с согласного звука</li><li><strong>an</strong> - перед словами, начинающимися с гласного звука</li></ul>",
                "assignment": "<p>Выберите правильный артикль:</p>",
                "options": [
                    "___ apple (an)",
                    "___ book (a)",
                    "___ university (a)",
                    "___ hour (an)",
                    "___ car (a)"
                ],
                "answer": 0  # Индекс правильного ответа
            }
        ]
    },
    "Средний уровень": {
        "duration": 72,
        "teacher": "Иван Сидоров",
        "lessons": [
            {
                "id": 1,
                "title": "Present Simple",
                "duration": 30,
                "difficulty": "Средняя",
                "type": "text",
                "theory": "<p><strong>Present Simple</strong> используется для описания регулярных действий, привычек и общеизвестных фактов.</p><p>Образование: I/You/We/They + V1, He/She/It + V1 + s/es</p><p>Примеры:</p><ul><li>I work every day.</li><li>She plays tennis on weekends.</li><li>The sun rises in the east.</li></ul>",
                "assignment": "<p>Напишите 5 предложений о своих ежедневных привычках, используя Present Simple.</p>"
            },
            {
                "id": 2,
                "title": "Past Simple",
                "duration": 35,
                "difficulty": "Средняя",
                "type": "choice",
                "theory": "<p><strong>Past Simple</strong> используется для описания действий, которые произошли в определенный момент в прошлом.</p><p>Образование: V2 для неправильных глаголов, V1 + ed для правильных.</p><p>Примеры:</p><ul><li>I visited London last year.</li><li>She bought a new car yesterday.</li><li>They went to the cinema on Friday.</li></ul>",
                "assignment": "<p>Выберите правильную форму глагола в Past Simple:</p>",
                "options": [
                    "I ___ to school yesterday. (went)",
                    "She ___ a letter last night. (wrote)",
                    "We ___ dinner at 7 pm. (ate)",
                    "He ___ his homework. (did)",
                    "They ___ the movie. (watched)"
                ],
                "answer": 0  # Индекс правильного ответа
            },
            {
                "id": 3,
                "title": "Future Simple",
                "duration": 40,
                "difficulty": "Средняя",
                "type": "choice",
                "theory": "<p><strong>Future Simple</strong> используется для описания действий, которые произойдут в будущем.</p><p>Образование: will + V1</p><p>Примеры:</p><ul><li>I will call you tomorrow.</li><li>She will finish the project next week.</li><li>They will travel to Spain in summer.</li></ul>",
                "assignment": "<p>Выберите правильную форму глагола в Future Simple:</p>",
                "options": [
                    "I ___ you later. (will call)",
                    "She ___ the report. (will write)",
                    "We ___ the meeting. (will attend)",
                    "He ___ early. (will arrive)",
                    "They ___ a new house. (will buy)"
                ],
                "answer": 0  # Индекс правильного ответа
            }
        ]
    },
    "Продвинутый уровень": {
        "duration": 96,
        "teacher": "Мария Иванова",
        "lessons": [
            {
                "id": 1,
                "title": "Conditionals",
                "duration": 45,
                "difficulty": "Продвинутая",
                "type": "text",
                "theory": "<p><strong>Условные предложения</strong> выражают условие и его следствие.</p><p>Типы:</p><ul><li>Zero Conditional: If + Present, Present (общие истины)</li><li>First Conditional: If + Present, Future (реальные будущие ситуации)</li><li>Second Conditional: If + Past, would + V1 (маловероятные ситуации)</li><li>Third Conditional: If + Past Perfect, would have + V3 (невозможные прошлые ситуации)</li></ul>",
                "assignment": "<p>Напишите по одному примеру для каждого типа условных предложений.</p>"
            },
            {
                "id": 2,
                "title": "Reported Speech",
                "duration": 50,
                "difficulty": "Продвинутая",
                "type": "choice",
                "theory": "<p><strong>Косвенная речь</strong> используется для передачи чьих-либо слов.</p><p>Основные изменения:</p><ul><li>Present Simple → Past Simple</li><li>Present Continuous → Past Continuous</li><li>will → would</li><li>can → could</li><li>today → that day</li><li>tomorrow → the next day</li></ul>",
                "assignment": "<p>Выберите правильный вариант преобразования прямой речи в косвенную:</p>",
                "options": [
                    "She said, 'I am happy.' → She said that she ___ happy. (was)",
                    "He said, 'I will come.' → He said that he ___. (would come)",
                    "They said, 'We are working.' → They said that they ___. (were working)",
                    "I said, 'I can help.' → I said that I ___. (could help)",
                    "You said, 'It is raining.' → You said that it ___. (was raining)"
                ],
                "answer": 0  # Индекс правильного ответа
            },
            {
                "id": 3,
                "title": "Phrasal Verbs",
                "duration": 55,
                "difficulty": "Продвинутая",
                "type": "choice",
                "theory": "<p><strong>Фразовые глаголы</strong> состоят из глагола и частицы (предлога или наречия). Значение часто отличается от исходного глагола.</p><p>Примеры:</p><ul><li>look up - искать в словаре</li><li>give up - сдаваться</li><li>take off - взлетать (о самолете)</li><li>turn on - включать</li><li>put off - откладывать</li></ul>",
                "assignment": "<p>Выберите правильный фразовый глагол для завершения предложения:</p>",
                "options": [
                    "Please ___ the light. It's dark. (turn on)",
                    "Don't ___! You can do it! (give up)",
                    "I need to ___ this word in the dictionary. (look up)",
                    "The plane will ___ in 10 minutes. (take off)",
                    "Let's ___ the meeting until tomorrow. (put off)"
                ],
                "answer": 0  # Индекс правильного ответа
            }
        ]
    }
}



@app.route('/course/<course_name>/lesson/<int:lesson_id>', methods=['GET', 'POST'])
def lesson(course_name, lesson_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    course_info = COURSE_DATA.get(course_name)
    if not course_info:
        flash('Курс не найден', 'danger')
        return redirect(url_for('courses'))
    
    # Находим текущий урок
    current_lesson = None
    for l in course_info['lessons']:
        if l['id'] == lesson_id:
            current_lesson = l
            break
    
    if not current_lesson:
        flash('Урок не найден', 'danger')
        return redirect(url_for('course_details', course_name=course_name))
    
    # Проверяем статус выполнения урока
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    completed = is_lesson_completed(user, course_name, lesson_id)
    
    # Находим предыдущий и следующий уроки
    lessons = course_info['lessons']
    prev_lesson = next_lesson = None
    current_index = next((i for i, l in enumerate(lessons) if l['id'] == lesson_id), -1)
    
    if current_index > 0:
        prev_lesson = lessons[current_index - 1]
    if current_index < len(lessons) - 1:
        next_lesson = lessons[current_index + 1]
    
    # Обработка ответа на задание
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        if check_answer(current_lesson, user_answer):
            mark_lesson_completed(user, course_name, lesson_id)
            flash('Правильный ответ! Урок завершен', 'success')
            completed = True
        else:
            flash('Неправильный ответ. Попробуйте еще раз', 'danger')
    
    return render_template('lesson.html',
                          course_name=course_name,
                          lesson=current_lesson,
                          prev_lesson=prev_lesson,
                          next_lesson=next_lesson,
                          completed=completed)

def is_lesson_completed(user, course_name, lesson_id):
    if user.completed_lessons:
        try:
            completed = json.loads(user.completed_lessons)
            return lesson_id in completed.get(course_name, [])
        except:
            return False
    return False

def mark_lesson_completed(user, course_name, lesson_id):
    completed = {}
    if user.completed_lessons:
        try:
            completed = json.loads(user.completed_lessons)
        except:
            pass
    
    if course_name not in completed:
        completed[course_name] = []
    
    if lesson_id not in completed[course_name]:
        completed[course_name].append(lesson_id)
        user.completed_lessons = json.dumps(completed)
        db.session.commit()

def check_answer(lesson, user_answer):
    if lesson['type'] == 'choice':
        try:
            # Проверяем, что выбранный ответ совпадает с правильным
            return int(user_answer) == lesson.get('answer', -1)
        except:
            return False
    return True  # Для текстовых всегда верно

@app.route('/submit_assignment/<course_name>/<int:lesson_id>', methods=['POST'])
def submit_assignment(course_name, lesson_id):
    if not session.get('logged_in'):
        return jsonify(success=False, error="Не авторизован"), 401
        
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    
    # Загрузка файла задания (если есть)
    if 'assignment_file' in request.files:
        file = request.files['assignment_file']
        if file.filename != '':
            # Здесь должна быть логика сохранения файла
            flash('Файл успешно загружен', 'success')
    
    # Отмечаем урок как выполненный
    try:
        completed_lessons = json.loads(user.completed_lessons) if user.completed_lessons else {}
    except json.JSONDecodeError:
        completed_lessons = {}
        
    if course_name not in completed_lessons:
        completed_lessons[course_name] = []
        
    if lesson_id not in completed_lessons[course_name]:
        completed_lessons[course_name].append(lesson_id)
        user.completed_lessons = json.dumps(completed_lessons)
        db.session.commit()
        flash('Задание успешно отправлено!', 'success')
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Задание уже было отправлено"), 400

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
