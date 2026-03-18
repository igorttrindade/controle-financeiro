import datetime
import re
import time
import uuid
from collections import defaultdict, deque
from decimal import Decimal, InvalidOperation
from pathlib import Path
from threading import Lock

import jwt
import psycopg2
from flask import Blueprint, Response, current_app, g, jsonify, request

from backend.api.middlewares.auth import token_required
from backend.api.routes.dashboard import invalidate_dashboard_cache
from backend.api.security.token_store import revoke_jti
from backend.core.extensions import bcrypt
from backend.db.connection import get_db_connection
from backend.services.subscription_service import ensure_free_subscription_for_user

users_bp = Blueprint('users', __name__)
SQL_DIR = Path(__file__).resolve().parent.parent.parent / 'sql'
RATE_LIMIT_LOCK = Lock()
RATE_LIMIT_BUCKETS = defaultdict(deque)
LOGIN_FAILURE_BUCKETS = defaultdict(deque)
LOGIN_LOCKOUTS = {}
ALLOWED_THEMES = {'light', 'dark'}
ALLOWED_AVATAR_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
PASSWORD_POLICY_REGEX = re.compile(r'^(?=.*[A-Za-z])(?=.*\d).{8,}$')


def hash_password(password):
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed


def read_sql_file(filename):
    return (SQL_DIR / filename).read_text(encoding='utf-8')


def _client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def _prune_bucket(bucket, window_seconds, now):
    cutoff = now - window_seconds
    while bucket and bucket[0] <= cutoff:
        bucket.popleft()


def _consume_rate_limit(scope_key, max_requests, window_seconds):
    now = time.time()
    with RATE_LIMIT_LOCK:
        bucket = RATE_LIMIT_BUCKETS[scope_key]
        _prune_bucket(bucket, window_seconds, now)
        if len(bucket) >= max_requests:
            retry_after = int(max(1, window_seconds - (now - bucket[0])))
            return False, retry_after
        bucket.append(now)
        return True, 0


def _register_failed_login(login_key, threshold, window_seconds, lockout_seconds):
    now = time.time()
    with RATE_LIMIT_LOCK:
        failure_bucket = LOGIN_FAILURE_BUCKETS[login_key]
        _prune_bucket(failure_bucket, window_seconds, now)
        failure_bucket.append(now)
        if len(failure_bucket) >= threshold:
            LOGIN_LOCKOUTS[login_key] = now + lockout_seconds
            failure_bucket.clear()


def _clear_login_failures(login_key):
    with RATE_LIMIT_LOCK:
        LOGIN_FAILURE_BUCKETS.pop(login_key, None)
        LOGIN_LOCKOUTS.pop(login_key, None)


def _check_lockout(login_key):
    now = time.time()
    with RATE_LIMIT_LOCK:
        locked_until = LOGIN_LOCKOUTS.get(login_key)
        if not locked_until:
            return False, 0
        if locked_until <= now:
            LOGIN_LOCKOUTS.pop(login_key, None)
            return False, 0
        return True, int(max(1, locked_until - now))


def _ensure_profile_row(cur, user_id):
    cur.execute(
        """
        INSERT INTO tb_user_profile (id_user_fk, theme, updated_at)
        VALUES (%s, 'light', CURRENT_TIMESTAMP)
        ON CONFLICT (id_user_fk) DO NOTHING;
        """,
        (user_id,),
    )


def _fetch_profile(cur, user_id):
    _ensure_profile_row(cur, user_id)
    try:
        cur.execute(
            """
            SELECT
                u.id_user,
                u.nome_user,
                u.email_user,
                u.tel_user,
                p.theme,
                p.avatar_mime_type,
                p.avatar_updated_at,
                p.avatar_bytes IS NOT NULL AS has_avatar,
                p.monthly_goal_value
            FROM tb_user u
            JOIN tb_user_profile p ON p.id_user_fk = u.id_user
            WHERE u.id_user = %s
            LIMIT 1;
            """,
            (user_id,),
        )
    except psycopg2.errors.UndefinedColumn:
        cur.connection.rollback()
        _ensure_profile_row(cur, user_id)
        cur.execute(
            """
            SELECT
                u.id_user,
                u.nome_user,
                u.email_user,
                u.tel_user,
                p.theme,
                p.avatar_mime_type,
                p.avatar_updated_at,
                p.avatar_bytes IS NOT NULL AS has_avatar,
                NULL::NUMERIC AS monthly_goal_value
            FROM tb_user u
            JOIN tb_user_profile p ON p.id_user_fk = u.id_user
            WHERE u.id_user = %s
            LIMIT 1;
            """,
            (user_id,),
        )
    return cur.fetchone()


