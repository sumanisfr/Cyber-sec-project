import json

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from database import execute
from scanner.vuln_scan import run_scan
from extensions import csrf
from realtime import publish_dashboard_update

vuln_bp = Blueprint('vuln', __name__)


@vuln_bp.route('/scan', methods=['POST'])
@jwt_required()
@csrf.exempt
def scan_website():
    data = request.get_json() or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL missing'}), 400

    jwt_claims = get_jwt()
    tenant_id = jwt_claims.get('tenant_id', 'default')
    username = jwt_claims.get('sub')

    report = run_scan(url)

    # Store report in the database
    execute(
        'INSERT INTO vuln_reports (tenant_id, username, url, report) VALUES (%s, %s, %s, %s)',
        (tenant_id, username, url, json.dumps(report)),
        commit=True,
    )

    publish_dashboard_update({'type': 'vuln-scan-complete', 'tenant_id': tenant_id})

    return jsonify(report)


@vuln_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    tenant_id = get_jwt().get('tenant_id', 'default')
    rows = execute(
        'SELECT id, url, scanned_at FROM vuln_reports WHERE tenant_id = %s ORDER BY scanned_at DESC LIMIT 100',
        (tenant_id,),
        fetchall=True,
    )
    history = [dict(r) for r in rows] if rows else []
    return jsonify({'history': history})


@vuln_bp.route('/report/<int:report_id>', methods=['GET'])
@jwt_required()
def report(report_id):
    tenant_id = get_jwt().get('tenant_id', 'default')
    row = execute('SELECT * FROM vuln_reports WHERE id = %s AND tenant_id = %s', (report_id, tenant_id), fetchone=True)
    if not row:
        return jsonify({'error': 'Report not found'}), 404
    record = dict(row)
    # JSON stored as string in sqlite; decode if necessary
    try:
        record['report'] = json.loads(record['report'])
    except Exception:
        pass
    return jsonify(record)
