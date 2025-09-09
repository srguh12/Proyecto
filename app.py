from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from datetime import datetime
import openai
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")
CORS(app, supports_credentials=True)

# Configura tus credenciales de Google aquí
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Solo para desarrollo
GOOGLE_CLIENT_ID = "38450342474-ita8mntg6qgc1fj041j4khuaameah1rt.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=["profile", "email"],
    redirect_url="/google_login/authorized"
)
app.register_blueprint(google_bp, url_prefix="/google_login")

# Pega tu clave de OpenAI aquí
openai.api_key = "sk-...ChIA"

@app.route("/login")
def login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    user_info = resp.json()
    session['user'] = user_info
    return redirect("/")

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/")

@app.route('/user')
def get_user():
    user = session.get('user')
    if user:
        return jsonify(user)
    else:
        return jsonify({}), 401

@app.route('/chat', methods=['POST'])
def chat():
    if not session.get('user'):
        return jsonify({'reply': 'Debes iniciar sesión con Google para usar el chatbot.'}), 401
    data = request.get_json()
    user_message = data.get('message', '')
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente virtual profesional especializado en gestión de información y atención al cliente. Responde siempre en español y de forma clara y amable."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        reply = "Lo siento, hubo un error al conectar con la IA. Intenta de nuevo más tarde."
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
