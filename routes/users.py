from database.connection import get_db_connection
from flask import request, jsonify, Blueprint, current_app
from extensions import bcrypt

users_bp = Blueprint('users', __name__)
    
def hash_password(password):
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed

@users_bp.route('/register', methods=['POST','GET'])
def register():
    conn = None
    cnx = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        cnx = conn.cursor()
        if request.method == 'POST':
            name_user = request.json.get('name_user')
            email_user = request.json.get('email_user')
            dt_nascimento_user = request.json.get('dt_nascimento_user')
            tel_user = request.json.get('tel_user')
            password = request.json.get('password')
            if not all([name_user, email_user, password]):
                return jsonify({'error': 'Dados incompletos'}), 400
            
            password_hashed = hash_password(password)

            with open ('./sql/query_register.sql', 'r') as r:
                query_register = r.read()
            if conn:
                cnx.execute(query_register, (name_user, email_user, dt_nascimento_user, password_hashed, tel_user))
                conn.commit()
                return jsonify({'message': 'Usuário criado com sucesso!'})
            
    except Exception as e:
        return jsonify({'error': f"Erro ao registrar usuário: {e}"}), 500
    
    finally:
        if cnx and conn:
            cnx.close()
            conn.close()

    return "Esta é a página de registro. Use o método POST para enviar seus dados."

@users_bp.route('/login', methods=['POST','GET'])
def login():
    conn = None
    cnx = None
    try:
        if request.method == 'POST':
            conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
            cnx = conn.cursor()
            email_user = request.json.get('email_user')
            password = request.json.get('password')
            password_hashed = hash_password(password)
            if not all([email_user, password]):
                return jsonify({'error': 'Email e senha são obrigatórios'}), 400
            with open ('./sql/query_login.sql','r') as r:
                query_login = r.read()
            if conn:
                cnx.execute(query_login, (email_user,))
                user_record = cnx.fetchone()
                if user_record is None:
                    return jsonify({'error': 'Email ou senha inválidos'}), 401
                password_matches = bcrypt.check_password_hash(user_record[2], password)
            if password_matches:
                return jsonify({
                    'message': 'Login realizado com sucesso',
                    'user_id': user_record[0],
                    'email': user_record[1]
                }), 200
            else:
                return jsonify({'error': 'Email ou senha inválidos'}), 401
    except Exception as e:
        return jsonify({'error':f"Erro ao realizar login.{e}"}),500
    finally:
        if cnx and conn:
            cnx.close()
            conn.close()
    return "Página de login"