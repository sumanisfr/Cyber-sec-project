from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from database import execute
from extensions import csrf
from job_scam_analyzer import analyze_job_text

job_scam_bp = Blueprint('job_scam', __name__)


@job_scam_bp.route('/check', methods=['POST'])
@csrf.exempt
def check_job_post():
    data = request.get_json() or {}
    content = data.get('content', '')
    title = (data.get('title') or '').strip()

    verify_jwt_in_request(optional=True)
    jwt_claims = get_jwt()
    tenant_id = jwt_claims.get('tenant_id', 'default')
    username = jwt_claims.get('sub', 'guest')

    analysis = analyze_job_text(content)
    analysis['title'] = title or 'Untitled job post'

    check_id = execute(
        'INSERT INTO job_scam_checks (tenant_id, username, title, content, score, risk_level, created_at) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)',
        (
            tenant_id,
            username,
            analysis['title'],
            content,
            analysis['score'],
            analysis['risk_level'],
        ),
        commit=True,
        return_lastrowid=True,
    )
    analysis['check_id'] = check_id
    return jsonify(analysis)
