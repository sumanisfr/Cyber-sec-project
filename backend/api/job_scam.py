from flask import Blueprint, jsonify, request

from extensions import csrf
from job_scam_analyzer import analyze_job_text

job_scam_bp = Blueprint('job_scam', __name__)


@job_scam_bp.route('/check', methods=['POST'])
@csrf.exempt
def check_job_post():
    data = request.get_json() or {}
    content = data.get('content', '')
    title = (data.get('title') or '').strip()

    analysis = analyze_job_text(content)
    analysis['title'] = title or 'Untitled job post'
    return jsonify(analysis)
