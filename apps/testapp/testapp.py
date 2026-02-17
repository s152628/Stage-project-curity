from flask import Flask, redirect, url_for, session, render_template_string
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

oauth = OAuth(app)
oauth.register(
    name='curity',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    server_metadata_url=f"{os.getenv('CURITY_BASE_URL')}/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid profile'}
)

@app.route('/')
def home():
    user = session.get('user')
    if user:
        return f"<h1>Welkom, {user['sub']}!</h1><a href='/logout'>Logout</a>"
    return "<h1>Test App</h1><a href='/login'>Login met Curity</a>"

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.curity.authorize_redirect(redirect_uri)

@app.route('/callback')
def auth():
    token = oauth.curity.authorize_access_token()
    session['user'] = token.get('userinfo')
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)