def _update_profile_preferences(cur, user_id, theme, monthly_goal_value):
    cur.execute("SAVEPOINT profile_preferences;")
    try:
        cur.execute(
            """
            UPDATE tb_user_profile
            SET theme = %s,
                monthly_goal_value = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_user_fk = %s;
            """,
            (theme, monthly_goal_value, user_id),
        )
        cur.execute("RELEASE SAVEPOINT profile_preferences;")
        return True
    except psycopg2.errors.UndefinedColumn:
        cur.execute("ROLLBACK TO SAVEPOINT profile_preferences;")
        cur.execute(
            """
            UPDATE tb_user_profile
            SET theme = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_user_fk = %s;
            """,
            (theme, user_id),
        )
        cur.execute("RELEASE SAVEPOINT profile_preferences;")
        return False


def _normalize_theme(raw_theme):
    theme = str(raw_theme or '').strip().lower()
    if theme in ALLOWED_THEMES:
        return theme
    return None


def _is_valid_phone(phone):
    if phone is None:
        return True
    normalized = str(phone).strip()
    if not normalized:
        return True
    return bool(re.fullmatch(r'[0-9+()\-\s]{8,20}', normalized))


def _is_password_strong(password):
    return bool(PASSWORD_POLICY_REGEX.fullmatch(str(password or '')))


def _safe_invalidate_dashboard_cache(user_id):
    try:
        invalidate_dashboard_cache(user_id)
    except Exception:
        current_app.logger.warning(
            "Falha ao invalidar cache de dashboard para user_id=%s", user_id
        )


@users_bp.route('/register', methods=['POST'])
def register():
    conn = None
    cnx = None
    try:
        data = request.get_json(silent=True) or {}
        name_user = data.get('name_user')
        email_user = data.get('email_user')
        dt_nascimento_user = data.get('dt_nascimento_user')
        tel_user = data.get('tel_user')
        password = data.get('password')

        if not all([name_user, email_user, password]):
            return jsonify({'error': 'Dados incompletos'}), 400

        email_normalized = email_user.strip().lower()
        register_max = current_app.config['REGISTER_RATE_LIMIT_MAX']
        register_window = current_app.config['REGISTER_RATE_LIMIT_WINDOW_SECONDS']

        allowed_by_ip, retry_after_ip = _consume_rate_limit(
            f'register:ip:{_client_ip()}',
            register_max,
            register_window,
        )
        if not allowed_by_ip:
            return (
                jsonify({'error': 'Muitas tentativas de cadastro. Tente novamente mais tarde.'}),
                429,
                {'Retry-After': str(retry_after_ip)},
            )

        allowed_by_email, retry_after_email = _consume_rate_limit(
            f'register:email:{email_normalized}',
            register_max,
            register_window,
        )
        if not allowed_by_email:
            return (
                jsonify({'error': 'Muitas tentativas de cadastro. Tente novamente mais tarde.'}),
                429,
                {'Retry-After': str(retry_after_email)},
            )

        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cnx = conn.cursor()
        password_hashed = hash_password(password)

        query_register = read_sql_file('query_register_user.sql')
        cnx.execute(query_register, (name_user, email_user, dt_nascimento_user, password_hashed, tel_user))
        created_user = cnx.fetchone()
        if not created_user:
            conn.rollback()
            return jsonify({'error': 'Erro ao criar usuário'}), 500

        ensure_free_subscription_for_user(int(created_user[0]), conn=conn, cur=cnx)
        conn.commit()
        return jsonify({'message': 'Usuário criado com sucesso!'}), 201

    except psycopg2.errors.UniqueViolation:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Este e-mail já está cadastrado.'}), 409
    except Exception:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Erro interno no servidor'}), 500

    finally:
        if cnx and conn:
            cnx.close()
            conn.close()


