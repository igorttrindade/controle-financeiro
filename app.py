from flask import Flask
from connection import get_db_connection
from flask_bcrypt import Bcrypt
from flask import request, jsonify

app = Flask(__name__)
bcrypt = Bcrypt(app)
    
def hash_password(password):
    
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed

@app.route('/')
def home():
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            return "Conexão com o banco de dados estabelecida com sucesso! 🐍"
        else:
            return "Erro: Conexão com o banco de dados falhou."
    finally:
        if conn:
            conn.close()

@app.route('/register', methods=['POST','GET'])
def register():
    try:
        conn = None
        cnx = None
        if request.method == 'POST':
            name_user = request.json.get('name_user')
            email_user = request.json.get('email_user')
            dt_nascimento_user = request.json.get('dt_nascimento_user')
            tel_user = request.json.get('tel_user')
            password = request.json.get('password')
            password_hashed = hash_password(password)

            with open ('./sql/query_register.sql', 'r') as r:
                query = r.read()
            conn = get_db_connection()
            if conn:
                cnx = conn.cursor()
                cnx.execute(query, (name_user, email_user, dt_nascimento_user, password_hashed, tel_user))
                conn.commit()
                return jsonify({'message': 'Usuário criado com sucesso!'})
            
    except Exception as e:
        return f"Erro ao registrar usuário: {e}"
    finally:
        if cnx and conn:
            cnx.close()
            conn.close()

    return "Esta é a página de registro. Use o método POST para enviar seus dados."
            
if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        print("Conexão com o banco de dados estabelecida.")
        conn.close()
    app.run(debug=True)