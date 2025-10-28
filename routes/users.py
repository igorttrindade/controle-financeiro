from database.connection import get_db_connection
from flask import request, jsonify, Blueprint, current_app
from extensions import bcrypt
import psycopg2

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

            with open ('./sql/query_register_user.sql', 'r') as r:
                query_register = r.read()
            if conn:
                cnx.execute(query_register, (name_user, email_user, dt_nascimento_user, password_hashed, tel_user))
                conn.commit()
                return jsonify({'message': 'Usuário criado com sucesso!'})
            
    except psycopg2.errors.UniqueViolation as e:
        return jsonify({'error': f'Usuário já registrado.'}),409
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
            if not all([email_user, password]):
                return jsonify({'error': 'Email e senha são obrigatórios'}), 400
            with open ('./sql/query_login_user.sql','r') as r:
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
                        'user_id': user_record[0]}), 200
                else:
                    return jsonify({'error': 'Email ou senha inválidos'}), 401
    except Exception as e:
        return jsonify({'error':f"Erro ao realizar login.{e}"}),500
    finally:
        if cnx and conn:
            cnx.close()
            conn.close()
    return "Página de login"

@users_bp.route('/<id_user>', methods=['DELETE'])
def delete_user(id_user):
    conn = None
    cnx = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        cnx = conn.cursor()
        with open('./sql/query_delete_user.sql','r') as r:
            query_delete = r.read()
        if conn:
            cnx.execute(query_delete, (id_user,))

            if cnx.rowcount == 0:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            conn.commit()
        return jsonify({'sucess':'Usuário deletado com sucesso!'}), 200
    except psycopg2.errors.ForeignKeyViolation as err:
        return jsonify({'error':f'Erro ao deletar usuário: {err}'}),400
    except Exception as e:
        return jsonify({'error': f"Erro no servidor: {e}"}), 500
    finally:
        if cnx:
            cnx.close()
        if conn:
            conn.close()
