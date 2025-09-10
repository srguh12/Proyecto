from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import os


DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'chatbot')
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Create the users table if it does not exist."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
            """
        )
        conn.commit()


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
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO users (username, password) VALUES (%s, %s)',
                (username, hashed),
            )
            conn.commit()
    except Error as e:
        if getattr(e, 'errno', None) == 1062:
            return jsonify({'message': 'Usuario ya existe'}), 409
        return jsonify({'message': 'Error del servidor'}), 500
    return jsonify({'message': 'Usuario registrado'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Datos incompletos'}), 400
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT password FROM users WHERE username = %s', (username,))
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

def generate_reply(message: str) -> str:
    text = message.lower()
    if 'hola' in text:
        return '¡Hola! ¿En qué puedo ayudarte?'
    if 'adios' in text or 'bye' in text:
        return '¡Hasta luego!'
    return 'No estoy seguro de cómo responder a eso, pero estoy aprendiendo.'


@app.route('/chat', methods=['POST'])
def chat():
    if not session.get('user'):
        return jsonify({'reply': 'Debes iniciar sesión para usar el chatbot.'}), 401
    data = request.get_json() or {}
    user_message = data.get('message', '')
    reply = generate_reply(user_message) if user_message else 'Por favor escribe un mensaje.'
    return jsonify({'reply': reply})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

