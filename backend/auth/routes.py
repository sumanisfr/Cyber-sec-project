import re
import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

from database import execute
from extensions import limiter, csrf

auth_bp = Blueprint('auth', __name__)

# Allow usernames or email-like identifiers (allows @ +) to support common login patterns
USERNAME_RE = re.compile(r'^[a-zA-Z0-9_.@+-]{4,64}$')


def _get_user(username):
    row = execute(
        'SELECT id, username, password, role, tenant_id, full_name, bio, avatar_url, google_url, facebook_url, linkedin_url, github_url '
        'FROM users WHERE username = %s',
        (username,),
        fetchone=True,
    )
    return dict(row) if row else None


def _serialize_profile(user):
    return {
        'username': user['username'],
        'role': user['role'],
        'tenant_id': user.get('tenant_id', 'default'),
        'full_name': user.get('full_name') or '',
        'bio': user.get('bio') or '',
        'avatar_url': user.get('avatar_url') or '',
        'social_links': {
            'google': user.get('google_url') or '',
            'facebook': user.get('facebook_url') or '',
            'linkedin': user.get('linkedin_url') or '',
            'github': user.get('github_url') or '',
        },
    }


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def _require_admin(fn):
    from functools import wraps

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)

    return wrapper


@auth_bp.route('/register', methods=['POST'])
@csrf.exempt
def register():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    full_name = (data.get('full_name') or '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if not USERNAME_RE.match(username):
        return jsonify({'error': 'Username must be 4-64 characters and can include letters, numbers, . _ @ + -'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    if _get_user(username):
        return jsonify({'error': 'User already exists'}), 400

    tenant_id = (data.get('tenant_id') or 'default').strip() or 'default'
    hashed = _hash_password(password)
    execute(
        'INSERT INTO users (username, password, role, tenant_id, full_name) VALUES (%s, %s, %s, %s, %s)',
        (username, hashed, 'user', tenant_id, full_name),
        commit=True
    )

    return jsonify({'message': 'User registered'})


@auth_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
@csrf.exempt
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    user = _get_user(username)
    if not user or not _verify_password(password, user['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(
        identity=username,
        additional_claims={
            'role': user.get('role', 'user'),
            'tenant_id': user.get('tenant_id', 'default'),
        },
    )
    return jsonify({'token': access_token})


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    username = get_jwt_identity()
    user = _get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(_serialize_profile(user))


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
@csrf.exempt
def update_profile():
    username = get_jwt_identity()
    user = _get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    social_links = data.get('social_links') or {}
    full_name = (data.get('full_name') or '').strip()
    bio = (data.get('bio') or '').strip()
    avatar_url = (data.get('avatar_url') or '').strip()

    execute(
        'UPDATE users SET full_name = %s, bio = %s, avatar_url = %s, google_url = %s, facebook_url = %s, linkedin_url = %s, github_url = %s WHERE username = %s',
        (
            full_name,
            bio,
            avatar_url,
            (social_links.get('google') or '').strip(),
            (social_links.get('facebook') or '').strip(),
            (social_links.get('linkedin') or '').strip(),
            (social_links.get('github') or '').strip(),
            username,
        ),
        commit=True,
    )

    updated_user = _get_user(username)
    return jsonify({'message': 'Profile updated', 'profile': _serialize_profile(updated_user)})


@auth_bp.route('/admin/users', methods=['GET'])
@_require_admin
def list_users():
    rows = execute('SELECT id, username, role, tenant_id, created_at FROM users ORDER BY created_at DESC', fetchall=True)
    users = [dict(r) for r in rows] if rows else []
    return jsonify({'users': users})
