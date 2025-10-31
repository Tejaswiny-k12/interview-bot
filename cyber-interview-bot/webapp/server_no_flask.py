"""
Minimal static + API server using Python stdlib so the web UI can run without Flask.
Run with: python server_no_flask.py
Serves on http://127.0.0.1:5000/
"""
import http.server
import socketserver
import json
import os
import random
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(__file__)
STATIC_DIR = os.path.join(ROOT, 'static')
TEMPLATES_DIR = os.path.join(ROOT, 'templates')
QUESTIONS_PATH = os.path.join(os.path.dirname(ROOT), 'questions.json')

# import the evaluator from parent package file
import sys
sys.path.insert(0, os.path.dirname(ROOT))
from cyber_interview_bot import load_questions, evaluate_answer

PORT = 5000
QUESTIONS = load_questions()
QUESTIONS_BY_ID = {q['id']: q for q in QUESTIONS}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == '/' or path == '/index.html':
            self.serve_file(os.path.join(TEMPLATES_DIR, 'index.html'))
            return
        if path.startswith('/static/'):
            rel = path[len('/static/'):]
            self.serve_file(os.path.join(STATIC_DIR, rel))
            return
        if path == '/api/question':
            difficulty = qs.get('difficulty', ['Intermediate'])[0].title()
            qtype = qs.get('type', [''])[0]
            pool = [q for q in QUESTIONS if q.get('difficulty','').title() == difficulty]
            if qtype:
                pool = [q for q in pool if q.get('type','').lower() == qtype.lower()]
            if not pool:
                pool = QUESTIONS
            question = random.choice(pool)
            payload = {'id': question['id'], 'question': question['question'], 'difficulty': question.get('difficulty'), 'type': question.get('type')}
            self.send_json(payload)
            return
        if path == '/api/explain':
            qid = qs.get('question_id', [None])[0]
            if not qid or qid not in QUESTIONS_BY_ID:
                self.send_json({'error':'invalid question id'}, code=400)
                return
            q = QUESTIONS_BY_ID[qid]
            self.send_json({'explanation': q.get('explanation',''), 'references': q.get('references', [])})
            return

        # fallback: 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == '/api/evaluate':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
            except Exception:
                self.send_json({'error':'invalid json'}, code=400)
                return
            qid = data.get('question_id')
            answer = data.get('answer','')
            if not qid or qid not in QUESTIONS_BY_ID:
                self.send_json({'error':'invalid question id'}, code=400)
                return
            q = QUESTIONS_BY_ID[qid]
            score, reason, strengths, weaknesses, tips = evaluate_answer(q, answer)
            self.send_json({'score': score, 'reason': reason, 'strengths': strengths, 'weaknesses': weaknesses, 'tips': tips})
            return
        # fallback
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')

    def serve_file(self, path):
        if not os.path.isfile(path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            return
        ctype = 'application/octet-stream'
        if path.endswith('.html'):
            ctype = 'text/html'
        elif path.endswith('.js'):
            ctype = 'application/javascript'
        elif path.endswith('.css'):
            ctype = 'text/css'
        elif path.endswith('.json'):
            ctype = 'application/json'
        with open(path, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-type', ctype)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, obj, code=200):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == '__main__':
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
        print(f"Serving at http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Shutting down')
            httpd.server_close()