@users_bp.route('/login', methods=['POST'])
def login():
    conn = None
    cnx = None
    try:
        data = request.get_json(silent=True) or {}
        email_user = data.get('email_user')
        password = data.get('password')
        if not all([email_user, password]):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400

        email_normalized = email_user.strip().lower()
        ip_address = _client_ip()
        login_key = f'{email_normalized}|{ip_address}'

        is_locked, lockout_retry = _check_lockout(login_key)
        if is_locked:
            return (
                jsonify({'error': 'Conta temporariamente bloqueada por excesso de tentativas.'}),
                429,
                {'Retry-After': str(lockout_retry)},
            )

        login_max = current_app.config['LOGIN_RATE_LIMIT_MAX']
        login_window = current_app.config['LOGIN_RATE_LIMIT_WINDOW_SECONDS']
        allowed, retry_after = _consume_rate_limit(
            f'login:{login_key}',
            login_max,
            login_window,
        )
        if not allowed:
            return (
                jsonify({'error': 'Muitas tentativas de login. Tente novamente mais tarde.'}),
                429,
                {'Retry-After': str(retry_after)},
            )

        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cnx = conn.cursor()
        query_login = read_sql_file('query_login_user.sql')
        cnx.execute(query_login, (email_user,))
        user_record = cnx.fetchone()
        if user_record is None:
            _register_failed_login(
                login_key,
                current_app.config['LOGIN_LOCKOUT_THRESHOLD'],
                current_app.config['LOGIN_LOCKOUT_WINDOW_SECONDS'],
                current_app.config['LOGIN_LOCKOUT_DURATION_SECONDS'],
            )
            return jsonify({'error': 'Email ou senha inválidos'}), 401

        password_matches = bcrypt.check_password_hash(user_record[2], password)
        if not password_matches:
            _register_failed_login(
                login_key,
                current_app.config['LOGIN_LOCKOUT_THRESHOLD'],
                current_app.config['LOGIN_LOCKOUT_WINDOW_SECONDS'],
                current_app.config['LOGIN_LOCKOUT_DURATION_SECONDS'],
            )
            return jsonify({'error': 'Email ou senha inválidos'}), 401

        _clear_login_failures(login_key)

        now = datetime.datetime.now(datetime.timezone.utc)
        expires_at = now + datetime.timedelta(hours=24)
        token_payload = {
            'sub': str(user_record[0]),
            'user_id': user_record[0],
            'jti': str(uuid.uuid4()),
            'iat': now,
            'nbf': now,
            'exp': expires_at,
            'iss': current_app.config['JWT_ISSUER'],
            'aud': current_app.config['JWT_AUDIENCE'],
        }
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')

        return (
            jsonify({'message': 'Login realizado com sucesso', 'token': token, 'user_id': user_record[0]}),
            200,
        )
    except Exception:
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cnx and conn:
            cnx.close()
            conn.close()


