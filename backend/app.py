from pathlib import Path

from flask import Flask
from flask_cors import CORS
from backend.db.connection import get_db_connection
from backend.api.routes.users import users_bp
from backend.api.routes.transactions import transaction_bp
from backend.api.routes.dashboard import dashboard_bp
from backend.api.routes.subscriptions import subscription_bp
from backend.core.extensions import bcrypt
from backend.core.config import DATABASE_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
bcrypt.init_app(app)
app.config['DATABASE_CONFIG'] = DATABASE_CONFIG
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_ISSUER'] = os.getenv('JWT_ISSUER', 'controle-financeiro-api')
app.config['JWT_AUDIENCE'] = os.getenv('JWT_AUDIENCE', 'controle-financeiro-web')
app.config['REGISTER_RATE_LIMIT_MAX'] = int(os.getenv('REGISTER_RATE_LIMIT_MAX', '5'))
app.config['REGISTER_RATE_LIMIT_WINDOW_SECONDS'] = int(os.getenv('REGISTER_RATE_LIMIT_WINDOW_SECONDS', '900'))
app.config['LOGIN_RATE_LIMIT_MAX'] = int(os.getenv('LOGIN_RATE_LIMIT_MAX', '10'))
app.config['LOGIN_RATE_LIMIT_WINDOW_SECONDS'] = int(os.getenv('LOGIN_RATE_LIMIT_WINDOW_SECONDS', '900'))
app.config['LOGIN_LOCKOUT_THRESHOLD'] = int(os.getenv('LOGIN_LOCKOUT_THRESHOLD', '5'))
app.config['LOGIN_LOCKOUT_WINDOW_SECONDS'] = int(os.getenv('LOGIN_LOCKOUT_WINDOW_SECONDS', '900'))
app.config['LOGIN_LOCKOUT_DURATION_SECONDS'] = int(os.getenv('LOGIN_LOCKOUT_DURATION_SECONDS', '900'))
app.config['MAX_AVATAR_BYTES'] = int(os.getenv('MAX_AVATAR_BYTES', str(2 * 1024 * 1024)))
app.config['SECURITY_PENDING_EXPIRATION_MINUTES'] = int(
    os.getenv('SECURITY_PENDING_EXPIRATION_MINUTES', '30')
)
app.config['APP_TIMEZONE'] = os.getenv('APP_TIMEZONE', 'America/Sao_Paulo')
app.config['CAKTO_WEBHOOK_SECRET'] = os.getenv('CAKTO_WEBHOOK_SECRET', '')
app.config['CAKTO_PRODUCT_CHECKOUT_URL'] = os.getenv('CAKTO_PRODUCT_CHECKOUT_URL', '')


def ensure_profile_schema():
    sql_dir = Path(__file__).resolve().parent / "sql"
    db_migration_dir = Path(__file__).resolve().parent / "db" / "migrations"
    migration_files = [
        sql_dir / "create_user_profile_tables.sql",
        sql_dir / "alter_user_profile_add_monthly_goal.sql",
        db_migration_dir / "20260309_add_subscriptions.sql",
        db_migration_dir / "20260309_add_webhook_logs.sql",
    ]

    conn = None
    cur = None
    try:
        conn = get_db_connection(app.config['DATABASE_CONFIG'])
        if not conn:
            app.logger.warning("Não foi possível validar schema de perfil: conexão indisponível")
            return
        cur = conn.cursor()

        for migration_file in migration_files:
            if not migration_file.exists():
                app.logger.warning("Arquivo de migração não encontrado: %s", migration_file)
                continue
            cur.execute(migration_file.read_text(encoding="utf-8"))

        conn.commit()
        app.logger.info("Schema de perfil validado/criado com sucesso.")
    except Exception:
        if conn:
            conn.rollback()
        app.logger.exception("Falha ao validar/criar schema de perfil.")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


ensure_profile_schema()

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
app.register_blueprint(transaction_bp, url_prefix='/api/transaction')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(subscription_bp, url_prefix='/api/subscription')

if __name__ == '__main__':
    conn = get_db_connection(app.config['DATABASE_CONFIG'])
    if conn:
        print("Conexão com o banco de dados estabelecida.")
        conn.close()
    debug_mode = os.getenv('FLASK_DEBUG', '0').strip().lower() in {'1', 'true', 'yes', 'on'}
    app.run(debug=debug_mode)
