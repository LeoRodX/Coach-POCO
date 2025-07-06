from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# Пути к файлам
DATA_DIR = 'data'
QUESTIONS_FILE = os.path.join(DATA_DIR, 'questions.json')
RESULTS_FILE = os.path.join(DATA_DIR, 'results.txt')

# Создаем папку data, если ее нет
os.makedirs(DATA_DIR, exist_ok=True)

def load_test_data():
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        'title': data.get('test_title', 'Тест'),
        'intro': data.get('test_intro', ''),
        'questions': data.get('questions', [])
    }

def save_result(email, score, total, answers):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RESULTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"Дата: {timestamp}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Баллы: {score} из {total}\n")
        f.write("Ответы:\n")
        for i, answer in enumerate(answers, 1):
            f.write(f"  Вопрос {i}: {answer}\n")
        f.write("\n")

@app.route('/', methods=['GET', 'POST'])
def index():
    test_data = load_test_data()
    questions = test_data['questions']
    total_points = sum(q['points'] for q in questions)
    
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return redirect(url_for('index'))
        
        score = 0
        user_answers = []
        
        for i, question in enumerate(questions):
            answer_key = f'question_{i}'
            if question['type'] == 'single':
                user_answer = request.form.get(answer_key)
                user_answers.append(user_answer or "Нет ответа")
                if user_answer and int(user_answer) in question['correct']:
                    score += question['points']
            else:  # multiple
                user_answer = request.form.getlist(answer_key)
                user_answers.append(", ".join(user_answer) or "Нет ответа")
                correct_answers = set(str(i) for i in question['correct'])
                user_answers_set = set(user_answer)
                if user_answers_set == correct_answers:
                    score += question['points']
        
        save_result(email, score, total_points, user_answers)
        return render_template('index.html', 
                             test_title=test_data['title'],
                             test_intro=test_data['intro'],
                             questions=questions,
                             email=email,
                             score=score,
                             total=total_points,
                             show_result=True)
    
    return render_template('index.html', 
                         test_title=test_data['title'],
                         test_intro=test_data['intro'],
                         questions=questions,
                         show_result=False)

if __name__ == '__main__':
    app.run(debug=True)