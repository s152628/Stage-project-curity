from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
    # We halen de Curity URL uit een omgevingsvariabele (geïnjecteerd door K8s)
    curity_url = os.getenv('CURITY_URL', 'https://dev.curity.local')
    return f"<h1>Test App</h1><p>Verbonden met Curity op: {curity_url}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)