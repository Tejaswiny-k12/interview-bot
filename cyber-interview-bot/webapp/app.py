from flask import Flask, jsonify, request, render_template, send_from_directory
import random
import os

# Import evaluator and loader from the CLI module
from cyber_interview_bot import load_questions, evaluate_answer

ROOT = os.path.dirname(os.path.dirname(__file__))
APP_ROOT = os.path.dirname(__file__)

app = Flask(__name__, static_folder=os.path.join(APP_ROOT, 'static'), template_folder=os.path.join(APP_ROOT, 'templates'))

# Load questions once
QUESTIONS = load_questions()
QUESTIONS_BY_ID = {q['id']: q for q in QUESTIONS}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/question')
def api_question():
    difficulty = request.args.get('difficulty', 'Intermediate').title()
    qtype = request.args.get('type', '')
    # filter by difficulty
    pool = [q for q in QUESTIONS if q.get('difficulty','').title() == difficulty]
    if qtype:
        pool = [q for q in pool if q.get('type','').lower() == qtype.lower()]
    if not pool:
        pool = QUESTIONS
    question = random.choice(pool)
    # return safe fields
    return jsonify({
        'id': question['id'],
        'question': question['question'],
        'difficulty': question.get('difficulty'),
        'type': question.get('type')
    })

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    data = request.get_json() or {}
    qid = data.get('question_id')
    answer = data.get('answer', '')
    if not qid or qid not in QUESTIONS_BY_ID:
        return jsonify({'error': 'invalid question id'}), 400
    q = QUESTIONS_BY_ID[qid]
    score, reason, strengths, weaknesses, tips = evaluate_answer(q, answer)
    return jsonify({
        'score': score,
        'reason': reason,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'tips': tips
    })

@app.route('/api/explain')
def api_explain():
    qid = request.args.get('question_id')
    if not qid or qid not in QUESTIONS_BY_ID:
        return jsonify({'error': 'invalid question id'}), 400
    q = QUESTIONS_BY_ID[qid]
    return jsonify({
        'explanation': q.get('explanation',''),
        'references': q.get('references', [])
    })

if __name__ == '__main__':
    # Host on 127.0.0.1:5000 by default
    app.run(host='127.0.0.1', port=5000, debug=True)