@users_bp.route('/me/profile', methods=['GET'])
@token_required
def get_my_profile(current_user_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503

        cur = conn.cursor()
        row = _fetch_profile(cur, current_user_id)
        if not row:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        return (
            jsonify(
                {
                    'id_user': row[0],
                    'name_user': row[1],
                    'email_user': row[2],
                    'tel_user': row[3] or '',
                    'theme': row[4],
                    'avatar_mime_type': row[5],
                    'avatar_updated_at': row[6].isoformat() if row[6] else None,
                    'has_avatar': bool(row[7]),
                    'monthly_goal_value': float(row[8]) if row[8] is not None else None,
                }
            ),
            200,
        )
    except Exception:
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@users_bp.route('/me/profile', methods=['PATCH'])
@token_required
def update_my_profile(current_user_id):
    data = request.get_json(silent=True) or {}
    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503

        cur = conn.cursor()
        row = _fetch_profile(cur, current_user_id)
        if not row:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        current_name, current_tel, current_theme, current_goal = row[1], row[3] or '', row[4], row[8]
        incoming_name = data.get('name_user')
        incoming_tel = data.get('tel_user')
        incoming_theme = data.get('theme')
        has_goal_in_payload = 'monthly_goal_value' in data
        incoming_goal = data.get('monthly_goal_value') if has_goal_in_payload else current_goal

        next_name = current_name
        if incoming_name is not None:
            candidate_name = str(incoming_name).strip()
            if len(candidate_name) < 2 or len(candidate_name) > 120:
                return jsonify({'error': 'O nome deve ter entre 2 e 120 caracteres'}), 400
            next_name = candidate_name

        next_tel = current_tel
        if incoming_tel is not None:
            candidate_tel = str(incoming_tel).strip()
            if not _is_valid_phone(candidate_tel):
                return jsonify({'error': 'Telefone inválido'}), 400
            next_tel = candidate_tel

        next_theme = current_theme
        if incoming_theme is not None:
            normalized_theme = _normalize_theme(incoming_theme)
            if not normalized_theme:
                return jsonify({'error': 'Tema inválido'}), 400
            next_theme = normalized_theme

        next_goal = current_goal
        if incoming_goal is None or (isinstance(incoming_goal, str) and not incoming_goal.strip()):
            next_goal = None
        else:
            try:
                parsed_goal = Decimal(str(incoming_goal))
            except (InvalidOperation, TypeError, ValueError):
                return jsonify({'error': 'Meta mensal inválida'}), 400

            if parsed_goal <= 0 or parsed_goal > Decimal('100000000'):
                return jsonify({'error': 'Meta mensal deve ser maior que zero e menor que 100000000'}), 400

            next_goal = parsed_goal

        goal_supported = _update_profile_preferences(cur, current_user_id, next_theme, next_goal)
        if has_goal_in_payload and not goal_supported:
            conn.rollback()
            return (
                jsonify(
                    {
                        'error': (
                            'Meta mensal indisponível no momento. '
                            'Execute a migração alter_user_profile_add_monthly_goal.sql.'
                        )
                    }
                ),
                503,
            )

        cur.execute(
            """
            UPDATE tb_user
            SET nome_user = %s,
                tel_user = %s
            WHERE id_user = %s;
            """,
            (next_name, next_tel, current_user_id),
        )

        conn.commit()
        if has_goal_in_payload:
            _safe_invalidate_dashboard_cache(current_user_id)
        return (
            jsonify(
                {
                    'message': 'Perfil atualizado com sucesso',
                    'name_user': next_name,
                    'tel_user': next_tel,
                    'theme': next_theme,
                    'monthly_goal_value': float(next_goal) if next_goal is not None else None,
                }
            ),
            200,
        )
    except Exception:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@users_bp.route('/me/avatar', methods=['POST'])
@token_required
def upload_avatar(current_user_id):
    conn = None
    cur = None
    try:
        avatar = request.files.get('avatar')
        if not avatar:
            return jsonify({'error': 'Arquivo de avatar é obrigatório'}), 400

        mime_type = str(avatar.mimetype or '').lower()
        if mime_type not in ALLOWED_AVATAR_MIME_TYPES:
            return jsonify({'error': 'Tipo de arquivo inválido. Use JPG, PNG ou WebP.'}), 400

        avatar_bytes = avatar.read()
        if not avatar_bytes:
            return jsonify({'error': 'Arquivo vazio'}), 400

        max_bytes = current_app.config['MAX_AVATAR_BYTES']
        if len(avatar_bytes) > max_bytes:
            return jsonify({'error': 'Arquivo excede o limite de 2MB'}), 413

        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503

        cur = conn.cursor()
        _ensure_profile_row(cur, current_user_id)
        cur.execute(
            """
            UPDATE tb_user_profile
            SET avatar_bytes = %s,
                avatar_mime_type = %s,
                avatar_updated_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_user_fk = %s;
            """,
            (psycopg2.Binary(avatar_bytes), mime_type, current_user_id),
        )
        conn.commit()
        return jsonify({'message': 'Avatar atualizado com sucesso'}), 200
    except (psycopg2.errors.UndefinedTable, psycopg2.errors.UndefinedColumn):
        if conn:
            conn.rollback()
        return (
            jsonify(
                {
                    'error': (
                        'Estrutura de perfil/avatar não encontrada no banco. '
                        'Execute a migração create_user_profile_tables.sql.'
                    )
                }
            ),
            500,
        )
    except Exception:
        if conn:
            conn.rollback()
        current_app.logger.exception("Erro ao enviar avatar para user_id=%s", current_user_id)
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@users_bp.route('/me/avatar', methods=['GET'])
@token_required
def get_avatar(current_user_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503

        cur = conn.cursor()
        _ensure_profile_row(cur, current_user_id)
        cur.execute(
            """
            SELECT avatar_bytes, avatar_mime_type
            FROM tb_user_profile
            WHERE id_user_fk = %s
            LIMIT 1;
            """,
            (current_user_id,),
        )
        row = cur.fetchone()
        if not row or not row[0]:
            return jsonify({'error': 'Avatar não encontrado'}), 404

        response = Response(row[0], mimetype=row[1] or 'application/octet-stream')
        response.headers['Cache-Control'] = 'no-store'
        return response
    except Exception:
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@users_bp.route('/me/avatar', methods=['DELETE'])
@token_required
def delete_avatar(current_user_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503

        cur = conn.cursor()
        _ensure_profile_row(cur, current_user_id)
        cur.execute(
            """
            UPDATE tb_user_profile
            SET avatar_bytes = NULL,
                avatar_mime_type = NULL,
                avatar_updated_at = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id_user_fk = %s;
            """,
            (current_user_id,),
        )
        conn.commit()
        return jsonify({'message': 'Avatar removido com sucesso'}), 200
    except Exception:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@users_bp.route('/me/security/request', methods=['POST'])
@token_required
def request_security_change(current_user_id):
    data = request.get_json(silent=True) or {}
    change_type = str(data.get('change_type') or '').strip().lower()

    if change_type not in {'email_change', 'password_change'}:
        return jsonify({'error': 'Tipo de alteração inválido'}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503

        cur = conn.cursor()
        new_email = None
        new_password_hash = None

        if change_type == 'email_change':
            candidate_email = str(data.get('new_email') or '').strip().lower()
            if not candidate_email or '@' not in candidate_email:
                return jsonify({'error': 'Novo e-mail inválido'}), 400

            cur.execute(
                """
                SELECT 1 FROM tb_user
                WHERE LOWER(email_user) = LOWER(%s)
                  AND id_user <> %s
                LIMIT 1;
                """,
                (candidate_email, current_user_id),
            )
            if cur.fetchone():
                return jsonify({'error': 'Este e-mail já está em uso'}), 409
            new_email = candidate_email

        if change_type == 'password_change':
            candidate_password = str(data.get('new_password') or '')
            if not _is_password_strong(candidate_password):
                return jsonify({'error': 'Senha deve ter no mínimo 8 caracteres, com letras e números'}), 400
            new_password_hash = hash_password(candidate_password)

        expires_minutes = current_app.config['SECURITY_PENDING_EXPIRATION_MINUTES']
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes)
        token = str(uuid.uuid4())

        cur.execute(
            """
            INSERT INTO tb_user_security_pending (
                id_user_fk, change_type, new_email, new_password_hash, token, expires_at
            )
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (current_user_id, change_type, new_email, new_password_hash, token, expires_at),
        )
        conn.commit()

        return (
            jsonify(
                {
                    'message': 'Solicitação criada com sucesso',
                    'token': token,
                    'confirmation_url': f'/profile?tab=security&token={token}',
                    'expires_at': expires_at.isoformat() + 'Z',
                }
            ),
            200,
        )
    except Exception:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@users_bp.route('/me/security/confirm', methods=['POST'])
@token_required
def confirm_security_change(current_user_id):
    data = request.get_json(silent=True) or {}
    token = str(data.get('token') or '').strip()
    if not token:
        return jsonify({'error': 'Token de confirmação é obrigatório'}), 400

    conn = None
    cur = None
    try:
        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503

        cur = conn.cursor()
        cur.execute(
            """
            SELECT id_pending, change_type, new_email, new_password_hash, expires_at, used_at
            FROM tb_user_security_pending
            WHERE token = %s
              AND id_user_fk = %s
            LIMIT 1;
            """,
            (token, current_user_id),
        )
        pending = cur.fetchone()
        if not pending:
            return jsonify({'error': 'Solicitação não encontrada'}), 404

        pending_id, change_type, new_email, new_password_hash, expires_at, used_at = pending
        if used_at is not None:
            return jsonify({'error': 'Token já utilizado'}), 410

        if expires_at <= datetime.datetime.utcnow():
            return jsonify({'error': 'Token expirado'}), 410

        if change_type == 'email_change':
            cur.execute(
                """
                SELECT 1 FROM tb_user
                WHERE LOWER(email_user) = LOWER(%s)
                  AND id_user <> %s
                LIMIT 1;
                """,
                (new_email, current_user_id),
            )
            if cur.fetchone():
                return jsonify({'error': 'Este e-mail já está em uso'}), 409

            cur.execute(
                """
                UPDATE tb_user
                SET email_user = %s
                WHERE id_user = %s;
                """,
                (new_email, current_user_id),
            )

        if change_type == 'password_change':
            cur.execute(
                """
                UPDATE tb_user
                SET password_hash_user = %s
                WHERE id_user = %s;
                """,
                (new_password_hash, current_user_id),
            )

        cur.execute(
            """
            UPDATE tb_user_security_pending
            SET used_at = CURRENT_TIMESTAMP
            WHERE id_pending = %s;
            """,
            (pending_id,),
        )

        conn.commit()
        return jsonify({'message': 'Alteração de segurança confirmada com sucesso'}), 200
    except Exception:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@users_bp.route('/<id_user>', methods=['DELETE'])
@token_required
def delete_user(current_user_id, id_user):
    conn = None
    cnx = None
    try:
        try:
            target_user_id = int(id_user)
        except ValueError:
            return jsonify({'error': 'ID de usuário inválido'}), 400

        if current_user_id != target_user_id:
            return jsonify({'error': 'Acesso negado: você só pode excluir sua própria conta'}), 403

        data = request.get_json(silent=True) or {}
        current_password = data.get('password')
        if not current_password:
            return jsonify({'error': 'Senha atual é obrigatória para excluir a conta'}), 400

        conn = get_db_connection(current_app.config['DATABASE_CONFIG'])
        if not conn:
            return jsonify({'error': 'Serviço temporariamente indisponível'}), 503
        cnx = conn.cursor()

        cnx.execute('SELECT password_hash_user FROM tb_user WHERE id_user = %s', (target_user_id,))
        user_row = cnx.fetchone()
        if not user_row:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        if not bcrypt.check_password_hash(user_row[0], current_password):
            return jsonify({'error': 'Senha atual inválida'}), 403

        query_delete = read_sql_file('query_delete_user.sql')
        cnx.execute(query_delete, (target_user_id,))

        if cnx.rowcount == 0:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        conn.commit()
        return jsonify({'success': 'Usuário deletado com sucesso!'}), 200
    except psycopg2.errors.ForeignKeyViolation:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Não foi possível deletar o usuário'}), 400
    except Exception:
        if conn:
            conn.rollback()
        return jsonify({'error': 'Erro interno no servidor'}), 500
    finally:
        if cnx:
            cnx.close()
        if conn:
            conn.close()


@users_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user_id):
    payload = getattr(g, 'jwt_payload', None)
    if not payload:
        return jsonify({'error': 'Token inválido!'}), 401

    revoke_jti(payload['jti'], payload['exp'])
    return jsonify({'message': 'Logout realizado com sucesso.'}), 200
