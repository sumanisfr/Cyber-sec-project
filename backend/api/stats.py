from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from database import execute

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/summary', methods=['GET'])
def summary():
    """Return dashboard summary statistics scoped to the current tenant."""
    verify_jwt_in_request(optional=True)
    tenant_id = get_jwt().get('tenant_id')

    if tenant_id:
        scans = execute('SELECT COUNT(*) as cnt FROM malware_scans WHERE tenant_id = %s', (tenant_id,), fetchone=True)
        vuln_reports = execute('SELECT COUNT(*) as cnt FROM vuln_reports WHERE tenant_id = %s', (tenant_id,), fetchone=True)
        malware = execute(
            'SELECT COUNT(*) as cnt FROM malware_scans WHERE tenant_id = %s AND status = %s',
            (tenant_id, 'MALICIOUS'),
            fetchone=True,
        )
        fraud_detected = execute(
            'SELECT COUNT(*) as cnt FROM malware_scans WHERE tenant_id = %s AND fraud_detected = TRUE',
            (tenant_id,),
            fetchone=True,
        )
    else:
        scans = execute('SELECT COUNT(*) as cnt FROM malware_scans', fetchone=True)
        vuln_reports = execute('SELECT COUNT(*) as cnt FROM vuln_reports', fetchone=True)
        malware = execute(
            'SELECT COUNT(*) as cnt FROM malware_scans WHERE status = %s',
            ('MALICIOUS',),
            fetchone=True,
        )
        fraud_detected = execute(
            'SELECT COUNT(*) as cnt FROM malware_scans WHERE fraud_detected = TRUE',
            fetchone=True,
        )

    return jsonify({
        'total_scans': scans['cnt'] if scans and 'cnt' in scans else 0,
        'malware_detected': malware['cnt'] if malware and 'cnt' in malware else 0,
        'vulnerability_reports': vuln_reports['cnt'] if vuln_reports and 'cnt' in vuln_reports else 0,
        'fraud_detected': fraud_detected['cnt'] if fraud_detected and 'cnt' in fraud_detected else 0,
    })
