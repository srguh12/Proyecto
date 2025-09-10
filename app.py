from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')


def init_db():
    """Create the users table if it does not exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )


init_db()


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")
CORS(app, supports_credentials=True)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Datos incompletos'}), 400
    hashed = generate_password_hash(password)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Usuario ya existe'}), 409
    return jsonify({'message': 'Usuario registrado'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Datos incompletos'}), 400
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            'SELECT password FROM users WHERE username = ?', (username,)
        )
        row = cur.fetchone()
    if row and check_password_hash(row[0], password):
        session['user'] = username
        return jsonify({'message': 'Inicio de sesión correcto'})
    return jsonify({'message': 'Credenciales inválidas'}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Sesión cerrada'})


@app.route('/user')
def get_user():
    user = session.get('user')
    if user:
        return jsonify({'username': user})
    return jsonify({}), 401


@app.route('/chat', methods=['POST'])
def chat():
    if not session.get('user'):
        return jsonify({'reply': 'Debes iniciar sesión para usar el chatbot.'}), 401
    data = request.get_json() or {}
    user_message = data.get('message', '')
    if not user_message:
        reply = 'Por favor escribe un mensaje.'
    else:
        reply = f"Recibí tu mensaje: {user_message}"
    return jsonify({'reply': reply})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

