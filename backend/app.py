from flask import Flask
from database.connection import get_db_connection
from routes.users import users_bp
from extensions import bcrypt
from config import DATABASE_CONFIG

app = Flask(__name__)
bcrypt.init_app(app)
app.config['DATABASE_CONFIG'] = DATABASE_CONFIG

@app.route('/')
def home():
    conn = None
    try:
        conn = get_db_connection(app.config['DATABASE_CONFIG'])
        if conn:
            return "Conexão com o banco de dados estabelecida com sucesso! 🐍"
        else:
            return "Erro: Conexão com o banco de dados falhou."
    finally:
        if conn:
            conn.close()

app.register_blueprint(users_bp, url_prefix='/api/users')     

if __name__ == '__main__':
    conn = get_db_connection(app.config['DATABASE_CONFIG'])
    if conn:
        print("Conexão com o banco de dados estabelecida.")
        conn.close()
    app.run(debug=True)