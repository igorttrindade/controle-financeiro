from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from backend.api.security.token_store import is_jti_revoked

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'message': 'Token malformatado!'}), 401

        token = parts[1]
        if not token:
            return jsonify({'message': 'Token ausente!'}), 401

        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"],
                issuer=current_app.config['JWT_ISSUER'],
                audience=current_app.config['JWT_AUDIENCE'],
                options={'require': ['exp', 'iat', 'nbf', 'iss', 'aud', 'jti', 'sub']},
            )
            if is_jti_revoked(data['jti']):
                return jsonify({'message': 'Token revogado! Faça login novamente.'}), 401
            current_user_id = int(data['sub'])
            g.jwt_payload = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado! Faça login novamente.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        except Exception:
            return jsonify({'message': 'Erro interno no servidor'}), 500
        return f(current_user_id, *args, **kwargs)

    return decorated
